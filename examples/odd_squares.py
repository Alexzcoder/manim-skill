"""Demo for the manim skill: why 1 + 3 + 5 + ... = n squared.

    cp ../skills/manim/narrated.py .
    manim -pql odd_squares.py OddSquares            # captions only
"""
from narrated import *

COLORS = [BLUE_C, TEAL_C, YELLOW_C, "#F0892A", "#E5484D"]
S = 0.55


class OddSquares(Narrated):
    def construct(self):
        self.header("Why odd numbers add up to squares")
        corner = LEFT * 5 + DOWN * 1.4

        def layer(n):   # the L-shaped strip that turns an n x n square into (n+1) x (n+1)
            return VGroup(*[Square(S, fill_color=COLORS[n], fill_opacity=0.9, stroke_color="#0E1116", stroke_width=2)
                            .move_to(corner + RIGHT * i * S + UP * j * S)
                            for i in range(n + 1) for j in range(n + 1) if max(i, j) == n])

        layers = [layer(n) for n in range(5)]
        sums = ["1 = 1²", "1 + 3 = 2²", "1 + 3 + 5 = 3²", "1 + 3 + 5 + 7 = 4²", "1 + 3 + 5 + 7 + 9 = 5²"]
        eqs = VGroup(*[label(t, 34, COLORS[i]) for i, t in enumerate(sums)])
        eqs.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(RIGHT * 2.6 + UP * 0.4)

        def grow(n, run_time=1.2):
            self.play(LaggedStart(*[FadeIn(c, scale=0.4) for c in layers[n]], lag_ratio=0.15),
                      FadeIn(eqs[n], shift=UP * 0.2), run_time=run_time)

        with self.say("Start with one square. One is one times one."):
            grow(0)
        with self.say("Wrap it with three more, and you get a two by two square. "
                      "Wrap that with five more, and it is three by three."):
            grow(1)
            self.wait(1.5)
            grow(2)
        with self.say("Every new layer is the next odd number, and every layer completes the next square."):
            grow(3)
            grow(4)
        rule = label("1 + 3 + 5 + … + (2n − 1) = n²", 44, YELLOW).move_to(DOWN * 2.2)
        with self.say("So the first n odd numbers always add up to n squared."):
            self.play(Write(rule), run_time=2)
            self.play(Indicate(rule, color=WHITE))
