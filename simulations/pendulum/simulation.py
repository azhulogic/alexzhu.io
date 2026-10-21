"""Fixed-step integration and telemetry. Independent of the GUI."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .controller import Controller
from .dynamics import derivatives
from .models import Parameters, Rates, State


@dataclass(frozen=True)
class Sample:
    time: float
    theta: float
    omega: float
    target: float
    torque: float


class Simulation:
    def __init__(
        self,
        initial: State = State(),
        params: Parameters = Parameters(),
        controller: Controller | None = None,
        target: float = 0.0,
        model: Callable[[float, State, float, Parameters], Rates] = derivatives,
    ) -> None:
        self.initial = initial
        self.params = params
        self.controller = controller if controller is not None else Controller()
        self.target = target
        self.model = model
        self.reset()

    def reset(self) -> None:
        self.state = self.initial
        self.time = 0.0
        self.torque = 0.0
        self.controller.reset()
        self.history = [self.sample()]

    def sample(self) -> Sample:
        return Sample(self.time, self.state.theta, self.state.omega, self.target, self.torque)

    def step(self, dt: float) -> Sample:
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("Time step must be finite and positive.")
        command = float(self.controller.compute(self.time, self.state, self.target, dt, self.params))
        if not math.isfinite(command):
            raise ValueError("Controller returned a non-finite torque.")
        torque = max(-self.params.torque_limit, min(self.params.torque_limit, command))
        rates = self.model(self.time, self.state, torque, self.params)
        # Explicit Euler is just the default integrator; replace it if desired.
        next_state = State(
            theta=self.state.theta + dt * rates.theta_dot,
            omega=self.state.omega + dt * rates.omega_dot,
        )
        if not all(math.isfinite(value) for value in (next_state.theta, next_state.omega)):
            raise ValueError("Dynamics produced a non-finite state.")
        self.state = next_state
        self.time += dt
        self.torque = torque
        sample = self.sample()
        self.history.append(sample)
        return sample

    def export_csv(self, path: str | Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(["time_s", "theta_rad", "omega_rad_s", "target_rad", "torque_Nm"])
            for sample in self.history:
                writer.writerow([sample.time, sample.theta, sample.omega, sample.target, sample.torque])
