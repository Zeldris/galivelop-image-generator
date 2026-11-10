import math
import unittest

from gimg import matte

BG = (0, 160, 0)
FG = (200, 40, 40)


def disc(size=40, radius=14.0, hole=0.0, bg=BG, fg=FG, soft=True):
    """A disc (with a hole of radius `hole` showing the background color) on a flat background; soft edge."""
    px = bytearray()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - c, y - c)
            cov = max(0.0, min(1.0, radius + 0.5 - r)) if soft else float(r <= radius)
            if hole and r <= hole:
                cov = 0.0
            px += bytes(int(round(cov * f + (1 - cov) * b)) for f, b in zip(fg, bg)) + b"\xff"
    return size, size, px


def at(px, size, x, y):
    i = (y * size + x) * 4
    return tuple(px[i:i + 4])


class RemoveBgTests(unittest.TestCase):
    def test_disc_on_green_keeps_the_disc_and_clears_the_background(self):
        w, h, px = disc()
        out = matte.remove_bg(w, h, px)
        self.assertEqual(len(out), len(px))
        self.assertEqual(at(out, w, 0, 0)[3], 0)
        self.assertEqual(at(out, w, 20, 3)[3], 0)
        self.assertEqual(at(out, w, 20, 20), FG + (255,))
        self.assertEqual(at(px, w, 0, 0), BG + (255,), "the input must not be touched")

    def test_border_color_is_the_median_of_the_border(self):
        w, h, px = disc(bg=(10, 20, 30))
        self.assertEqual(matte.border_color(w, h, px), (10, 20, 30))

    def test_inside_color_equal_to_the_background_is_kept(self):
        w, h, px = disc(size=60, radius=26, hole=10)
        self.assertEqual(at(px, w, 30, 30)[:3], BG)
        out = matte.remove_bg(w, h, px)
        self.assertEqual(at(out, w, 30, 30), BG + (255,))  # same color as the background, not connected to the border
        self.assertEqual(at(out, w, 30, 8), FG + (255,))
        self.assertEqual(at(out, w, 1, 1)[3], 0)

    def test_edge_has_no_halo_of_the_background_color(self):
        w, h, px = disc(size=60, radius=22)
        out = matte.remove_bg(w, h, px, t0=20, t1=200)
        edge = [p for p in (at(out, w, x, y) for y in range(h) for x in range(w)) if 64 <= p[3] < 255]
        self.assertGreater(len(edge), 10)
        for p in edge:  # despill: the color of a partly transparent pixel is the disc's, not a mix with green
            self.assertLess(math.dist(p[:3], FG), 45, p)

    def test_grow_reaches_the_soft_edge_and_zero_does_not(self):
        w, h, px = disc(size=60, radius=22)
        with_grow = matte.remove_bg(w, h, px, t0=20, t1=200, grow=3)
        without = matte.remove_bg(w, h, px, t0=20, t1=200, grow=0)
        soft = lambda o: sum(1 for k in range(w * h) if 0 < o[k * 4 + 3] < 255)
        self.assertGreater(soft(with_grow), soft(without))

    def test_edge_cases(self):
        out = matte.remove_bg(1, 1, bytearray([9, 9, 9, 255]))
        self.assertEqual(tuple(out), (9, 9, 9, 0))  # one pixel: it is the border, so it is background
        flat = bytearray(bytes(BG + (255,)) * 100)
        self.assertEqual(set(matte.remove_bg(10, 10, flat)[3::4]), {0})  # all background
        noisy = bytearray()
        for k in range(100):  # all different from the border median: nothing is connected, all stays
            noisy += bytes(BG + (255,)) if k % 10 in (0, 9) or k < 10 or k >= 90 else bytes((255, 255, 255, 255))
        out = matte.remove_bg(10, 10, noisy, border=1)
        self.assertEqual(at(out, 10, 5, 5)[3], 255)

    def test_input_alpha_under_128_is_background(self):
        w, h, px = disc(size=30, radius=8)
        for k in range(w * h):  # the larger part of a 3 px frame is transparent with a garbage color
            x, y = k % w, k // w
            if min(x, y, w - 1 - x, h - 1 - y) < 3 and x < 22:
                px[k * 4:k * 4 + 4] = bytes((250, 0, 250, 0))
        self.assertEqual(matte.border_color(w, h, px, border=3), BG)  # not the garbage color
        out = matte.remove_bg(w, h, px, border=3)
        self.assertEqual(at(out, w, 0, 0)[3], 0)
        self.assertEqual(at(out, w, 15, 15), FG + (255,))
        self.assertEqual(at(out, w, 5, 5)[3], 0)

    def test_bad_arguments_say_why(self):
        px = bytearray(4 * 4)
        with self.assertRaisesRegex(ValueError, "t0 and t1 must satisfy"):
            matte.remove_bg(2, 2, px, t0=50, t1=50)
        with self.assertRaisesRegex(ValueError, "do not fit a 3x3"):
            matte.remove_bg(3, 3, px)
        with self.assertRaisesRegex(ValueError, "border must be at least 1"):
            matte.remove_bg(2, 2, px, border=0)


if __name__ == "__main__":
    unittest.main()
