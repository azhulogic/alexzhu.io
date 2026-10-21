"""Tkinter view and controls. Physics and control live in their own files."""

import math
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .controller import Controller
from .models import Parameters, State
from .simulation import Simulation


class PendulumApp:
    DT = 1 / 240

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Pendulum sandbox")
        self.root.geometry("980x720")
        self.root.minsize(760, 600)
        self.running = False
        self.accumulator = 0.0
        self.last_clock = time.perf_counter()
        self.after_id: str | None = None
        self.sim = Simulation()
        self.fields: dict[str, tk.StringVar] = {}

        shell = ttk.Frame(root, padding=20)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(1, weight=1)
        ttk.Label(shell, text="Inverted pendulum", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(shell, text="Local Python sandbox", foreground="#666").grid(row=0, column=1, sticky="e")

        self.canvas = tk.Canvas(shell, background="#fafafa", highlightthickness=1, highlightbackground="#ddd", height=360)
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(18, 12), padx=(0, 20))
        controls = ttk.Frame(shell, width=220)
        controls.grid(row=1, column=1, sticky="n", pady=(18, 12))
        entries = [
            ("Initial angle (deg)", "theta", math.degrees(0.16)),
            ("Initial speed (deg/s)", "omega", 0),
            ("Target angle (deg)", "target", 0),
            ("Length (m)", "length", 1.8),
            ("Mass (kg)", "mass", 0.2),
            ("Gravity (m/s²)", "gravity", 9.81),
            ("Damping", "damping", 0.05),
            ("Torque limit (N m)", "limit", 10),
            ("Kp", "kp", 0), ("Ki", "ki", 0), ("Kd", "kd", 0),
        ]
        for row, (label, key, value) in enumerate(entries):
            ttk.Label(controls, text=label).grid(row=row, column=0, sticky="w", pady=3)
            variable = tk.StringVar(value=f"{value:.4g}")
            self.fields[key] = variable
            ttk.Entry(controls, textvariable=variable, width=10).grid(row=row, column=1, sticky="e", padx=(12, 0))
        ttk.Label(controls, text="Settings apply on Reset.", foreground="#666").grid(row=len(entries), column=0, columnspan=2, sticky="w", pady=(10, 0))

        toolbar = ttk.Frame(shell)
        toolbar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.play_button = ttk.Button(toolbar, text="Start", command=self.toggle)
        self.play_button.pack(side="left")
        ttk.Button(toolbar, text="Step", command=self.single_step).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Reset", command=self.reset).pack(side="left")
        ttk.Button(toolbar, text="Export CSV…", command=self.export).pack(side="right")
        self.telemetry = tk.StringVar()
        ttk.Label(shell, textvariable=self.telemetry, font=("Consolas", 10)).grid(row=3, column=0, columnspan=2, sticky="w", pady=12)
        self.trace = tk.Canvas(shell, background="#fafafa", height=140, highlightthickness=1, highlightbackground="#ddd")
        self.trace.grid(row=4, column=0, columnspan=2, sticky="ew")
        ttk.Label(shell, text="Angle (solid) / target (dashed) · last 10 simulated seconds", foreground="#666").grid(row=5, column=0, columnspan=2, sticky="w", pady=(5, 10))
        ttk.Label(shell, text="Add your equations in dynamics.py and controller.py. Placeholders hold the state fixed.", wraplength=850, foreground="#666").grid(row=6, column=0, columnspan=2, sticky="w")

        self.root.bind("<space>", self.keyboard_toggle)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas.bind("<Configure>", lambda _event: self.draw())
        self.trace.bind("<Configure>", lambda _event: self.draw_trace())
        self.draw()
        self.tick()

    def keyboard_toggle(self, _event: tk.Event) -> str | None:
        if isinstance(self.root.focus_get(), (tk.Entry, ttk.Entry)):
            return None
        self.toggle()
        return "break"

    def toggle(self) -> None:
        self.running = not self.running
        self.last_clock = time.perf_counter()
        self.play_button.configure(text="Pause" if self.running else "Resume")

    def reset(self) -> None:
        try:
            values = {key: float(variable.get()) for key, variable in self.fields.items()}
            if not all(math.isfinite(value) for value in values.values()):
                raise ValueError("All settings must be finite numbers.")
            if any(values[key] <= 0 for key in ("length", "mass", "limit")):
                raise ValueError("Length, mass, and torque limit must be positive.")
            if values["damping"] < 0 or values["gravity"] < 0:
                raise ValueError("Gravity and damping must be nonnegative.")
            self.sim = Simulation(
                initial=State(math.radians(values["theta"]), math.radians(values["omega"])),
                params=Parameters(values["length"], values["mass"], values["gravity"], values["damping"], values["limit"]),
                controller=Controller(kp=values["kp"], ki=values["ki"], kd=values["kd"]),
                target=math.radians(values["target"]),
            )
        except ValueError as error:
            messagebox.showerror("Invalid settings", str(error), parent=self.root)
            return
        self.running = False
        self.accumulator = 0.0
        self.last_clock = time.perf_counter()
        self.play_button.configure(text="Start")
        self.draw()

    def advance(self) -> bool:
        try:
            self.sim.step(self.DT)
            return True
        except Exception as error:
            self.running = False
            self.accumulator = 0.0
            self.play_button.configure(text="Resume")
            messagebox.showerror("Simulation stopped", f"{type(error).__name__}: {error}", parent=self.root)
            return False

    def single_step(self) -> None:
        self.running = False
        self.play_button.configure(text="Resume")
        self.accumulator = 0.0
        self.advance()
        self.draw()

    def tick(self) -> None:
        now = time.perf_counter()
        elapsed = min(now - self.last_clock, 0.1)
        self.last_clock = now
        if self.running:
            self.accumulator += elapsed
            while self.accumulator >= self.DT:
                if not self.advance():
                    break
                self.accumulator -= self.DT
            self.draw()
        self.after_id = self.root.after(16, self.tick)

    def draw(self) -> None:
        width, height = max(self.canvas.winfo_width(), 100), max(self.canvas.winfo_height(), 100)
        self.canvas.delete("all")
        x, y = width / 2, height / 2
        radius = min(width / 2 - 35, height / 2 - 35)
        bob_x = x + radius * math.sin(self.sim.state.theta)
        bob_y = y - radius * math.cos(self.sim.state.theta)
        target_x = x + radius * math.sin(self.sim.target)
        target_y = y - radius * math.cos(self.sim.target)
        self.canvas.create_line(24, y, width - 24, y, fill="#ddd")
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="#eee", dash=(3, 5))
        self.canvas.create_line(x, y, target_x, target_y, fill="#a6b4b8", width=2, dash=(5, 5))
        self.canvas.create_line(x, y, bob_x, bob_y, width=6, fill="#222", capstyle="round")
        self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#222", outline="")
        self.canvas.create_oval(bob_x - 12, bob_y - 12, bob_x + 12, bob_y + 12, fill="#365b65", outline="")
        self.canvas.create_text(14, 14, anchor="nw", text="0° upright · clockwise positive", fill="#777")
        self.canvas.create_text(14, height - 14, anchor="sw", text=f"Length: {self.sim.params.length:g} m (drawing scaled to fit)", fill="#777")
        self.telemetry.set(f"t {self.sim.time:7.2f} s    θ {math.degrees(self.sim.state.theta):8.2f}°    ω {math.degrees(self.sim.state.omega):8.2f}°/s    u {self.sim.torque:7.3f} N m")
        self.draw_trace()

    def draw_trace(self) -> None:
        self.trace.delete("all")
        width, height = max(self.trace.winfo_width(), 100), max(self.trace.winfo_height(), 100)
        start = max(0.0, self.sim.time - 10)
        samples = [sample for sample in self.sim.history[-2401:] if sample.time >= start]
        span = max(10.0, self.sim.time - start)
        extent = max(20, abs(math.degrees(self.sim.target)) * 1.2,
                     max((abs(math.degrees(sample.theta)) * 1.2 for sample in samples), default=20))
        def point(t: float, theta: float) -> tuple[float, float]:
            return 12 + (t - start) / span * (width - 24), height / 2 - math.degrees(theta) / extent * (height / 2 - 20)
        self.trace.create_line(12, height / 2, width - 12, height / 2, fill="#e4e4e4")
        target_y = point(start, self.sim.target)[1]
        self.trace.create_line(12, target_y, width - 12, target_y, fill="#a6b4b8", dash=(5, 4))
        coordinates = [coordinate for sample in samples for coordinate in point(sample.time, sample.theta)]
        if len(coordinates) >= 4:
            self.trace.create_line(*coordinates, fill="#365b65", width=2)
        self.trace.create_text(12, 8, anchor="nw", text=f"±{extent:.0f}°", fill="#777")

    def export(self) -> None:
        path = filedialog.asksaveasfilename(parent=self.root, defaultextension=".csv", filetypes=[("CSV", "*.csv")], initialfile="pendulum.csv")
        if path:
            try:
                self.sim.export_csv(path)
            except OSError as error:
                messagebox.showerror("Export failed", str(error), parent=self.root)

    def close(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    PendulumApp(root)
    root.mainloop()
