# Pendulum sandbox

A local Python framework for writing your own inverted pendulum dynamics and
controller. Python 3.10+ and Tkinter are the only requirements. No pip packages.

## Run

From the repository root on this Windows machine:

```powershell
.\simulations\pendulum\run.cmd
```

The launcher uses the Python launcher if installed, otherwise Codex's available
Python runtime, then a regular Python installation. It avoids the Windows Store
Python alias. You can also run this directly with your chosen Python interpreter:

```sh
python -m simulations.pendulum
```

## Your math

- **`dynamics.py` → `derivatives(...)`:** return `Rates(theta_dot=..., omega_dot=...)`.
  This is where you choose the model and write the equations of motion.
- **`controller.py` → `Controller.compute(...)`:** return actuator torque.
  The gain inputs and controller memory are ready for your implementation.
- **`models.py`:** state, derivative, and parameter definitions with units.
- **`simulation.py` → `Simulation.step(...)`:** explicit Euler integration by
  default. Replace the integration method here if you prefer something else.
- **`app.py`:** drawing, inputs, animation timing, and CSV export.

Both math hooks deliberately return zero. Start initially advances simulation
time while the pendulum stays still. No gravity equation or PID law is supplied.
Restart the app after editing Python code.

## Conventions

- Angle is in radians internally, measured from upright, positive clockwise.
- Angular velocity is radians/second. Simulation time and `dt` are seconds.
- Controller output is torque in N m, positive clockwise. This is a fixed-pivot,
  torque-actuated scaffold, matching the existing pendulum demo's geometry.
- Length, mass, and gravity use SI units. Define damping in your model.
- The engine limits commanded torque using `torque_limit` after the controller.
- The UI displays degrees and degrees/second; exported CSV values use radians.
- The drawing scales to fit the window; screen pixels are not physical units.

## Controls

Start/Pause (or Space), single Step (1/240 s), Reset, and Export CSV. Parameters,
initial state, target, and gain edits apply when you click Reset. Reset clears
controller memory, time, and recorded history. Export writes the full history
since the last reset; the chart displays the last 10 simulated seconds.

The simulation uses fixed time steps independently of redraw timing. Long GUI
stalls are capped rather than causing a large, unstable integration step.
Non-finite outputs or exceptions stop the simulation and show the error.

This local tool is independent of the Astro website. CSV output can help you
compare your Python experiments with a future browser implementation.

## Verify the framework

```sh
python -m unittest simulations.pendulum.test_framework
```

These tests exercise integration plumbing, reset, output limits, CSV export, and
the GUI. They do not specify the physics or controller equations you will write.
