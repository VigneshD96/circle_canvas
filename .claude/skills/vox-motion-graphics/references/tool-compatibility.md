# Tool Compatibility and Setup

Read for installation/readiness checks and before the first tool-dependent
production stage. Resolve the connected toolset at runtime. Tool names below
describe the interface verified while preparing this package; a future schema
is authoritative. Do not install or invoke a legacy route merely to match a name.

## Setup without generation

1. Confirm `SKILL.md`, both visual references and the other referenced documents
   are present and readable. Preserve these relative paths when installing.
2. Discover available Higgsfield tools and inspect their descriptions/schemas.
   Distinguish an image/video model from a speech engine and an editing runtime.
3. Use a read-only account/balance check when authorized. A successful balance
   response proves account access for that call, not a successful generation.
4. Inspect model constraints and the available assembly environment. For a local
   Higgsedit route, check its actual installed help/capabilities; do not assume the
   remote sandbox has the same build. For a local media route, inspect installed
   utilities rather than promising an executable that is absent.
5. Report readiness per stage: discovered, authenticated where testable, available
   to execute, or missing. Say explicitly that no media was generated in setup.

Do not open a voice picker just to check whether speech tools exist. During an
actual speech request, the current picker may need an exclusive tool turn and
the user's selected voice pair before generation can continue.

If a Skill archive is supplied, inspect its entries before unpacking; keep paths
inside its destination. When updating an existing installation, preserve a backup
and unrelated user configuration. The package's folder name is
`vox-motion-graphics`; its entire `references/` directory travels with it.

## Current routes

Connected names may have a prefix such as `mcp__codex_apps__higgsfield_`.
Discover the actual callable name rather than composing one blindly.

| Stage | Tool or runtime | Important distinction |
|---|---|---|
| Account | `balance` | Read-only, no media produced |
| Model discovery | `models_search`, `models_get` | Inspect durations, reference roles, dimensions and audio controls |
| Cost | `estimate_image_cost`, `estimate_video_cost` | Exact request parameters; read-only |
| Style image | `generate_image` | Paid submission when authorized; retain actual output |
| Scene footage | `generate_video`, `generate_video_batch` | Single vs indexed batch lifecycle |
| Narration | `list_voices`, `generate_audio`, `generate_audio_batch` | Speech, not music/SFX |
| Batch completion | `jobs_wait` | Up to eight jobs; current maximum wait is 15 seconds |
| Batch display | `show_generation_by_ids` | Display the exact completed batch as required by its schema |
| User attachment input | `media_upload_and_confirm` | Attachment-only helper, not an arbitrary local-file reader |
| Other supported byte upload | `media_upload`, successful PUT, `media_confirm` | Confirm only after bytes upload successfully |
| Hosted work | `sandbox_exec` | Remote environment, cannot read a desktop path |
| Assembly | Documented native Higgsedit or an available authorized local editor/CLI | Actual files and export required |

Historical routes such as `resolve_explainer_preset`, `explainer_video`,
`job_status` and `models_explore` may be absent. Replace an absent route with a
verified current capability, preserving the intended workflow. Do not invent
job responses, IDs, galleries, hosted editor links or DEV access. A generic
workflow resolver that documents website work is not a video assembly service.

## Parameters and costs

For current Higgsfield generators, arguments belong in a single `params` object.
Read the live schema before submitting. Discover the model, then verify that it
supports the requested duration, aspect ratio, resolution and reference type.
Examples of canonical reference roles are `image`, `start_image`, `end_image`,
`video`, `audio` and `ref_element`; use only the selected model's supported subset.
Do not substitute old `image_references` fields for the current schema.

Use current estimates for the actual image/video parameters and the documented
audio cost-only route when needed. Do not reuse old fixed credit prices or claim
that resolving/generating a reference is free. State material cost uncertainty.
Proceed within the user's existing budget and production authorization; do not
add a generic second approval gate. A returned `unlim_choice` is a separate tool
choice and means no job was submitted: obtain that choice as required, then reuse
the same request with the selected option.

For speech, use the exact `voice_id` and `voice_type` pair from the user/picker.
The present `generate_audio` route defaults to `seed_audio`, accepts spoken text,
and supports `get_cost:true` for a cost-only check. Inspect the actual engine
before using tuning fields. A name such as Holden alone is not a voice ID.

## Async jobs

Record returned job IDs immediately. A submission acknowledgement is not a
finished file. For batches, keep caller indices mapped to scenes, wait on the
returned IDs and inspect every terminal status. `all_terminal` can include failed
jobs. Display completed batch results according to the tool contract.

Single-generation tools may already create a live result widget; do not repeatedly
open duplicate displays to poll it. Use supported waiting/status behavior, honor
poll intervals and inspect the output when complete. On a transport timeout,
resolve whether the original request submitted before making another paid call.

## Files and runtime boundaries

Keep a local input local unless there is a supported, authorized upload route.
Do not pass a Mac path to a cloud sandbox or an attachment-only helper. Preserve
confirmed media IDs separately from local paths and temporary URLs.

In an ephemeral hosted run, keep inputs recoverable and finish the render and
successful output upload before the lease expires. Reserve output upload slots
when needed, PUT the actual generated bytes and confirm only successful uploads.
A file that exists only in an expired sandbox is not a delivered asset.

Use connected tools for their documented purpose. Music/SFX may come from native
generated sound when supported, authorized existing assets, or a separately
available sound tool. If none exists, identify this stage as unavailable; speech
synthesis cannot replace it. Do not spend credits merely to test readiness.
