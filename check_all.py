#!/usr/bin/env python3
"""Every check this site has, in order, stopping at the first that fails.

    ./check_all.py            the Mac gate: run before ./refresh.py is committed
                              and before every push (.githooks/pre-push runs it)
    ./check_all.py --site     only what the site alone can show -- what GitHub
                              Actions runs (.github/workflows/check.yml)
    ./check_all.py --phone    the real-phone pass, which does not exist yet:
                              fails, so nobody mistakes it for having run

The checks, and where each one's inputs live:

  cases     audio-ingest/scripts/quotes_cases.py -- the 73 cases and the
            snapshot of every line's decision. Exit 1: a case failed. Exit 2:
            the snapshot moved and nobody has accepted it. Needs audio-ingest's
            build/reports, which are not in git, so it runs on the Mac only.
  site      ./refresh.py --check -- every internal link resolves, and every
            count agrees with itself across the pages and the door.
  pages     purana-atlas/atlas_regress.py --repo . -- every page loaded at phone
            width in headless Chrome, every control pressed (it must play,
            refuse or act), deep links, script errors, sideways scroll.
  phone     NOT BUILT. The same injected script, run by a real phone over
            Tailscale. See README, "On a real phone". Printed as SKIPPED here,
            never as a pass.

A missing sibling repository is a FAILURE, not a skip: a gate that skips what it
cannot find is a gate that passes. Exit status is the failing check's own (so
2 still means "snapshot not accepted"), or 0 when everything ran and held.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
AUDIO = os.path.join(UP, 'audio-ingest')
ATLAS = os.path.join(UP, 'purana-atlas')
SHARADA_PY = os.path.join(UP, 'sharadapeetham', 'myenv', 'bin', 'python')


def step(name, argv, cwd, needs):
    missing = [p for p in needs if not os.path.exists(p)]
    print('\n=== %s' % name, flush=True)
    if missing:
        print('FAIL  %s: cannot run, missing %s' % (name, ', '.join(missing)))
        return 1
    shown = [os.path.relpath(x, cwd) if os.path.isabs(x) and x.startswith(UP) else x
             for x in argv]
    print('$ (cd %s && %s)' % (os.path.relpath(cwd, UP), ' '.join(shown)), flush=True)
    # Output is passed through line by line. Under GitHub Actions each FAIL
    # line is also raised as an annotation: a job's log needs admin rights to
    # read through the API, its annotations do not, so the reason a run went
    # red can be read by anyone, not just found by opening the page.
    gha = os.environ.get('GITHUB_ACTIONS') == 'true'
    p = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        sys.stdout.write(line)
        if gha and line.lstrip().startswith('FAIL'):
            print('::error title=check_all %s::%s' % (name, line.strip()[:900]))
    rc = p.wait()
    sys.stdout.flush()
    print('%s  %s (exit %d)' % ('ok  ' if rc == 0 else 'FAIL', name, rc))
    if gha and rc:
        print('::error title=check_all::%s failed (exit %d)' % (name, rc))
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--site', action='store_true',
                    help='only the checks that need nothing but this repo and the harness')
    ap.add_argument('--phone', action='store_true',
                    help='the real-phone pass (not built yet: fails)')
    a = ap.parse_args()

    if a.phone:
        print('FAIL  phone: the real-phone pass is not built yet '
              '(README, "On a real phone")')
        return 3

    steps = []
    if not a.site:
        steps.append(('cases', [SHARADA_PY, 'scripts/quotes_cases.py'], AUDIO,
                      [AUDIO, SHARADA_PY]))
    steps.append(('site', [sys.executable, 'refresh.py', '--check'], HERE, []))
    harness = os.path.join(ATLAS, 'atlas_regress.py')
    steps.append(('pages', [sys.executable, harness, '--repo', HERE], ATLAS, [harness]))

    for name, argv, cwd, needs in steps:
        rc = step(name, argv, cwd, needs)
        if rc:
            print('\nstopped at %s. Nothing after it ran.' % name)
            return rc
    print('\n=== phone\nSKIPPED  phone: not built yet (README, "On a real phone")')
    print('\nevery check that exists ran, and held.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
