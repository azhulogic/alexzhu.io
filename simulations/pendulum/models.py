from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    """theta: radians from upright, clockwise positive. omega: radians/second."""

    theta: float = 0.16
    omega: float = 0.0


@dataclass(frozen=True)
class Rates:
    """Time derivatives: radians/second and radians/second squared."""

    theta_dot: float = 0.0
    omega_dot: float = 0.0


@dataclass(frozen=True)
class Parameters:
    """SI units. Define how mass/length/damping enter your model in dynamics.py."""

    length: float = 1.8
    mass: float = 0.2
    gravity: float = 9.81
    damping: float = 0.05
    torque_limit: float = 10.0
