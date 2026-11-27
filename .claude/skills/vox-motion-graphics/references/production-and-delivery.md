# Production, Assembly and Delivery

Read once a plan is approved or the user has authorized autonomous production.
Use an existing project structure where possible. A useful standalone structure is:

```text
research.md
narration-draft.md
scene-plan.md
style-direction.md
assets/                 approved style sheet, subjects, source footage and audio
prompts/                actual requests tied to scene/version
versions/               original scenes and revised variants
edit/                   native project or reproducible assembly instructions
exports/                checked outputs and requested comparisons
manifest.json           paths/IDs, provenance, selected versions and measurements
```

Create only files relevant to the requested stage. Do not populate empty folders
and call the project complete. The manifest should record real assets and results.

## Plan exact timing

Choose the target duration and frame rate from the brief or existing timeline.
Represent important boundaries in frames to avoid rounding drift. For the
tutorial, 30 seconds at 25 fps is 750 frames; each ten-second scene is 250 frames.
For arbitrary lengths, allocate the final block's remainder explicitly rather
than silently changing the total to a multiple of ten seconds.

Check actual source lengths and supported generation durations. If a source is
longer, select a natural-speed range that contains the approved action. If shorter,
do not slow it just to fill the slot. Use an intentional hold only where the
explanation and approved timing allow it, or obtain suitable source footage.

Write the narration against visual beats. Generate or use the chosen take, measure
its duration and locate meaningful words against actions. Preserve a locked voice
take during visual revisions. If fresh narration overruns, shorten the wording
within the brief or rerecord at an appropriate pace; do not silently accelerate it.

## Inspect sources before assembly

For every selected clip check opening, key action and ending, plus normal-speed
playback. Verify subject identity, causal order and direction. Inspect title-free
areas if generated footage must remain clean. Probe dimensions, fps, duration and
audio streams. Record any upscale or conversion required for final delivery.

Do not change the requested aspect ratio to match an accidental wrong output.
Use a considered crop only if it preserves the approved composition; otherwise
correct the source. Preserve originals when stripping unwanted generated audio.

## Assemble with an available editor

Prefer the connected documented editor for editable text and graphics. If the
installed Higgsfield video-editing Skill is available and applies, follow its
current runtime instructions. It is a capability route, not a file bundled here.

For native Higgsedit, inspect the installed CLI help/types before version-specific
use. The documented building blocks are:

- `project({dir, size, fps, background})` to create/open a project.
- `p.add(file)` to import a real asset.
- `p.cut(handle, {from, dur, at, fit})` to place a source range: `from` is source
  seconds and `at` is timeline seconds.
- `p.compose(nodes, {at, dur, name, camera})` for editable graphics.
- `p.frame(...)`, `p.read()` and `p.render(...)` to inspect and export.

Construct code against the current installed definitions, not this abbreviated
list alone. A whole-script build may replace a timeline; inspect an existing
human-edited project and use bounded changes instead. Back up before editing.

If the native editor is unavailable, a documented local editor or an installed
media CLI can assemble authorized local files. Preserve the edit decisions and
text/audio layers in an editable project or reproducible assembly script. A flat
MP4 should not be described as an editable timeline. Report any genuine capability
gap rather than fabricating a hosted project.

## Typography and handoffs

Use real fonts and exact approved words. Apply consistent headline, explanation
and annotation styles, allowing for close/wide compositions. Keep text away from
the moving focal subject, and test readability at the intended viewing size.

Review the last frame of each shot beside the first of the next. Check object
position, screen direction and where the eye lands. Then play the join normally
with the actual narration; a frame comparison alone cannot establish a good cut.
Use enough footage on both sides to understand the transition. Avoid unnecessary
cutaways, jumpy zooms or abrupt holds that break the causal explanation.

For a clean/assembled comparison, use identical source timing and scale. Export
real layers, not an imitation of how the edit might look. Add speech captions
only when requested and time them to the actual spoken track.

## Export and review

Use the requested dimensions and frame rate. A practical review format is H.264
MP4 with stereo AAC; retain a higher-quality master or separate WAV tracks if the
brief calls for them. Preserve native source quality and state when a 4K delivery
is an upscale. Do not invent resolution that the tool did not produce.

After export, check the file itself:

1. Duration/frame count and scene boundaries match the plan.
2. All media is present; no black gaps, corrupt frames or frozen action masquerading
   as animation. Intended holds are deliberate and documented.
3. Titles are correct, legible and consistent through movement.
4. Narration is complete, intelligible and aligned; sound does not obscure words.
5. Joins and the ending work at normal playback speed.

For a revision, compare unaffected ranges or their edit decisions against the
original. Keep original and selected versions separately named. For a full video,
deliver one finished checked MP4 with supporting script, source links and relevant
project files; do not stop at generation results. Provide requested comparisons
and stems as additional deliverables.
