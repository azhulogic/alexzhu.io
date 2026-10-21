import csv
import math
import tempfile
import unittest
from pathlib import Path

from .controller import Controller
from .models import Parameters, Rates, State
from .simulation import Simulation


class FrameworkTests(unittest.TestCase):
    def test_initial_placeholders_hold_state(self):
        sim = Simulation()
        for _ in range(240):
            sim.step(1 / 240)
        self.assertEqual(sim.state, sim.initial)
        self.assertAlmostEqual(sim.time, 1)
        self.assertEqual(sim.torque, 0)

    def test_custom_derivatives_flow_through_integrator(self):
        calls = []

        def model(t, state, torque, params):
            calls.append((t, state, torque, params))
            return Rates(theta_dot=2, omega_dot=-3)

        sim = Simulation(initial=State(theta=0, omega=0), model=model)
        sim.step(0.25)
        self.assertEqual(sim.state, State(theta=0.5, omega=-0.75))
        self.assertEqual(calls[0][0], 0)
        self.assertEqual(sim.history[-1].time, 0.25)

    def test_reset_clears_history_time_and_controller_memory(self):
        sim = Simulation()
        sim.step(0.1)
        sim.controller.integral = 42
        sim.controller.previous_error = 1
        sim.reset()
        self.assertEqual(sim.time, 0)
        self.assertEqual(sim.state, sim.initial)
        self.assertEqual(len(sim.history), 1)
        self.assertEqual(sim.controller.integral, 0)
        self.assertIsNone(sim.controller.previous_error)

    def test_limits_and_nonfinite_values(self):
        class FixedCommand(Controller):
            command = 100

            def compute(self, *args):
                return self.command

        controller = FixedCommand()
        sim = Simulation(controller=controller, params=Parameters(torque_limit=2))
        self.assertEqual(sim.step(0.01).torque, 2)
        controller.command = -100
        self.assertEqual(sim.step(0.01).torque, -2)
        controller.command = math.nan
        with self.assertRaisesRegex(ValueError, "non-finite torque"):
            sim.step(0.01)
        sim.model = lambda *args: Rates(theta_dot=math.inf)
        controller.command = 0
        with self.assertRaisesRegex(ValueError, "non-finite state"):
            sim.step(0.01)
        for dt in (0, -1, math.nan):
            with self.assertRaises(ValueError):
                sim.step(dt)

    def test_export_includes_initial_and_recorded_states(self):
        sim = Simulation()
        sim.step(0.01)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.csv"
            sim.export_csv(path)
            with path.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 2)
        self.assertEqual(float(rows[1]["time_s"]), 0.01)
        self.assertEqual(float(rows[1]["theta_rad"]), sim.initial.theta)


class GuiSmokeTests(unittest.TestCase):
    def test_controls_render_step_reset_and_close(self):
        import tkinter as tk
        from .app import PendulumApp

        root = tk.Tk()
        root.withdraw()
        app = PendulumApp(root)
        try:
            root.update_idletasks()
            app.draw()
            self.assertGreater(len(app.canvas.find_all()), 0)
            self.assertGreater(len(app.trace.find_all()), 0)
            app.single_step()
            self.assertAlmostEqual(app.sim.time, app.DT)
            app.fields["theta"].set("15")
            app.fields["kp"].set("3")
            app.reset()
            self.assertAlmostEqual(math.degrees(app.sim.state.theta), 15)
            self.assertEqual(app.sim.controller.kp, 3)
            self.assertEqual(app.sim.time, 0)
            app.toggle()
            self.assertTrue(app.running)
            app.toggle()
            self.assertFalse(app.running)
        finally:
            app.close()


if __name__ == "__main__":
    unittest.main()
