#!/usr/bin/env python3
"""Copies the shared kit (assets/kit) into program sites and checks the copies.

  python tools/sync_kit.py --to <pages root> [<pages root> ...]
  python tools/sync_kit.py --check <pages root> [<pages root> ...]

<pages root> is the folder that is published as the site root of a repository
(the repository root, or docs/ or website/); the kit lives in <pages root>/assets/kit/.
--check exits with 1 and lists every file that differs, is missing or is left over.
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / 'assets' / 'kit'
KIT_FILES = ('kit.css', 'kit-theme.js', 'kit.js', 'programs.js', 'KIT_VERSION')
OPTIONAL_FILES = ('demo.html',)  # lives only in the profile's own copy; never copied, never a leftover


def kit_dir(site):
    return pathlib.Path(site) / 'assets' / 'kit'


def copy_kit(source, site):
    target = kit_dir(site)
    target.mkdir(parents=True, exist_ok=True)
    for name in KIT_FILES:
        (target / name).write_bytes((source / name).read_bytes())
    return target


def problems(source, site):
    """Lines describing how the kit copy in <site> differs from the source."""
    target = kit_dir(site)
    found = []
    if not target.is_dir():
        return ['%s: no assets/kit folder' % site]
    for name in KIT_FILES:
        copy = target / name
        if not copy.is_file():
            found.append('%s: missing' % copy)
        elif copy.read_bytes() != (source / name).read_bytes():
            found.append('%s: differs from the source' % copy)
    for extra in sorted(p for p in target.iterdir() if p.name not in KIT_FILES + OPTIONAL_FILES):
        found.append('%s: not part of the kit' % extra)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--to', nargs='+', metavar='PAGES_ROOT', help='copy the kit into these site roots')
    mode.add_argument('--check', nargs='+', metavar='PAGES_ROOT', help='verify the copies are byte-identical')
    parser.add_argument('--source', type=pathlib.Path, default=DEFAULT_SOURCE, help='kit source folder (default: assets/kit)')
    args = parser.parse_args(argv)
    missing = [n for n in KIT_FILES if not (args.source / n).is_file()]
    if missing:
        print('Kit source incomplete (%s): %s' % (args.source, ', '.join(missing)))
        return 1
    if args.to:
        for site in args.to:
            print('kit copied: %s' % copy_kit(args.source, site))
        return 0
    found = [line for site in args.check for line in problems(args.source, site)]
    if found:
        print('\n'.join(found))
        print('Kit copies out of date. Fix: python tools/sync_kit.py --to <pages root>')
        return 1
    print('Kit copies match the source: %d site(s).' % len(args.check))
    return 0


if __name__ == '__main__':
    sys.exit(main())
