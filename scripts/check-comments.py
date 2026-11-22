import io
import sys
from pathlib import Path
import subprocess
import tokenize

from pygments import lex
from pygments.lexers import BashLexer, YamlLexer
from pygments.token import Comment


def comment_lines(source):
    return [number for number, line in enumerate(source.splitlines(), 1)
            if line.startswith('#')]


def source_comments(path, source):
    if path.endswith('.py'):
        return [token.start[0] for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type == tokenize.COMMENT
                and not (token.start[0] == 1 and token.string.startswith('#!'))]
    if path.endswith(('.sh', '.yml', '.yaml')):
        lines = []
        number = 1
        lexer = BashLexer() if path.endswith('.sh') else YamlLexer()
        for token, value in lex(source, lexer):
            if token in Comment and not (path.endswith('.sh') and number == 1 and value.startswith('#!')):
                lines.append(number)
            number += value.count('\n')
        return lines
    if path == '.gitignore':
        return comment_lines(source)
    return []


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        assert comment_lines('_internal/\n# stale\n') == [2]
        assert comment_lines('report#1.csv\n\\#archive\n') == []
        assert source_comments('code.py', '#!/usr/bin/env python3\nx = "https://host/#part"\n# old') == [3]
        assert source_comments('script.sh', '#!/bin/sh\nprintf "%s" "# literal"\n# old') == [3]
        assert source_comments('script.sh', 'echo ready;# old') == [1]
        assert source_comments('script.sh', 'cat <<EOF\n# literal data\nEOF\n# old') == [4]
        assert source_comments('workflow.yml', 'name: "# literal"\non: push # old') == [2]
        assert source_comments('workflow.yml', 'run: |\n  #!/bin/sh\n  echo ok\nname: x # old') == [4]
        print('Comment lint self-test passed')
    else:
        files = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
        failures = [f'{path}:{line}' for path in files if path and Path(path).is_file()
                    for line in source_comments(path, Path(path).read_text())]
        if failures:
            print('Comments forbidden:\n' + '\n'.join(failures), file=sys.stderr)
            sys.exit(1)
        print('Comment ratchet: zero comments in tracked Python, shell, YAML and Git configuration')
