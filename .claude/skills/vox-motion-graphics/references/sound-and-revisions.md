# Sound, Timing Revisions and Comparisons

Read when recording narration, finishing sound or revising an existing scene.
Honor stage-specific requests: a silent preview can stay silent even though a
later full deliverable includes sound.

## Narration and stems

Reuse a supplied or approved voice take. For new speech, use the exact chosen
voice pair and the approved words. Measure the real audio and align meaningful
phrases with visible action. A fixed-duration take is successful when it fits the
window and sounds natural, not when its word count matches an estimate.

Retain separate narration, music and SFX sources. Keep an audio edit map with
source start, timeline position and gain. Build a narration-only export and the
full mix from the same voice source and processing chain.

Music should support the pacing. Duck it under speech; restore it gently during
natural gaps when appropriate. Place effects on visible meaningful events, such
as the first brake or a diagram entrance. Do not add an effect at every cut or
use loudness to obscure an unclear visual.

Check clipping and speech intelligibility at normal playback volume. If the user
specifies delivery loudness, measure against that target. Otherwise choose a
sensible mix and report measured values only if actually measured.

Do not use a speech generator as a music/SFX engine. Use authorized supplied or
licensed audio, documented native generated audio, or a genuine available sound
tool. Report a missing sound source instead of claiming a completed sound pass.

When only a mixed file exists and the user requests voice-only, source separation
can provide an **extracted** narration track. Retain sample alignment and inspect
remaining music, missing consonants and other artifacts. A separated residual is
not an original studio music/SFX stem. Do not regenerate someone's approved speech
and describe it as extracted audio.

## Timing revision

1. Preserve the original scene, source ranges, narration and first full assembly.
2. Translate the note into an observable change: what will remain visible longer,
   when the viewer should notice it, and what stays fixed.
3. Inspect available time. Write a before/after timing map before rendering.
4. Change the smallest relevant section and keep unaffected scenes untouched.
5. Measure the result, compare it and review its two neighboring joins.

Example: add about one second to the initiating slowdown in a ten-second scene,
recover that second from the ending hold, and keep the reaction sequence at its
original speed. This budget is valid only if the real ending has enough removable
hold. Do not invent that spare second or compress the reaction to fit. If it is
absent, explain the actual timing conflict and propose a viable alternative.

An intentional edit hold should be described as such. Do not claim a new model
generation if the revision was made locally by editing the existing footage.

## Original / revised A/B

Use the actual original and revised files with the same framing and narration.
Label them `ORIGINAL` and `REVISED`.

- **Sequential viewing:** show the same scene interval in each version.
- **Whole-scene comparison:** start both at scene time zero, use one shared
  narration track and a common time counter; verify equal total duration.
- **Reaction-tempo comparison:** align the start of the chain reaction in each
  version, which may occur at different scene times. Play at original speed.
  This answers a different question from the whole-scene comparison.

Keep these alignments explicit. Do not speed one side, crop away the relevant
action or change audio to make the preferred version appear better. Mark the
selected version only after the user selects it or delegates that decision.

## Voiceover only / full mix A/B

Choose one short passage containing a complete thought and representative sound.
Export it twice with identical video source range, frame rate, scale and length:

1. `VOICEOVER ONLY`: only the narration source.
2. `FULL MIX`: that narration plus music and SFX from the selected mix.

Keep the voice source and its gain/processing identical. Do not independently
normalize the two comparison halves or use whole-mix processing that makes the
narration louder in one half. Check the selected excerpt after audio encoding.

For a combined comparison, play the voice-only passage, then restart the exact
same passage with the full mix. Put the labels in a quiet part of the frame.
In a tutorial edit, mute the host during this comparison. A requested short slot
may require a shorter complete phrase, not arbitrary truncation mid-word.

For the traffic tutorial's measured 5.2-second slot, a valid example is two
2.6-second passages. Those durations and the words must be verified against the
actual selected version; do not transplant timestamps from an unrelated render.

## Deliverable names

Use clear names such as `scene02_original`, `scene02_revised`, `full_selected`,
`voiceover_only`, `full_mix` and `comparison`. Include duration/format when useful.
Keep one source manifest so a future note can be applied to the actual chosen
version. Preserve separate source stems even if the user only requests the final
video today; they make later audio variants reliable.
