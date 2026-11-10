"""Narration plumbing for Manim explainer videos (copy next to your scene file).

    from narrated import *          # gives you manim, Narrated, label

    class MyVideo(Narrated):
        def construct(self):
            self.header("Section title")
            with self.say("One narration line. The animations inside last as long as the line."):
                self.play(Write(label("hello", 48)))
            self.wipe()

Modes (environment variables):
    (none)                      timed captions only, ~2.6 words per second
    NARRATION_AUDIO_DIR=audio   plays audio/01.mp3, 02.mp3, ... (one per say(), in order);
                                each beat lasts as long as its clip, captions follow the pauses
    NARRATION_DUMP=lines.json   with `manim --dry_run`: writes every say() line, in order
    NARRATION_CAPTIONS=0        hide captions

No LaTeX needed: use label()/Text, never MathTex/Tex/DecimalNumber/include_numbers.
"""
from manim import *
import bisect
import json
import os
import re
import subprocess
from contextlib import contextmanager

config.background_color = "#0E1116"

AUDIO_DIR = os.environ.get("NARRATION_AUDIO_DIR")
DUMP = os.environ.get("NARRATION_DUMP")
CAPTIONS = os.environ.get("NARRATION_CAPTIONS", "1") != "0"
WORDS_PER_SEC = 2.6
CLIP_GAP = 0.15          # silence after each clip, seconds
CAPTION_TOP = -3.05      # keep scene content above this y; captions live below it


def label(s, size=24, color=WHITE, **kw):
    return Text(s, font_size=size, color=color, **kw)


def phrases(text, max_len=58):
    """Split a narration line into caption-sized phrases, breaking at punctuation where possible."""
    out, buf = [], ""
    for part in re.findall(r"[^,.:;?!]+[,.:;?!]*\s*", text):
        if buf and (len(buf) >= 28 or len(buf) + len(part) > max_len):
            out.append(buf)
            buf = ""
        buf += part
    out.append(buf)
    final = []
    for ph in out:                       # still too long: split at word boundaries into even pieces
        words, n = ph.split(), -(-len(ph) // max_len)
        size = -(-len(words) // n)
        final += [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
    return [f.strip() for f in final if f.strip()]


def clip_pauses(path):
    """Midpoints of the short silences inside a clip (used to time caption changes)."""
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    a = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    b = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return [(x + y) / 2 for x, y in zip(a, b)]


def phrase_times(parts, duration, pauses=()):
    """When each phrase after the first appears: proportional to text length,
    snapped to the nearest real pause in the audio if one is within 0.7 s."""
    total, cum, out = sum(map(len, parts)), 0, []
    for ph in parts[:-1]:
        cum += len(ph)
        t = duration * cum / total
        near = min(pauses, key=lambda m: abs(m - t), default=None)
        if near is not None and abs(near - t) <= 0.7 and (not out or near > out[-1] + 0.4):
            t = near
        out.append(t)
    return out


def clip_seconds(path):
    import av
    with av.open(path) as f:
        return f.duration / 1e6


class _Tracker:
    def __init__(self, d):
        self.duration = d


class Narrated(Scene):
    def setup(self):
        super().setup()
        self.sub = None
        self.clip_no = 0
        self.lines = []

    @contextmanager
    def say(self, text):
        self.clip_no += 1
        if DUMP:
            self.lines.append(text)
            json.dump(self.lines, open(DUMP, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        est, speech, pauses = max(2.0, len(text.split()) / WORDS_PER_SEC), None, ()
        if AUDIO_DIR:
            clip = os.path.join(AUDIO_DIR, f"{self.clip_no:02d}.mp3")
            self.add_sound(clip)
            speech = clip_seconds(clip)
            est, pauses = speech + CLIP_GAP, clip_pauses(clip)
        if CAPTIONS:
            parts = phrases(text)
            times = phrase_times(parts, speech or est, pauses)
            caps = [Text(ph, font_size=26, color="#F5F5F5").to_edge(DOWN, buff=0.32)
                    .add_background_rectangle(color="#0E1116", opacity=0.7, buff=0.08).set_z_index(10)
                    for ph in parts]
            home, away = caps[0].get_center(), DOWN * 50
            for c in caps[1:]:
                c.move_to(away)
            # All phrases stay in one group and only the current one is on screen.
            # (Swapping submobjects instead leaves stale captions stuck on screen.)
            self.sub = VGroup(*caps)
            self.sub.t = 0.0

            def show(t):
                k = bisect.bisect_right(times, t)
                for i, c in enumerate(caps):
                    c.move_to(home if i == k else away)

            def switch(m, dt):
                m.t += dt
                show(m.t)
            self.sub.add_updater(switch)
            self.add(self.sub)
        start = self.renderer.time
        yield _Tracker(est)
        # Wait out the rest of the line. The updater is dropped first so these waits are
        # static frames (fast to render); captions are switched by hand between them.
        marks = [est]
        if self.sub is not None:
            self.sub.clear_updaters()
            marks = times + [est]
        now = self.renderer.time - start
        for t in marks:
            if self.sub is not None:
                show(now)
            if t - now > 1.5 / config.frame_rate:
                self.wait(t - now)
                now = t
        if self.sub is not None:
            self.remove(self.sub)
            self.sub = None

    def wipe(self, run_time=0.8):
        """Fade out everything on screen (call between sections, outside say())."""
        mobs = [m for m in self.mobjects if m is not self.sub and not isinstance(m, ValueTracker)]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def header(self, s):
        h = Text(s, font_size=22, color=GREY_B).to_corner(UL, buff=0.35)
        self.play(FadeIn(h), run_time=0.4)
        return h
