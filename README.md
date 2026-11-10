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
| [`skills/manim/watch_render.sh`](skills/manim/watch_render.sh) | Live progress bar and time left for a running render |

## What the skill already knows

Things that are slow to discover and are written into the skill, so the agent does not relearn them:

- "It rendered" is not "it looks right". The agent tiles a frame every few seconds into contact sheets and reads them all before the final render.
- Thousands of small shapes make the render crawl. Merging them into a few shapes fixes it with no visible change.
- A caption that updates every frame stops Manim from reusing still frames. Captions switch between static waits.
- Narration never needs regenerating for a visual change: clips are numbered files, and the scene reads their length.

## Limits

- The agent cannot listen to audio. It checks that the voice is present, how loud it is and where the pauses are; pronunciation is yours to check.
- Caption timing is estimated where a clip has no pause near a phrase boundary.
- A ten-minute video takes roughly 10 to 15 minutes to render at 1080p60 on a laptop.
- Voice generation spends your ElevenLabs credits, roughly one per character.
- Tested with Manim Community 0.22 on Linux (WSL). The skill has been used end to end on one long video and the demo above.

## License

MIT. See [LICENSE](LICENSE).
