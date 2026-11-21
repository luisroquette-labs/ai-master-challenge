import io
import subprocess
import sys
import tokenize
from pathlib import Path


SOURCE_EXTENSIONS = {'.c', '.cpp', '.css', '.go', '.h', '.html', '.java', '.js', '.jsx', '.mjs', '.php', '.rs', '.sql', '.swift', '.ts', '.tsx'}


def violations(path, source):
    if path.suffix == '.py':
        return [token.start[0] for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type == tokenize.COMMENT]
    if path.name == '.gitignore' or path.suffix in {'.sh', '.yml', '.yaml'}:
        return [number for number, line in enumerate(source.splitlines(), 1)
                if '#' in line and not (path.suffix == '.sh' and number == 1 and line.startswith('#!'))]
    if path.suffix in SOURCE_EXTENSIONS:
        return [0]
    return []


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        assert violations(Path('.gitignore'), '_internal/\n# stale\n') == [2]
        assert violations(Path('x.py'), 'url = "https://x"\n# stale\n') == [2]
        assert violations(Path('x.js'), 'const x = 1;') == [0]
        print('Comment lint self-test passed')
    else:
        files = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
        errors = []
        for name in filter(None, files):
            path = Path(name)
            if not path.is_file() or (path.name != '.gitignore' and path.suffix not in SOURCE_EXTENSIONS | {'.py', '.sh', '.yml', '.yaml'}):
                continue
            for line in violations(path, path.read_text()):
                detail = 'new source format needs a comment parser' if line == 0 else 'comment forbidden'
                errors.append(f'{name}:{line}: {detail}')
        if errors:
            print('\n'.join(errors), file=sys.stderr)
            sys.exit(1)
        print('Comment ratchet: zero comments in tracked source and config')
