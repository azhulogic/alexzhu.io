from dataclasses import dataclass

from .models import Parameters, State


@dataclass
class Controller:
    kp: float = 0.0
    ki: float = 0.0
    kd: float = 0.0
    integral: float = 0.0
    previous_error: float | None = None

    def reset(self) -> None:
        self.integral = 0.0
        self.previous_error = None

    def compute(
        self, t: float, state: State, target: float, dt: float, params: Parameters
    ) -> float:
        """Return commanded torque (N m), clockwise positive.

        target is in radians, dt in seconds. self.kp/ki/kd come from the UI.
        self.integral and self.previous_error are memory for your implementation.

        TODO: Calculate error, update memory, and return your control law.
        The engine applies the torque limit after this method returns.
        """
        return 0.0
