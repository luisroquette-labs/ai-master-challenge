import sys
from pathlib import Path


def comment_lines(source):
    return [number for number, line in enumerate(source.splitlines(), 1)
            if line.startswith('#')]


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        assert comment_lines('_internal/\n# stale\n') == [2]
        assert comment_lines('report#1.csv\n\\#archive\n') == []
        print('Comment lint self-test passed')
    else:
        failures = comment_lines(Path('.gitignore').read_text())
        if failures:
            print('Comments forbidden in .gitignore: ' + ', '.join(map(str, failures)), file=sys.stderr)
            sys.exit(1)
        print('Comment ratchet: zero comments in audited Git configuration')
