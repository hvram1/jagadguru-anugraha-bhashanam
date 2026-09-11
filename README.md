# Jagadguru Anugraha Bhāṣaṇam

Forty-one recorded discourses of the Jagadgurus of Sringeri, with every
Sanskrit verse chanted in them placed on the clock of the recording.

**<https://hvram1.github.io/jagadguru-anugraha-bhashanam/>**

| Page | What it is |
|---|---|
| [`index.html`](index.html) | the door — what this is, and the two pages it opens |
| [`what-the-jagadgurus-quote.html`](what-the-jagadgurus-quote.html) | ask it for a verse, a chapter or a work; every answer is a timestamp that opens the recording at the chant |
| [`chanted-and-not-named.html`](chanted-and-not-named.html) | the passages the index could not name — the list of what is worth digitizing next |
| [`the-note.html`](the-note.html) | the whole measurement read end to end, talk by talk — not linked from the door; it is reached from *the full note* in the quotes page, which is the only place it is wanted |

Four files. No build step, no framework, no data files: each page carries its
own data inline. Between them they make two off-site requests —
`fonts.googleapis.com` for Noto Sans Devanagari, and `youtube.com` when a
timestamp is followed.

## This repository is a deployment

Nothing here is authored by hand except `index.html` and this README. The three
pages are built in [`audio-ingest`](../audio-ingest), which is where their
inputs live — the transcripts, the forced alignments, the citation keys — and
copied in by `./refresh.py`:

```
audio-ingest/AB-VL-QUOTES-V2.html    ->  what-the-jagadgurus-quote.html
audio-ingest/AB-VL-UNNAMED.html      ->  chanted-and-not-named.html
audio-ingest/AB-VL-QUOTES-NOTE.html  ->  the-note.html
```

So the loop is: rebuild there, refresh here, commit here.

```
audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_v2.py
audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_unnamed.py
audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_note.py
here$           ./refresh.py
here$           git commit -am "refresh" && git push
```

`./refresh.py --check` verifies what is already here and copies nothing.

## What refresh.py checks, and why

It renames the files on the way in, so it repoints the cross-page links and
then resolves **every** internal link against the files on disk. A rewrite that
misses is a 404 that only a visitor finds.

Then it reads the counts back out of the published HTML and compares the ones
that overlap — the quotes page says `240 recitations named` and the note says
`shown as 240 entries`; both should be the same measurement. Rebuild two pages
and forget the third and the site contradicts itself in public, with no broken
link and no error to show for it. That is not hypothetical: the note had sat at
283 recitations since August while the quotes page had moved to 240 entries,
and nothing said so until these two were published side by side.

The same numbers are then written into `index.html`, which is why its tallies
carry `data-n="named"` rather than a typed figure. A number on the door that
disagrees with the page behind it is the same failure, one click earlier.

## On a phone

All four pages are laid out for a phone and were measured at 390 × 844 by
driving them, not by reading the CSS: no horizontal overflow in any state of
any control, the sticky bars kept under a fifth of the screen, and tap targets
sized by `(hover:none)` rather than by width, so a tablet gets them too.

## What this is not

A working measurement made from recordings published on the Sringeri maṭha's
public YouTube channel. It is not a publication of the maṭha, and no citation
in it carries a scholar's attestation. Where a citation is wrong, the recording
is the authority and the page is not.

## The neighbours

Companion to the [Purāṇa Atlas](https://hvram1.github.io/purana-atlas/), which
does the same for recorded upanyāsams of the Purāṇas — where there is an
edition to align against, and so a verse-by-verse atlas rather than an index of
quotations.
