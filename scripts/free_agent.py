"""Generate a small, allowlisted set of source edits using the Gemini free tier.

No third-party Python packages, shell commands, or direct GitHub write access.
The agent may propose edits only under lab/, tests/, docs/. Pull requests are
created by a separate job after tests and patch validation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.select_task import ROOT, create_prompt, pending_task

DEFAULT_MODEL = 'gemini-3.8-flash'
MAX_FILES = 8
MAX_EDIT_BYTES = 90000
ALLOWED_ROOTS = {'lab', 'tests', 'docs'}
ALLOWED_SUFFIXES = {'.py', '.md'}


def safe_target(path: str, root: Path = ROOT) -> Path:
    if not isinstance(path, str) or not path or '\\' in path or '\x00' in path:
        raise ValueError('invalid file path')
    pure = Path(path)
    if pure.is_absolute() or len(pure.parts) < 2 or pure.parts[0] not in ALLOWED_ROOTS:
        raise ValueError('file outside allowlisted directories')
    if any(component in {'.', '..'} or component.startswith('.') for component in pure.parts):
        raise ValueError('hidden or parent path not allowed')
    if pure.suffix not in ALLOWED_SUFFIXES:
        raise ValueError('unapproved file extension')
    destination = root / pure
    if not destination.resolve().is_relative_to(root.resolve()):
        raise ValueError('target resolves outside repository')
    return destination


def apply_proposal(proposal: dict, root: Path = ROOT) -> list[str]:
    if not isinstance(proposal, dict) or not isinstance(proposal.get('files'), list):
        raise ValueError('response must contain files list')
    edits = proposal['files']
    if not 1 <= len(edits) <= MAX_FILES:
        raise ValueError('unexpected number of files')
    checked: list[tuple[Path, str]] = []
    total = 0
    seen = set()
    changed_python = False
    for edit in edits:
        if not isinstance(edit, dict) or not isinstance(edit.get('content'), str):
            raise ValueError('each edit needs a text content field')
        path = safe_target(edit.get('path'), root)
        if path in seen:
            raise ValueError('duplicate path')
        seen.add(path)
        data = edit['content']
        total += len(data.encode('utf-8'))
        if total > MAX_EDIT_BYTES:
            raise ValueError('generated edit too large')
        if path.parts[len(root.parts)] == 'lab' and path.suffix == '.py':
            changed_python = True
        if path.exists() and path.read_text(encoding='utf-8') == data:
            continue
        checked.append((path, data))
    if not changed_python:
        raise ValueError('proposal must include at least one lab/*.py source edit')
    if not checked:
        raise ValueError('nothing changed')
    # Validate every path before touching any source file.
    for path, data in checked:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding='utf-8')
    return [p.relative_to(root).as_posix() for p, _ in checked]


def build_context(root: Path, task: dict) -> str:
    # A bounded snapshot avoids making arbitrary repository files available.
    files = [root / 'lab/__init__.py', root / 'lab/metrics.py',
             root / 'docs/guide.md', root / 'AGENTS.md']
    files += sorted((root / 'lab').glob('*.py'))
    files += sorted((root / 'tests').glob('test_*.py'))
    known = {}
    for path in files:
        if path.is_file() and not path.is_symlink():
            rel = path.relative_to(root).as_posix()
            known[rel] = path.read_text(encoding='utf-8')[:16000]
    return (create_prompt(task) + '\nThe following are current source files, as JSON.\n' +
            json.dumps(known, ensure_ascii=False) +
            '\nReturn ONLY a JSON object with a files array. Each file has exact '
            'path and complete replacement content. Create genuine tested code, '
            'not filler commits. Change no other files. No markdown code fences.')


def generate(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> dict:
    if not re.fullmatch(r'[a-zA-Z0-9._-]+', model):
        raise ValueError('invalid Gemini model name')
    schema = {
        'type': 'OBJECT',
        'properties': {
            'summary': {'type': 'STRING'},
            'files': {'type': 'ARRAY', 'items': {'type': 'OBJECT', 'properties': {
                'path': {'type': 'STRING'}, 'content': {'type': 'STRING'}},
                'required': ['path', 'content']}},
        }, 'required': ['files']}
    payload = {
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {'responseMimeType': 'application/json',
                             'responseSchema': schema, 'maxOutputTokens': 12000},
    }
    req = Request(
        'https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key},
        method='POST',
    )
    max_attempts = 4
    for attempt in range(1, max_attempts + 1):
        try:
            with urlopen(req, timeout=90) as response:
                data = json.load(response)
            response_text = ''.join(
                part.get('text', '')
                for part in data['candidates'][0]['content']['parts']
            )
            return json.loads(response_text)
        except HTTPError as exc:
            if exc.code in {500, 502, 503, 504} and attempt < max_attempts:
                delay = 8 * (2 ** (attempt - 1))
                print(
                    f'Gemini HTTP {exc.code}; retrying in {delay}s '
                    f'(attempt {attempt}/{max_attempts})',
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            if exc.code in {500, 502, 503, 504}:
                raise RuntimeError(
                    f'Gemini service unavailable (HTTP {exc.code}) after '
                    f'{max_attempts} attempts. Run the workflow again later.'
                ) from exc
            if exc.code == 429:
                raise RuntimeError(
                    'Gemini rate/quota limit (HTTP 429). Check the free-tier '
                    'usage and limits in Google AI Studio. No changes published.'
                ) from exc
            if exc.code in {401, 403}:
                raise RuntimeError(
                    f'Gemini access denied (HTTP {exc.code}). Verify the '
                    'GEMINI_API_KEY secret and account/model access.'
                ) from exc
            if exc.code == 404:
                raise RuntimeError(
                    'Gemini model unavailable (HTTP 404). Verify GEMINI_MODEL '
                    'and the models enabled for your account.'
                ) from exc
            raise RuntimeError(f'Gemini API HTTP error {exc.code}') from exc
        except (URLError, TimeoutError) as exc:
            if attempt < max_attempts:
                delay = 8 * (2 ** (attempt - 1))
                print(
                    f'Gemini network timeout/error; retrying in {delay}s '
                    f'(attempt {attempt}/{max_attempts})',
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
            raise RuntimeError(
                'Gemini connection failed after multiple attempts. '
                'Try the workflow again later.'
            ) from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise RuntimeError('Gemini returned an invalid structured response') from exc


def main() -> None:
    key = os.environ.get('GEMINI_API_KEY', '')
    if not key:
        raise SystemExit('GEMINI_API_KEY GitHub Actions secret is required')
    task = pending_task()
    if task is None:
        print('No approved backlog tasks remain')
        return
    proposal = generate(build_context(ROOT, task), key, os.getenv('GEMINI_MODEL', DEFAULT_MODEL))
    files = apply_proposal(proposal)
    print('Generated changes for task', task['id'], ':', ', '.join(files))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError) as exc:
        print('Free AI generation failed:', exc, file=sys.stderr)
        raise SystemExit(1)
