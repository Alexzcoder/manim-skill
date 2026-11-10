<h1 align="center">manim</h1>

<p align="center">
  <em>Hand your agent a topic. Get back a narrated explainer video.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-skill-111111?style=flat-square" alt="Claude Code skill">
  <img src="https://img.shields.io/badge/renders%20with-Manim%20CE-111111?style=flat-square" alt="Renders with Manim Community Edition">
  <img src="https://img.shields.io/badge/voice-ElevenLabs%20(optional)-111111?style=flat-square" alt="Voice: ElevenLabs, optional">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT license">
</p>

<p align="center">
  <img src="assets/demo.gif" width="720" alt="Demo: coloured L-shaped layers of squares build a 5 by 5 grid while the sums 1, 1+3, 1+3+5 appear beside it, with a caption line at the bottom">
</p>

<p align="center">
  <sub>The demo above is a <a href="examples/odd_squares.py">44-line scene</a>. Captions are generated from the narration text.</sub>
</p>

---

You have a document nobody will read and a team that would watch a ten-minute video. Making that video by hand means a script, an animation tool, a voice-over, subtitles, and a weekend.

`manim` is a skill for Claude Code that does the whole pipeline: it reads your sources, writes the scene in [Manim](https://www.manim.community/), checks its own layout, adds a voice and captions, renders 1080p, and puts the MP4 in your Downloads folder.

## What you type

```
/manim explain our Q3 capacity plan, sources are in ./docs
```

## What you get

- A 1080p MP4 in the 3Blue1Brown style: dark background, one idea per beat, smooth transforms.
- A voice-over, if you have the ElevenLabs connector. One clip per narration line, and each animation beat lasts exactly as long as its clip.
- Captions that appear phrase by phrase and switch on the real pauses in the audio.
- The scene file, so you can change a number and re-render without paying for the voice again.

No voice connector? You still get the video with timed captions.

## How it works

```
1. Read the sources        → outline: 8-14 sections, one message and one picture each
2. Write the scene         → one Narrated class, one method per section
3. Preview and review      → contact sheets of the whole video; fix overflow and overlaps
4. Narrate                 → dump the lines, generate one clip per line, download them
5. Render                  → 1080p60, then check duration, audio level and pauses
6. Deliver                 → copy to Downloads; optional faster cut
```

Three rules hold for every video:

- **No invented data.** Every number on screen traces to your sources. Anything illustrative or schematic is labelled as such on screen.
- **Show the subject, not only charts.** If the topic has real geometry (routes, maps, networks), the skill looks for the real data and animates that.
- **No LaTeX.** Text rendering only, so there is nothing extra to install.

## Install

Needs Python 3.10+, [`uv`](https://docs.astral.sh/uv/) and `ffmpeg` on your PATH. Manim itself is installed into a project venv by the skill.

### Claude Code plugin

```
/plugin marketplace add Alexzcoder/manim-skill
```
```
/plugin install manim@manim-skill
```

### Or copy the folder

```bash
git clone https://github.com/Alexzcoder/manim-skill
cp -r manim-skill/skills/manim ~/.claude/skills/manim
```

Then type `/manim <topic or source files>` in any project.

## Use the module without the skill

`narrated.py` is one file with no dependencies beyond Manim and ffmpeg. Copy it next to your scene:

```python
from narrated import *

class MyVideo(Narrated):
    def construct(self):
        self.header("Section title")
        with self.say("One narration line. The animations inside last as long as the line."):
            self.play(Write(label("hello", 48)))
        self.wipe()
```

```bash
manim -pql scene.py MyVideo                                  # captions only
NARRATION_DUMP=lines.json manim -ql --dry_run scene.py MyVideo   # list the narration lines
NARRATION_AUDIO_DIR=audio manim -pqh scene.py MyVideo        # with audio/01.mp3, 02.mp3, ...
```

Any text-to-speech tool works for the clips: one MP3 per line, numbered in order.

| File | What it does |
|---|---|
| [`skills/manim/SKILL.md`](skills/manim/SKILL.md) | The workflow the agent follows |
| [`skills/manim/narrated.py`](skills/manim/narrated.py) | `Narrated` scene class: `say()`, captions, audio sync |
| [`skills/manim/review.sh`](skills/manim/review.sh) | Contact sheets, duration and audio check for a rendered video |
| [`skills/manim/fetch_clips.sh`](skills/manim/fetch_clips.sh) | Downloads narration clips from signed URLs |
| [`skills/manim/speed.sh`](skills/manim/speed.sh) | Faster cut with pitch preserved |
| [`skills/manim/progress.sh`](skills/manim/progress.sh) | Review copy with a progress bar along the bottom edge |

## How this was built

The skill is a write-up of one long session, not a design exercise. The task was a ten-minute explainer for a university project, starting from a Manim draft that had never been rendered. What happened, in order:

1. **The draft rendered first time, and looked wrong.** No errors, but captions ran under axis labels, a legend ran off the frame, and coloured text bled into the next word. None of that shows up in a log. The fix was to stop trusting "it rendered" and look: tile a frame every six seconds into contact sheets and read them all. That became `review.sh`.
2. **Every number was checked against the source PDFs,** including the ones that only appear inside charts. Two examples in the draft turned out to be illustrative and were not labelled. They are now.
3. **Voice came from an ElevenLabs connector, not an API key.** 58 narration lines became 58 clips (about 8,750 characters). The scene reads each clip's length and stretches the beat to fit, so nothing is cut off and the longest silence in the final video is 1.7 seconds.
4. **Feedback after the first watch: "this is just lots of graphs."** Fair. The topic was a bus network, and the video never showed a bus. The data had real route geometry, so the next version draws all 234 lines as a map, with vehicles moving along them. Same narration, no new voice cost. That became the "show the subject" rule.
5. **Captions went from a block of text to one phrase at a time.** Each clip is scanned for pauses and phrase changes snap to them; 125 of 170 changes landed on a real pause.

### Things that cost time

- A dot for each of 2,210 buses made the render crawl. Merging them into about 36 shapes fixed it with no visible change.
- A caption that updates every frame stops Manim from reusing still frames, and a 13-minute render became much longer. Captions now switch by hand between static waits.
- Swapping a group's submobjects left stale captions stuck on screen. Keeping every phrase in the group and moving the unused ones off screen does not.
- `pkill -f "manim ..."` kills the shell that typed it.

All of these are in the skill's gotcha list, so the agent does not rediscover them.

## Limits

- The agent cannot listen to audio. It checks that the voice is present, how loud it is and where the pauses are; pronunciation is yours to check.
- Caption timing is estimated where a clip has no pause near a phrase boundary.
- A ten-minute video takes roughly 10 to 15 minutes to render at 1080p60 on a laptop.
- Voice generation spends your ElevenLabs credits, roughly one per character.
- Tested with Manim Community 0.22 on Linux (WSL). The skill has been used end to end on one long video and the demo above.

## License

MIT. See [LICENSE](LICENSE).
