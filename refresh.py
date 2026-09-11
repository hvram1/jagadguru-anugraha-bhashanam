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
of it: the index says `240 recitations named` and `661 heard, not yet named`,
and the note says `shown as 240 entries` and `A further 661 Sanskrit passages`.
Rebuild two of them and forget the third and the site contradicts itself in
public, with no broken link and no error to show for it. That is not
hypothetical -- the note in the repository next door had sat at 283/226/677
since August while the index had moved to 299/240/661, and nothing said so.
So the counts are read back out of the published HTML and compared, and a
disagreement stops the publish.

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

    Each entry is one quantity and the two places it is stated. They are read
    back out of the published HTML as the strings a reader sees, not parsed
    from some shared source: what is being checked is what the pages claim.
    """
    q = pages['what-the-jagadgurus-quote.html']
    u = pages['chanted-and-not-named.html']
    n = pages['the-note.html']
    return [
        # key          what              first reading                       second reading
        ('named', 'recitations named',
         ('quotes', q, r'<b class="num">([\d,]+)</b>recitations named'),
         ('note', n, r'shown as ([\d,]+) entries')),
        ('verses', 'distinct verses',
         ('quotes', q, r'<b class="num">([\d,]+)</b>distinct verses'),
         ('note', n, r'drawn from ([\d,]+) distinct verses')),
        ('hours', 'hours of audio',
         ('quotes', q, r'<b class="num">([\d.]+)</b>hours of discourse'),
         ('note', n, r'recitations named across ([\d.]+) hours')),
        ('unnamed', 'heard, not named',
         ('quotes', q, r'<b class="num">([\d,]+)</b>heard, not yet named'),
         ('note', n, r'A further ([\d,]+) Sanskrit passages')),
        ('talks', 'talks',
         ('quotes', q, r'<p class="dek">([\d,]+) recorded talks'),
         ('unnamed', u, r'across the ([\d,]+) talks')),
        # These two are stated once, on the page they belong to, so there is
        # nothing to compare them against -- they are read only so that
        # index.html does not have to have them typed into it.
        ('recurring', 'recurring passages',
         ('unnamed', u, r'<p class="dek">([\d,]+) Sanskrit passages'), None),
        ('passages', 'unnamed passages',
         ('unnamed', u, r'<b>([\d,]+)</b>unnamed passages in all'), None),
    ]


def check_agreement(pages):
    """The three pages are three views of one measurement. Make them say so."""
    for name in ('what-the-jagadgurus-quote.html', 'chanted-and-not-named.html',
                 'the-note.html'):
        if name not in pages:
            return fail('all three pages must be here to check that they agree')

    bad, values = 0, {}
    for key, what, first, second in claims(pages):
        a_name, a_html, a_re = first
        a = num(a_html, a_re, 'the ' + what, a_name)
        if a is None:
            bad += 1
            continue
        values[key] = a
        if second is None:
            print('  %-18s %8s   (%s, stated once)' % (what, a, a_name))
            continue
        b_name, b_html, b_re = second
        b = num(b_html, b_re, 'the ' + what, b_name)
        if b is None:
            bad += 1
        elif a != b:
            bad += fail('%s: the %s page says %s, the %s page says %s. One of '
                        'them was rebuilt and the other was not.'
                        % (what, a_name, a, b_name, b))
        else:
            print('  %-18s %8s   (%s and %s agree)' % (what, a, a_name, b_name))
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
