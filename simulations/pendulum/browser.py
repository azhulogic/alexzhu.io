import math
from typing import Any


class Pendulum:
    def __init__(self) -> None:
        self.initial_angle = 0.16
        self.length = 1.8
        self.gravity = 9.81
        self.damping = 0.05
        self.time_scale = 1.25
        self.reset()

    def reset(self) -> None:
        self.theta = self.initial_angle
        self.omega = 0.0
        self.last_time: float | None = None

    def pause_clock(self) -> None:
        """Resume from the same state after a browser back/forward navigation."""
        self.last_time = None

    def acceleration(self) -> float:
        """Current demo dynamics. Replace or extend this with your model."""
        return (self.gravity / self.length) * math.sin(self.theta)

    def step(self, dt: float) -> None:
        """One integration step, preserving the original JavaScript demo."""
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("Time step must be finite and nonnegative.")
        self.omega += self.acceleration() * dt
        self.omega *= 1 - self.damping * dt
        self.theta += self.omega * dt

    def advance(self, now_ms: float) -> None:
        """Convert animation timestamps to capped, scaled simulation steps."""
        if self.last_time is None:
            self.last_time = now_ms
        dt = max(0.0, min((now_ms - self.last_time) / 1000, 0.033)) * self.time_scale
        self.last_time = now_ms
        self.step(dt)

    def draw(self, ctx: Any, width: float, height: float) -> None:
        """Draw through the browser's CanvasRenderingContext2D bridge."""
        length_pixels = self.length * 100
        pivot_x, pivot_y = width / 2, height - 70
        bob_x = pivot_x + length_pixels * math.sin(self.theta)
        bob_y = pivot_y - length_pixels * math.cos(self.theta)

        ctx.clearRect(0, 0, width, height)
        ctx.fillStyle = "#fafafa"
        ctx.fillRect(0, 0, width, height)

        ctx.strokeStyle = "#d9d9d9"
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(80, pivot_y)
        ctx.lineTo(width - 80, pivot_y)
        ctx.stroke()

        ctx.strokeStyle = "#111"
        ctx.lineWidth = 8
        ctx.lineCap = "round"
        ctx.beginPath()
        ctx.moveTo(pivot_x, pivot_y)
        ctx.lineTo(bob_x, bob_y)
        ctx.stroke()

        ctx.fillStyle = "#111"
        ctx.beginPath()
        ctx.arc(pivot_x, pivot_y, 8, 0, math.tau)
        ctx.fill()

        ctx.fillStyle = "#444"
        ctx.beginPath()
        ctx.arc(bob_x, bob_y, 16, 0, math.tau)
        ctx.fill()
