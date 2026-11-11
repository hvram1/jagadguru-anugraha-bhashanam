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
| [`shankara-quotes-not-found.html`](shankara-quotes-not-found.html) | for scholars: the verses the Jagadguru attributes to Śaṅkara Bhagavatpāda that we could not place, each with the recording at the moment, his own words around it, and the question — not linked from the door; hand the link to whoever can help |

Five files. No build step, no framework, no data files: each page carries its
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
audio-ingest/SHANKARA-NOT-FOUND.html ->  shankara-quotes-not-found.html
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

Then it reads the counts back out of the published HTML and compares every
place each one is stated — recitations named and the verses they are of,
recitations not named and the passages those are of, the recurring passages,
the dhyāna-ślokas. Rebuild two pages and forget the third and the site
contradicts itself in public, with no broken link and no error to show for it.
That is not hypothetical: the note had sat at 283 recitations since August
while the quotes page had moved to 240 entries, and nothing said so until these
two were published side by side.

Agreeing is not the same as meaning the same thing. The first pages shown at
Sringeri said 661, 73 and 264 about the unnamed chant — rows with Tamil in
them, the recurring passages only, and every passage — and each number passed
this check. So the patterns carry the unit's words: every page now states both
halves of the result as *recitations of verses* and *recitations of passages*.

The same numbers are then written into `index.html`, which is why its tallies
carry `data-n="named"` rather than a typed figure. A number on the door that
disagrees with the page behind it is the same failure, one click earlier.

## On a phone

All four pages are laid out for a phone and were measured at 390 × 844 by
driving them, not by reading the CSS: no horizontal overflow in any state of
any control, the sticky bars kept under a fifth of the screen, and tap targets
sized by `(hover:none)` rather than by width, so a tablet gets them too.

## Every check, in one command

```
here$   ./check_all.py            # the Mac gate: cases, site, pages
here$   ./check_all.py --site     # what GitHub Actions runs on every push
```

It stops at the first failure and exits with that check's own status, so
`2` still means *the snapshot moved and nobody has accepted it*. A missing
sibling repository fails; it is never skipped. The three checks:

| check | what it runs | needs |
|---|---|---|
| cases | `audio-ingest/scripts/quotes_cases.py`: 73 cases and the snapshot | audio-ingest's `build/`, which is not in git: Mac only |
| site | `./refresh.py --check`: links resolve, counts agree | this repo |
| pages | `purana-atlas/atlas_regress.py --repo .`: every control pressed at phone width | purana-atlas beside this repo, and Chrome (`$CHROME`, an installed Chrome, or a downloaded Chrome for Testing) |

To run it before every push, once per clone:

```
here$   git config core.hooksPath .githooks
```

Not enabled yet, on purpose: the gate is red until the snapshot of
2 November is read and accepted, and a hook that always blocks gets bypassed.
This site has no harness baseline yet either, so controls that do nothing
(the preview has 3) are listed but do not fail; take one with
`atlas_regress.py --repo ../jagadguru-anugraha-bhashanam --update` once those
three are understood.

### On a real phone (not built yet)

The gate prints `phone  SKIPPED`, and `--phone` fails, until this exists. The
plan, agreed 2026-11-11:

- **The phone runs the harness's own script.** The harness injects a script
  into a copy of each page, and that script presses the controls and measures.
  In phone mode the harness's server listens on the Mac's Tailscale address,
  port 8000 (already allowed), and the script POSTs its report back instead of
  writing it into the page for headless Chrome to read.
- **One start page** walks the phone through every page and then the
  deep-link addresses, so one tap runs the whole site.
- **At the phone's real width**: skip the 390 px iframe the Mac uses, because
  headless Chrome will not make a narrow window.
- **What it adds**: Android Chrome's real viewport and address bar, the player
  bootstrap on a real phone, and how One UI's fonts render Devanāgarī, Tamil
  and Kannada. **What it does not**: real touch; controls are pressed with
  `click()`.
- **Nothing on the phone but Tailscale and a browser.** Keep the screen on
  for the run (Android pauses scripts when it locks); it runs in real time.
- **Both browsers**: Chrome, and Samsung Internet, the default on the
  Galaxy M47, which many readers will use.
- **adb, later, only to automate it**: `brew install --cask
  android-platform-tools`; on the phone, Developer options → Wireless
  debugging, and Auto Blocker off (Settings → Security and privacy), which
  otherwise blocks adb silently. Then `am start -d <url>` per browser
  (`com.android.chrome`, `com.sec.android.app.sbrowser`) and `screencap` for
  a picture of each page. If wireless debugging refuses the Tailscale
  address, `adb tcpip 5555` once over USB.
- **Driving the phone's Chrome over adb with real taps** (DevTools forwarded
  to the Mac) is the next step after that, only if click() proves not enough.

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
