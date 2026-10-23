import math
import unittest
from unittest.mock import Mock

from .browser import Pendulum


class BrowserPendulumTests(unittest.TestCase):
    def test_matches_the_previous_javascript_step_sequence(self):
        theta, omega = 0.16, 0.0
        pendulum = Pendulum()
        for dt in (0, 0.016, 0.02, 0.01, 0.033) * 40:
            alpha = (9.81 / 1.8) * math.sin(theta)
            omega += alpha * dt
            omega *= 1 - 0.05 * dt
            theta += omega * dt
            pendulum.step(dt)
        self.assertAlmostEqual(pendulum.theta, theta)
        self.assertAlmostEqual(pendulum.omega, omega)

    def test_first_frame_reset_and_clock_pause(self):
        pendulum = Pendulum()
        pendulum.advance(1000)
        self.assertEqual(pendulum.theta, 0.16)
        pendulum.advance(1016)
        self.assertGreater(pendulum.theta, 0.16)
        before = pendulum.theta
        pendulum.pause_clock()
        pendulum.advance(90000)
        self.assertEqual(pendulum.theta, before)
        pendulum.reset()
        self.assertEqual(pendulum.theta, 0.16)
        self.assertEqual(pendulum.omega, 0)
        self.assertIsNone(pendulum.last_time)

    def test_long_frame_is_capped(self):
        actual, expected = Pendulum(), Pendulum()
        actual.advance(1000)
        actual.advance(5000)
        expected.step(0.033 * 1.25)
        self.assertEqual(actual.theta, expected.theta)
        self.assertEqual(actual.omega, expected.omega)

    def test_instances_keep_separate_states(self):
        first, second = Pendulum(), Pendulum()
        first.step(0.1)
        self.assertNotEqual(first.theta, second.theta)
        self.assertEqual(second.theta, 0.16)

    def test_canvas_geometry_matches_existing_demo(self):
        pendulum = Pendulum()
        context = Mock()
        pendulum.draw(context, 720, 420)
        context.clearRect.assert_called_once_with(0, 0, 720, 420)
        pivot, bob = context.arc.call_args_list
        self.assertEqual(pivot.args, (360, 350, 8, 0, math.tau))
        self.assertAlmostEqual(bob.args[0], 360 + 180 * math.sin(0.16))
        self.assertAlmostEqual(bob.args[1], 350 - 180 * math.cos(0.16))


if __name__ == "__main__":
    unittest.main()
