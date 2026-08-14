#!/usr/bin/env python3
"""Check the mechanical shape of a spec.

Judgment — is it too long, does it repeat itself, is it recounting the conversation —
belongs to the independent reviewer. This only catches what is decidable by reading
the bytes: the spine, dead section names, frontmatter, and malformed tables.

Usage: lint_spec.py <path>...
Output: `path:line CODE mensagem` on stdout. Exit 1 when any E-code fired.
"""

import re
import sys

# (nome em português, nome em inglês) — as duas grafias valem; a mensagem cita a portuguesa.
REQUIRED_SECTIONS = (("Decisões", "decisions"), ("Em aberto", "open"))
RECOMMENDED_SECTIONS = (
    ("Comportamento", "behavior", "W001", "o mapa de comportamento é o contrato de aceite"),
    ("Tarefas", "tasks", "W002", "sem tarefas o build não tem o que consumir"),
)
# An English section still parses; W003 carries the Portuguese name to write instead.
TRANSLATED_SECTIONS = {
    "decisions": "Decisões",
    "behavior": "Comportamento",
    "tasks": "Tarefas",
    "out of scope": "Fora de escopo",
    "open": "Em aberto",
    "problem": "Problema",
    "hypothesis": "Hipótese",
    "fit": "Encaixe",
    "cuts": "Cortes",
    "legal": "Jurídico",
}
DEAD_SECTIONS = {
    "design": (
        "`## design` é nome morto — no bb `design` é desenho de tela (`/bb:brisar`). "
        "Arquitetura vai pra metade de cima, com o nome que ela tem neste problema."
    ),
    "still open": "seção `## still open` — o nome é `## Em aberto`.",
}
VALID_STATUS = ("pending", "in-progress", "done", "blocked")
MAX_CELL = 100

HEADING = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEPARATOR_CELL = re.compile(r"^:?-{2,}:?$")
# A `|` escaped as `\|` is content, not a column boundary.
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def split_row(line):
    """Return a table row's cells, dropping the empty edges around the outer pipes."""
    parts = CELL_SPLIT.split(line.strip())
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.strip() for p in parts]


def check_frontmatter(lines):
    """Yield problems with the `---` block the spec-state contract requires."""
    if not lines or lines[0].strip() != "---":
        yield 1, "E001", "frontmatter ausente — o bloco `---` com status/created/slug abre o arquivo"
        return

    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), None)
    if end is None:
        yield 1, "E001", "frontmatter sem fechamento `---`"
        return

    fields = {}
    for i in range(1, end):
        key, sep, value = lines[i].partition(":")
        if sep:
            fields[key.strip()] = (i + 1, value.strip())

    for key in ("status", "created", "slug"):
        if key not in fields:
            yield 1, "E001", f"frontmatter sem `{key}`"

    if "status" in fields:
        line_no, value = fields["status"]
        if value not in VALID_STATUS:
            yield line_no, "E001", f"status `{value}` inválido — use {', '.join(VALID_STATUS)}"

    if "created" in fields:
        line_no, value = fields["created"]
        if not DATE.match(value):
            yield line_no, "E001", f"created `{value}` fora do formato YYYY-MM-DD"


def check_body(lines):
    """Yield problems with sections and tables, ignoring fenced blocks."""
    seen = set()
    in_fence = False
    table = []  # (line_no, cells) of the current run of table rows

    def flush(rows):
        if len(rows) < 2:
            return
        header_no, header = rows[0]
        width = len(header)
        body = rows[2:] if all(SEPARATOR_CELL.match(c) for c in rows[1][1]) else rows[1:]
        for line_no, cells in [rows[0]] + body:
            if len(cells) != width:
                yield (
                    line_no,
                    "E005",
                    f"row com {len(cells)} células contra {width} do cabeçalho — "
                    "um `|` literal precisa virar `\\|`",
                )
            for cell in cells:
                if len(cell) > MAX_CELL:
                    yield (
                        line_no,
                        "E004",
                        f"célula de {len(cell)} caracteres (teto {MAX_CELL}) — "
                        "conteúdo desse tamanho é prosa ou bullet, não tabela",
                    )

    for i, line in enumerate(lines, start=1):
        # A fence ends the current run of rows — two tables around a code block are
        # two tables, not one with a mismatched header.
        if FENCE.match(line) or in_fence:
            if table:
                yield from flush(table)
                table = []
            if FENCE.match(line):
                in_fence = not in_fence
            continue

        if line.strip().startswith("|"):
            table.append((i, split_row(line)))
            continue
        if table:
            yield from flush(table)
            table = []

        match = HEADING.match(line)
        if match:
            name = match.group(1).strip().lower()
            seen.add(name)
            if name in DEAD_SECTIONS:
                yield i, "E003", DEAD_SECTIONS[name]
            elif name in TRANSLATED_SECTIONS:
                yield i, "W003", (
                    f"`## {name}` em inglês — em português é "
                    f"`## {TRANSLATED_SECTIONS[name]}`; o arquivo continua válido"
                )

    if table:
        yield from flush(table)

    for pt, en in REQUIRED_SECTIONS:
        if pt.lower() not in seen and en not in seen:
            yield 1, "E002", f"sem `## {pt}` — a espinha precisa dela"

    for pt, en, code, why in RECOMMENDED_SECTIONS:
        if pt.lower() not in seen and en not in seen:
            yield 1, code, f"sem `## {pt}` — {why}"


def lint(path):
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError as err:
        return [(1, "E001", f"não deu pra ler o arquivo: {err}")]
    return sorted([*check_frontmatter(lines), *check_body(lines)], key=lambda p: (p[0], p[1]))


def main(argv):
    if not argv:
        print("uso: lint_spec.py <caminho>...", file=sys.stderr)
        return 2

    failed = False
    for path in argv:
        for line_no, code, message in lint(path):
            print(f"{path}:{line_no} {code} {message}")
            failed |= code.startswith("E")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
