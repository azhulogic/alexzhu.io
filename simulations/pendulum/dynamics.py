"""YOUR PHYSICS GOES HERE.

Convention: theta = 0 points straight up; clockwise angle/torque are positive.
All inputs are SI units. The renderer uses length only for visual geometry.
Choose your physical assumptions (point mass, rigid rod, friction, etc.).
"""

from .models import Parameters, Rates, State


def derivatives(t: float, state: State, torque: float, params: Parameters) -> Rates:
    """Return the two state derivatives at this instant.

    Available inputs:
      t              simulation time (seconds)
      state.theta    angle from upright (radians)
      state.omega    angular velocity (radians/second)
      torque         actuator torque (N m), limited by params.torque_limit
      params         length, mass, gravity, damping, torque_limit

    TODO: Write your kinematics and equation of motion here.
    The placeholder intentionally holds the state fixed.
    """
    return Rates(theta_dot=0.0, omega_dot=0.0)
