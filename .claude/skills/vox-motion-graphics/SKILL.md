---
name: vox-motion-graphics
description: >
  Plan, produce and revise Vox-style editorial mixed-media or paper-diorama
  explainers with Higgsfield: research, narration, scene plans, a shared visual
  reference, animated footage, typography, voiceover, sound and a verified final
  video. Use for an explicitly requested Vox-style or paper-collage explainer,
  including setup, planning, individual production stages and revisions. Perform
  only the stage requested; a setup or script request does not start generation.
---

# Vox Motion Graphics

Turn a brief into one coherent visual explanation and, when requested, a finished
video. The agent develops the story and directs the work; Higgsfield provides
available generation tools. This package contains instructions and prompt
references, not a subscription, a model entitlement or a built-in rendering engine.

## Choose the requested scope

- **Install / setup:** keep this folder and its references together. Verify the
  discovered Skill, connected tools, account access and available assembly route.
  Use [tool compatibility](references/tool-compatibility.md). Do not generate media.
- **Research / script / plan:** deliver the requested documents and stop there.
- **Full video:** continue through planning, generation, voice, edit, sound and
  export within the user's authorization. Deliver the assembled result, not only
  loose clips. If a required stage is unavailable, identify it specifically and
  complete independent work that remains useful.
- **Revision:** inspect the existing project and change only the requested scope.
  Preserve original versions and any human edits.

An ordinary chat message is a valid brief. Use existing conversation answers;
do not require the user to fill in a form or repeat approvals. Ask only for an
unresolved choice that materially blocks the requested work. If the user asks to
see the proposal first, present the actual proposal and wait at that point.
Existing approval for that scope remains valid.

## Defaults and overrides

| Item | Starting default when unspecified |
|---|---|
| Length and layout | 60 seconds, 9:16, six approximately ten-second blocks |
| Look | Editorial mixed-media collage; paper-diorama is an alternative |
| Story | One why/how question, a causal mechanism and a clear answer |
| Narration | English, measured documentary delivery; follow the user's language/voice choice |
| Working edit | 25 fps; choose a different rate when the brief or existing timeline requires it |
| Typography | Editable editorial headlines, labels and annotations where useful |
| Speech subtitles | Follow the brief; editorial text does not automatically mean speech subtitles |
| Sound | A full narrated deliverable includes voice and an appropriate sound pass; a silent-stage request stays silent |

User choices override these defaults. The tutorial's **30-second, 16:9,
three-by-ten-second traffic film** is a worked example, not a restriction on other
topics. GPT-6 Astra is the model used in that tutorial; this Skill does not change
the active model or require an Ultra setting. Do not promise access to a named
model or an internal/DEV connector.

## 1. Research the explanation

Use the user's topic and angle. If topic selection was delegated, research and
choose a suitable visual why/how question. Otherwise resolve a missing topic
before starting unrelated production.

Verify the central mechanism and the names, dates and quantities used in the
script. Prefer primary sources, and cross-check consequential or disputed claims.
Save claim → source URL → relevance in `research.md`. Visual prompt examples
are not factual sources. A plausible-looking generated scene does not verify a
claim. Avoid adding arbitrary statistics simply to make the piece feel editorial.

## 2. Write the narration and scene plan

Develop the opening question, explain the mechanism and resolve the question.
One block should advance one idea. Use concrete, spoken language; write narration
separately from production notes. Read it at the intended pace, then measure the
actual take later. Word count is a planning estimate, not a duration measurement.

Save `narration-draft.md` and `scene-plan.md`. For each scene record:

- Its timeline window and narration line.
- Starting state, focal object, initiating action and reaction order.
- What the camera reveals, and when the viewer should understand the point.
- Exact editorial text to add during assembly.
- End state and the visual/audio handoff into the next scene.

For a user-requested approval stage, present these documents with a concrete
visual direction before production. Do not replace them with a promise that a
plan has been made. See the [traffic example](references/traffic-example.md) for
the tutorial's actual requests, including its revision and sound comparison.

## 3. Establish a shared visual reference

Inspect supplied references first. Preserve the chosen design. Read
[vox-prompts.md](references/vox-prompts.md) for mixed-media templates or
[diorama-doc.md](references/diorama-doc.md) for the paper-world alternative.

Prepare a style sheet that shows palette, background/material, subject treatment,
composition and typography. Render exact typography as editable/design text;
do not depend on generated lettering to establish readable words. Reuse the
approved sheet and recurring subject references across scenes.

Separate **fixed style** from **shot-specific action and camera**. A close-up and
a wide view can have different compositions while sharing the same car, colors
and texture. Record real asset paths or confirmed media identifiers and their
roles. Do not copy example job IDs or another account's assets.

## 4. Produce and inspect footage

Read [tool compatibility](references/tool-compatibility.md) before the first
tool-dependent stage. Resolve supported model parameters and costs from current
tools. Use the approved reference and aspect ratio explicitly on every request.
Keep readable text out of generated footage; add it in assembly.

Give a scene a clear action order. Make the initiating cause visible before the
reaction unless the approved reveal deliberately uses another order. Camera
movement must help the explanation. Avoid mandatory whips, impacts or constant
zooming unrelated to the content.

Generate a representative scene first when the user wants a preview; otherwise
batch independent approved scenes. Record scene → request → returned job →
actual file. Confirm completion and inspect the returned result before calling it
usable. Check object identity, action order, camera framing, text contamination,
duration, aspect ratio and any returned parameter adjustments.

Fix the smallest failing part. After two unsuccessful quality revisions of the
same scene, report the concrete remaining defect and offer a bounded alternative
instead of continuing an open-ended generation loop. Settle uncertain submission
outcomes before retrying. Do not disguise a refused request or switch engines to
evade a safety or rights refusal.

## 5. Record the narration and assemble

Read [production and delivery](references/production-and-delivery.md). Use one
chosen voice consistently. Preserve supplied narration when it is part of the
brief. When a voice picker requires a user choice, follow that tool's contract;
do not invent an ID. Measure the takes and place them deliberately on the timeline.

Assemble approved scenes at their planned positions, then add clean titles,
labels and graphics with a consistent hierarchy. Use an available documented
editor/CLI. Keep project data and media recoverable. A complete production request
includes the assembly stage; perform it once inputs are ready.

Review adjacent last/first frames and play the joins at normal speed with the
narration. Keep attention on the same object, direction or explanatory element
across a cut. A sequence of stills with zooms does not substitute for requested
animated action. Likewise, a simulated interface is not evidence that a real tool
completed a job.

## 6. Revise, compare and finish sound

Read [sound and revisions](references/sound-and-revisions.md) for timing changes,
original/revised comparisons, narration, music and effects. Before revising, keep
an unchanged original scene and first cut. Explain what changes, what stays fixed
and where any added time comes from.

Review actual files under matched comparison conditions. A narration-only/full-mix
comparison uses identical picture, start time and voice gain. Keep genuine voice,
music and SFX sources separate so these variants can be exported without later
source separation. If only a mixed source exists, label an extracted voice as
extracted and inspect its artifacts.

For a full sound deliverable, make narration intelligible, duck background music
as needed and place restrained effects on meaningful actions. Speech synthesis
is not a music or SFX tool. If the connected toolset lacks those sources, use
authorized existing audio or clearly identify what is still needed.

## 7. Verify and deliver

Open the exported file and check playback, timing, text, sound and joins. Verify
dimensions, frame rate and duration. Keep the requested format; do not hide a
wrong aspect ratio with arbitrary cropping or call an upscale native 4K.

Deliver the verified final MP4 plus the script, scene plan, sources, used reference
and requested variants. Include an editable project or reproducible assembly
files when the chosen workflow supports them. Use real local links or confirmed
remote outputs; a local project is not a hosted editor URL.

Distinguish installed files, loaded Skill, authenticated connection, submitted
job, completed media and verified export. Do not claim an end-to-end generation
test during setup, or imply that an unfinished sound stage is complete.
