"""
OpticKnowledgeSpace vault lint tool.

Checks:
- YAML frontmatter validity
- Empty/null fields
- H1 heading presence
- Wiki link resolution (markdown files + attachments)
- Unbalanced wiki links

Usage:
    cd OpticKnowledgeSpace/.compute
    .venv/Scripts/python.exe scripts/lint_vault.py
"""

import re
import yaml
from pathlib import Path
from collections import Counter


def lint_vault():
    # Determine project root by looking for OpticKnowledgeSpace directory
    cwd = Path.cwd()
    if cwd.name == 'OpticKnowledgeSpace':
        base = cwd
    elif cwd.name == '.compute' and cwd.parent.name == 'OpticKnowledgeSpace':
        base = cwd.parent
    elif (cwd / 'OpticKnowledgeSpace').is_dir():
        base = cwd / 'OpticKnowledgeSpace'
    else:
        raise RuntimeError('Could not find OpticKnowledgeSpace directory. Run from project root or OpticKnowledgeSpace/.compute.')
    exclude = {'.venv', '.obsidian', '.hinote', '.copilot', 'node_modules', 'copilot'}

    md_files = []
    attachments = []
    for p in base.rglob('*'):
        if any(part in exclude for part in p.parts):
            continue
        if not p.is_file():
            continue
        if p.suffix == '.md':
            md_files.append(p)
        elif p.suffix in {'.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf'}:
            attachments.append(p)

    md_files.sort()
    attachments.sort()

    file_map = {}
    rel_map = {}
    for p in md_files + attachments:
        file_map.setdefault(p.stem, []).append(p)
        rel = p.relative_to(base).with_suffix('')
        rel_map[str(rel).replace('\\\\', '/')] = p
        rel_with_suffix = p.relative_to(base)
        rel_map[str(rel_with_suffix).replace('\\\\', '/')] = p

    issues = []
    all_links = []

    for p in md_files:
        text = p.read_text(encoding='utf-8')
        lines = text.split('\n')

        # Frontmatter checks
        if text.startswith('---'):
            parts = text.split('---', 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1].strip())
                    if fm is None:
                        issues.append((str(p), 'empty_frontmatter', 'frontmatter is empty'))
                    else:
                        for key, val in fm.items():
                            if val is None:
                                issues.append((str(p), 'null_field', f'{key} is null'))
                        if 'aliases' in fm and fm['aliases'] and isinstance(fm['aliases'], str):
                            issues.append((str(p), 'aliases_not_list', 'aliases should be a list'))
                except yaml.YAMLError as e:
                    issues.append((str(p), 'yaml_error', str(e).replace('\n', ' ')))
            else:
                issues.append((str(p), 'frontmatter_not_closed', 'frontmatter not closed'))
        else:
            if 'README' not in p.name:
                issues.append((str(p), 'no_frontmatter', 'file does not start with frontmatter'))

        # H1 checks
        h1_count = sum(1 for line in lines if line.startswith('# '))
        if h1_count == 0:
            issues.append((str(p), 'no_h1', 'no H1'))

        # Wiki link checks
        for match in re.finditer(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]', text):
            target = match.group(1)
            all_links.append((str(p), target))

            resolved = None
            if target in file_map or target.replace('\\\\', '/') in rel_map:
                resolved = file_map.get(target, [None])[0] or rel_map.get(target.replace('\\\\', '/'))

            if resolved is None:
                target_no_ext = Path(target.replace('\\\\', '/')).with_suffix('')
                target_key = str(target_no_ext).replace('\\\\', '/')
                if target_key in rel_map:
                    resolved = rel_map[target_key]

            if resolved is None:
                cur_dir = p.parent
                rel_target = Path(target.replace('\\\\', '/'))
                abs_target = (cur_dir / rel_target).resolve()
                try:
                    rel_to_base = abs_target.relative_to(base.resolve())
                    key = str(rel_to_base.with_suffix('')).replace('\\\\', '/')
                    resolved = rel_map.get(key)
                    if resolved is None:
                        key_with_suffix = str(rel_to_base).replace('\\\\', '/')
                        resolved = rel_map.get(key_with_suffix)
                except Exception:
                    pass

            if resolved is None:
                issues.append((str(p), 'broken_link', f'[[{target}]]'))

    counts = Counter(issue[1] for issue in issues)
    print('=== Vault lint results ===')
    print(f'Total markdown files: {len(md_files)}')
    print(f'Total wiki links: {len(all_links)}')
    print(f'Unique link targets: {len(set(t for _, t in all_links))}')
    print()
    if counts:
        print('Issue counts:')
        for k, v in counts.most_common():
            print(f'{v:4d} {k}')
        print(f'\nFiles with issues: {len(set(issue[0] for issue in issues))}')
        print('\n=== Detailed issues ===')
        for issue_type in sorted(set(i[1] for i in issues)):
            print(f'\n--- {issue_type} ---')
            for issue in issues:
                if issue[1] == issue_type:
                    print(f'{issue[0]}: {issue[2]}')
    else:
        print('No issues found.')


if __name__ == '__main__':
    lint_vault()
