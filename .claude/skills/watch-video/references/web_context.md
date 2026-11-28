# Web context — public videos only

Do this step only when `intake.json` says `visibility: public` and the identity is confirmed by the user or is certain (exact title in the filename/tags plus matching content). Private or "not sure": skip, and say so.

## Query rules

- Use identifiers only: show + season/episode, podcast name + guest + episode number, channel + video title, product + version.
- Never paste transcript text, quotes or private names into a query.
- 3–6 searches are usually enough; fetch only the best 2–4 pages.

## What to look for, by kind

- **Sitcom / TV episode**: episode title, air date, synopsis/recap, cast and character list (actor → character), recurring jokes or story arcs from earlier episodes that the episode depends on, famous quotes or scenes from the episode.
- **Podcast / interview**: show notes, chapter timestamps, guest bio and why they are notable, topics, clips or quotes that spread online (signals for "viral moments").
- **Tutorial / talk**: the official docs, repo, product version, the speaker's slides or blog post, errata.
- **Short clip**: creator, original source if it is a re-upload, the trend or meme it belongs to.

## Output: `<run_dir>/context/web_context.md`

```
# Web context (external — the video wins on conflicts)
Identity: <what it is> · confirmed by: user | filename+content
## Facts
- <fact> — <source URL>
## Cast / people
- <actor/person> → <character/role> — <source URL>
## Public reception / notable moments
- <moment, approximate time if known> — <source URL>
## Mismatches with this file
- e.g. the recap mentions a scene that is not in this cut (trimmed upload?)
```

Keep it short (under 400 words). Summarise; do not copy long passages.
