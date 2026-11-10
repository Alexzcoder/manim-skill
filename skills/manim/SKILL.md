---
name: manim
description: |
  Make a narrated explainer video with Manim (3Blue1Brown style): script it, animate it,
  add an ElevenLabs voice and phrase-by-phrase captions, check the layout, render 1080p,
  and deliver the MP4. Use when the user asks for an explainer/animated video, says
  "make a video about X", "manim video", "animate this", "turn this doc into a video",
  or types /manim <topic or source files>.
---

# manim: narrated explainer videos

Input: a topic, and usually source material (PDF, doc, repo, data). Output: a 1080p MP4 with
voice and captions in the user's Downloads folder, plus the scene file so it can be re-rendered.

Files next to this SKILL.md (below, `$SKILL` means this skill's folder: `~/.claude/skills/manim` for a
manual install, or the plugin's `skills/manim` folder):
- `narrated.py`: `Narrated` scene base class. `with self.say("line"):` syncs a beat to its
  narration clip and draws the captions. Copy it next to the scene file.
- `fetch_clips.sh`: downloads narration clips from signed URLs.
- `review.sh`: contact sheets + duration + audio check for a rendered video.
- `speed.sh`: speed-up (default 1.75x) with pitch preserved.
- `progress.sh`: review copy with a progress bar burned along the bottom edge.

## Rules that hold for every video

- **No invented data.** Every number on screen must trace to the user's sources. Verify them
  (read the PDFs' text *and* their charts). Anything illustrative, schematic or stylised is
  labelled so on screen.
- **Show the subject, not only charts.** If the topic has real geometry or objects (routes,
  maps, networks, machines), look for the real data (GTFS shapes, coordinates, the user's
  repo) and animate that. A video of bar charts alone is the failure mode.
- **No LaTeX.** Use `label()` / `Text` only. Never `MathTex`, `Tex`, `DecimalNumber`, or
  axis `include_numbers` (draw tick labels by hand with `label`).
- One idea per beat; one `say()` per beat; `self.wipe()` between sections.
- Keep scene content above y = -3.05; the caption line lives below that.
- Narration text spells numbers as words ("seventy seven"); on-screen text uses digits.

## Steps

1. **Understand the material.** Read the sources. Write the outline: 8-14 sections, each with
   its message and the picture that carries it. Target ~10 chars of narration per second;
   7-11 minutes is ~4,500-6,500 characters. Proceed without asking unless the topic is unclear.

2. **Set up** (project folder, once):
   ```bash
   uv venv -q --python 3.12 .venv && uv pip install -q --python .venv/bin/python manim
   cp $SKILL/narrated.py .
   ```
   Needs `ffmpeg` on PATH.

3. **Write the scene file**: one class deriving from `Narrated`, one `part_*` method per
   section, `construct` calls them with `self.wipe()` between. Put the hard-coded figures in
   one block at the top.

4. **Preview without voice and fix the layout.** Captions are timed by word count here.
   ```bash
   .venv/bin/manim -ql --disable_caching scene.py MyVideo
   $SKILL/review.sh media/videos/scene/480p15/MyVideo.mp4 <scratch>/sheets
   ```
   Read every contact sheet. Fix text off-frame, overlaps, labels under lines, anything in
   the caption band. Re-render and re-check the frames you fixed. To check one section fast,
   render a subclass whose `construct` calls only that `part_*`, with `-s` for the last frame.

5. **Narration** (spends the user's ElevenLabs credits, ~1 credit per character; say the
   total before generating if it is large, and never regenerate a clip that succeeded):
   - Dump the lines: `NARRATION_DUMP=narration.json .venv/bin/manim -ql --dry_run scene.py MyVideo`
   - ElevenLabs MCP: `creative_list_voices` to pick a clear narrator voice (don't ask),
     `creative_create_flow` once, then one `creative_generate_speech` per line with
     `generations_count: 1`, the same `flow_id` and `voice_id`, model `eleven_v4`.
   - `creative_get_flow_run_status` with up to 20 `session_ids` per call until
     `all_completed`. Match results to lines by their `prompt` text, not by order.
   - Download with the signed `content_url` (the signature is required):
     `$SKILL/fetch_clips.sh audio <<< "01 <url>"` (one `NN URL` per line).
     Every row must print `200` and a duration; the clip count must equal the line count.
   - No ElevenLabs connector: deliver the captions-only version and say so.
   - If narration lines change later, regenerate only the changed clips, keeping numbering.

6. **Final render and checks.**
   ```bash
   NARRATION_AUDIO_DIR=audio .venv/bin/manim -ql --disable_caching scene.py MyVideo   # preview
   NARRATION_AUDIO_DIR=audio .venv/bin/manim -qh --disable_caching scene.py MyVideo   # 1080p60, run in background
   $SKILL/review.sh media/videos/scene/1080p60/MyVideo.mp4 <scratch>/final
   ```
   Confirm: no errors in the log, duration in range, audio present (mean volume around
   -28 dB), no pause longer than ~2 s, spot-check frames. A 10-minute video takes roughly
   10-15 minutes to render at `-qh`.

7. **Deliver.** Copy the MP4 to the user's Downloads folder (on WSL:
   `/mnt/c/Users/<user>/Downloads/`) and verify the copy with `cmp`. If asked for a faster
   cut: `$SKILL/speed.sh in.mp4 out.mp4 1.75` and deliver both.
   If asked for a progress bar: `$SKILL/progress.sh in.mp4 out_progress.mp4`, as a separate
   copy; the clean file stays the one to share.
   Report: paths, duration, credits spent, what was checked, and what was not (you cannot
   listen to the audio, so pronunciation is unverified).

## Gotchas learned the hard way

- Thousands of small mobjects (e.g. a dot per bus) make Cairo crawl. Merge them into a few
  multi-subpath `VMobject`s with `append_points`; the picture is identical.
- Indexing a `Text` (`t[:6]`) counts glyphs without spaces. Count characters accordingly.
- Animations re-add their mobjects on top. Give markers and labels that must stay above
  recolouring lines a `set_z_index(2)`.
- Text over lines needs `.add_background_rectangle(color="#0E1116", opacity=0.75, buff=0.04)`.
- Never stop a render with `pkill -f "manim ..."` from a shell whose own command line
  contains that string; it kills the shell too.
- Each `-qh` render overwrites `media/videos/<file>/1080p60/<Scene>.mp4`. Copy a version you
  want to keep before rendering again.
- Real-map recipe: project lon/lat with `x = (lon - lon0) * cos(lat0)`, `y = lat - lat0`,
  build one polyline `VMobject` per route (downsample to ~70 points), then
  `scale_to_fit_height` and `move_to` the whole group. Moving vehicles are `Dot`s on
  `MoveAlongPath(dot, route, rate_func=linear)`.
