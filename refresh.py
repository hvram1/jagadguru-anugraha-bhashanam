#!/usr/bin/env python3
"""Publish the three bhāṣaṇam pages from audio-ingest into this repo.

This repository is a *deployment*, not a source tree. Nothing here is authored
by hand except index.html and README.md. The three pages are built next door
and copied in by this script:

    audio-ingest/AB-VL-QUOTES-V2.html    -> what-the-jagadgurus-quote.html
    audio-ingest/AB-VL-UNNAMED.html      -> chanted-and-not-named.html
    audio-ingest/AB-VL-QUOTES-NOTE.html  -> the-note.html

They come from audio-ingest because that is where their inputs live -- the
transcripts, the forced alignments, the citation keys -- and there is no
edition behind any of them, so nothing in the workbench is involved. The loop
is the same as the atlas's: rebuild there, refresh here, commit here.

    audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_v2.py
    audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_unnamed.py
    audio-ingest$   ../sharadapeetham/myenv/bin/python scripts/quotes_note.py
    here$           ./refresh.py
    here$           git commit -am "refresh" && git push

Each page is one self-contained file. Between them they make exactly two
off-site requests -- fonts.googleapis.com for Noto Sans Devanagari, and
youtube.com when a timestamp is followed -- and nothing else, so the site is
four files and works from any subdirectory, including a GitHub Pages project
site at https://<user>.github.io/<repo>/.

WHY THIS SCRIPT VERIFIES INSTEAD OF JUST COPYING
------------------------------------------------
Two things here can be wrong in a way that a copy would not notice.

The first is the renaming. `what-the-jagadgurus-quote.html` links to the note
twice, under the old file's name, so the copy rewrites those hrefs -- and a
rewrite that misses is a 404 that only a visitor finds. Every internal link in
every published page is resolved against the files on disk before the copy is
allowed to stand.

The second is staleness, and it is the one that matters. The three pages are
built by three scripts from one measurement, and they print overlapping counts
of it: recitations named, the verses they are of, recitations not named, and
the passages those are of -- each on two or three pages. Rebuild two of them
and forget the third and the site contradicts itself in public, with no broken
link and no error to show for it. That is not hypothetical -- the note in the
repository next door had sat at 283/226/677 since August while the index had
moved to 299/240/661, and nothing said so. So the counts are read back out of
the published HTML and compared, and a disagreement stops the publish.

Agreement is not enough on its own, and the maṭha found that out for us: the
pages once said 661, 73 and 264 about the unnamed chant, every one checked
and every one right, in three different units. So the patterns carry the
unit's words, and every page states the unnamed chant as recitations of
passages, as it states the named as recitations of verses.

    ./refresh.py          copy, rewrite the links, verify, report
    ./refresh.py --check  verify what is already here; copy nothing
"""

import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'audio-ingest'))

# source basename -> published name. The published names are what a visitor
# sees in the URL bar, so they are the titles of the pages rather than the
# build keys the pipeline knows them by.
PAGES = [
    ('AB-VL-QUOTES-V2.html', 'what-the-jagadgurus-quote.html'),
    ('AB-VL-UNNAMED.html', 'chanted-and-not-named.html'),
    ('AB-VL-QUOTES-NOTE.html', 'the-note.html'),
]
RENAME = {src: dst for src, dst in PAGES}


def fail(msg):
    print('  FAIL  %s' % msg)
    return 1


# ----------------------------------------------------------------- the copy

def rewrite(html):
    """Point the cross-page links at the published names.

    The pages link to each other by the file names they have in audio-ingest,
    which is right there and wrong here. Only the href is touched: the link
    TEXT is the author's prose and stays as written.
    """
    n = 0
    for old, new in RENAME.items():
        html, k = re.subn(r'(href=")%s' % re.escape(old), r'\1' + new, html)
        n += k
    return html, n


def copy():
    ok = True
    for src, dst in PAGES:
        s = os.path.join(SRC, src)
        if not os.path.exists(s):
            ok = not fail('%s is not in %s -- build it first' % (src, SRC))
            continue
        html = io.open(s, encoding='utf-8').read()
        html, n = rewrite(html)
        io.open(os.path.join(HERE, dst), 'w', encoding='utf-8').write(html)
        print('  %-30s <- %-24s %6.0f KB%s'
              % (dst, src, len(html.encode('utf-8')) / 1024.0,
                 '   %d link(s) renamed' % n if n else ''))
    return ok


# --------------------------------------------------------------- the checks

def num(html, pattern, what, where):
    """One number out of the published HTML, or a stated failure."""
    m = re.search(pattern, html)
    if not m:
        fail('%s: could not find %s -- the page\'s wording has changed, and '
             'this check is now measuring nothing' % (where, what))
        return None
    return m.group(1)


def read(dst):
    p = os.path.join(HERE, dst)
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else None


def check_document(dst, html):
    """A page a phone can lay out, and a browser can be sure of the encoding of.

    The note reached this repo as a bare <title><style><body> fragment, written
    for an Artifact host that supplies the rest. A fragment has no viewport
    meta, so a phone lays it out at 980px and shrinks it to fit -- the whole
    page legible only by pinching. Nothing about the file looks wrong.
    """
    bad = 0
    head = html[:4096].lower()
    for needle, what in (
            ('<!doctype html>', 'a doctype'),
            ('<meta charset="utf-8">', 'a charset'),
            ('name="viewport"', 'a viewport meta -- a phone will lay it out '
                                'at 980px without one'),
            ('<title>', 'a title')):
        if needle not in head:
            bad += fail('%s is missing %s' % (dst, what))
    return bad


def check_links(dst, html):
    """Every internal href resolves to a file that is here."""
    bad = 0
    for href in sorted(set(re.findall(r'href="([^"#:]+)(?:#[^"]*)?"', html))):
        if href.startswith(('http', 'mailto', '/', '\'')) or not href:
            continue
        if not os.path.exists(os.path.join(HERE, href)):
            bad += fail('%s links to %s, which is not in this repo' % (dst, href))
    return bad


def claims(pages):
    """Every number the three pages print that this repo relies on.

    Each entry is one quantity and every place it is stated. They are read
    back out of the published HTML as the strings a reader sees, not parsed
    from some shared source: what is being checked is what the pages claim.

    The unnamed figures are stated on all three pages, in one unit each:
    recitations (times chanted) and passages (what was chanted). They used to
    be stated in three different units -- rows on one page, recurring passages
    on another, all passages in a third tile -- and every one of them agreed
    with this script while the pages disagreed with each other in front of the
    maṭha. Comparing the number is only worth anything if the number means the
    same thing everywhere, so the patterns below carry the unit's words.
    """
    q = pages['what-the-jagadgurus-quote.html']
    u = pages['chanted-and-not-named.html']
    n = pages['the-note.html']
    return [
        # key          what                  readings
        ('named', 'recitations named', [
            ('quotes', q, r'<b class="num">([\d,]+)</b>recitations named'),
            ('quotes', q, r'A <i>recitation</i> is one time a verse was chanted: '
                          r'([\d,]+) recitations'),
            ('note', n, r'\*\*([\d,]+) recitations named across'),
            ('unnamed', u, r'which lists the ([\d,]+) recitations')]),
        ('verses', 'distinct verses', [
            ('quotes', q, r'<b class="num">([\d,]+)</b>distinct verses'),
            ('quotes', q, r'recitations of ([\d,]+) different verses'),
            ('note', n, r'drawn from ([\d,]+) distinct verses')]),
        ('hours', 'hours of audio', [
            ('quotes', q, r'<b class="num">([\d.]+)</b>hours of discourse'),
            ('note', n, r'recitations named across ([\d.]+) hours')]),
        ('dhyana', 'dhyāna-ślokas named', [
            ('quotes', q, r'so ([\d,]+) of these recitations are named'),
            ('unnamed', u, r'request: ([\d,]+) recitations'),
            ('note', n, r'([\d,]+) of them are dhyāna-ślokas')]),
        ('invocations', 'closing invocations', [
            ('quotes', q, r'heard at the end of ([\d,]+) talks'),
            ('quotes', q, r'पार्वतीपतये हर हर महादेव» closes ([\d,]+) of these'),
            ('unnamed', u, r'which closes ([\d,]+) of the talks'),
            ('note', n, r'heard at the end of ([\d,]+) talks')]),
        ('unnamed', 'recitations not named', [
            ('quotes', q, r'<b class="num">([\d,]+)</b>chanted, not yet named'),
            ('quotes', q, r'Another ([\d,]+) recitations'),
            ('unnamed', u, r'<b>([\d,]+)</b>recitations not yet named'),
            ('unnamed', u, r'chant, ([\d,]+) times'),
            ('note', n, r'A further ([\d,]+) recitations of Sanskrit chant')]),
        ('passages', 'passages not named', [
            ('unnamed', u, r'<b>([\d,]+)</b>distinct passages'),
            ('unnamed', u, r'<p class="dek">([\d,]+) Sanskrit passages'),
            ('quotes', q, r'recitations, of ([\d,]+)\s+passages'),
            ('note', n, r'of ([\d,]+) distinct\s+passages')]),
        ('recurring', 'recurring passages', [
            ('unnamed', u, r'<b>([\d,]+)</b>chanted in more than one talk'),
            ('unnamed', u, r'<b>([\d,]+)</b> recurring</button>'),
            ('quotes', q, r'<span class="n">([\d,]+) passages? heard in more '
                          r'than one talk')]),
        ('talks', 'talks', [
            ('quotes', q, r'<p class="dek">([\d,]+) recorded talks'),
            ('unnamed', u, r'across the ([\d,]+) talks')]),
    ]


def check_agreement(pages):
    """The three pages are three views of one measurement. Make them say so."""
    for name in ('what-the-jagadgurus-quote.html', 'chanted-and-not-named.html',
                 'the-note.html'):
        if name not in pages:
            return fail('all three pages must be here to check that they agree')

    bad, values = 0, {}
    for key, what, readings in claims(pages):
        got = []
        for where, html, pattern in readings:
            v = num(html, pattern, 'the ' + what, where)
            if v is None:
                bad += 1
            else:
                got.append((where, v))
        if not got:
            continue
        values[key] = got[0][1]
        if len({v for _, v in got}) > 1:
            bad += fail('%s: %s. One of them was rebuilt and the other was '
                        'not, or one is counting something else.'
                        % (what, ', '.join('the %s page says %s' % g
                                           for g in got)))
        else:
            print('  %-22s %8s   (%d readings, %s agree)'
                  % (what, got[0][1], len(got),
                     ' and '.join(sorted({w for w, _ in got}))))
    return bad, values


def fill_index(values):
    """Put the pages' own numbers into index.html.

    index.html is the one hand-written page here, and every number on it is
    already stated by a page it links to. Typed in, they are four numbers that
    are right on the day they are typed; each `data-n` says which measurement
    the number is, and the number itself comes from the page that made it.
    """
    p = os.path.join(HERE, 'index.html')
    if not os.path.exists(p):
        return fail('index.html is not here')
    html = io.open(p, encoding='utf-8').read()
    before, bad, seen = html, 0, {}
    for key, value in values.items():
        html, k = re.subn(r'(data-n="%s">)[^<]*' % key, r'\g<1>' + value, html)
        seen[key] = k
    for key in re.findall(r'data-n="([^"]+)"', html):
        if key not in values:
            bad += fail('index.html asks for `%s`, which no page states' % key)
    if bad:
        return bad
    if html != before:
        io.open(p, 'w', encoding='utf-8').write(html)
    print('  index.html          %s' % ', '.join(
        '%s\u00d7%d' % (k, n) for k, n in sorted(seen.items()) if n))
    return 0


def verify(fill):
    bad = 0
    pages = {}
    for _, dst in PAGES + [(None, 'index.html')]:
        html = read(dst)
        if html is None:
            bad += fail('%s has not been published here' % dst)
            continue
        pages[dst] = html
        bad += check_document(dst, html)
        bad += check_links(dst, html)
    agreed, values = check_agreement(pages)
    bad += agreed
    if fill and not agreed:
        bad += fill_index(values)
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true',
                    help='verify what is already here; copy nothing')
    args = ap.parse_args()

    if not args.check:
        print('copying from %s' % SRC)
        if not copy():
            print('\nnothing was published.')
            return 1
        print('')

    print('verifying what is in this repo')
    bad = verify(fill=not args.check)
    if bad:
        print('\n%d problem(s). Fix them before committing: what is on disk '
              'here is what the site will serve.' % bad)
        return 1
    print('\nthe three pages are here, they link to each other, and they '
          'agree about what was measured.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
