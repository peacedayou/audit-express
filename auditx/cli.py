"""Ligne de commande : auditx <dossier du projet> --client "Nom" --out rapport.md"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess  # noqa: S404 (outils d'analyse lancés sans shell)
import sys
from pathlib import Path

from . import checks, report, slither_parse
from .models import SuiteSummary


def _run(cmd: list[str], cwd: Path, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)  # noqa: S603


def run_tests(root: Path) -> SuiteSummary:
    if not (root / "foundry.toml").exists() or not shutil.which("forge"):
        return SuiteSummary()
    proc = _run(["forge", "test"], root)
    m = re.search(r"(\d+) tests passed, (\d+) failed", proc.stdout)
    if not m:
        return SuiteSummary(ran=True, passed=0, failed=1)
    return SuiteSummary(ran=True, passed=int(m.group(1)), failed=int(m.group(2)))


def run_slither(root: Path) -> list:
    if not shutil.which("slither"):
        print("Slither introuvable : analyse statique ignorée (pip install slither-analyzer)", file=sys.stderr)
        return []
    out = root / ".auditx-slither.json"
    out.unlink(missing_ok=True)
    _run(["slither", ".", "--json", str(out), "--exclude-dependencies"], root)
    if not out.exists():
        print("Slither n'a pas produit de résultat", file=sys.stderr)
        return []
    try:
        return slither_parse.parse(json.loads(out.read_text(encoding="utf-8")), root=str(root))
    finally:
        out.unlink(missing_ok=True)


def git_commit(root: Path) -> str:
    if not shutil.which("git"):
        return ""
    proc = _run(["git", "rev-parse", "--short", "HEAD"], root, timeout=30)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="auditx", description="Rapport d'audit Solidity automatisé")
    parser.add_argument("project", type=Path)
    parser.add_argument("--client", default="Confidentiel")
    parser.add_argument("--name", help="Nom du projet (par défaut : nom du dossier)")
    parser.add_argument("--out", type=Path, default=Path("rapport-audit.md"))
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args(argv)

    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f"Dossier introuvable : {root}")

    tests = SuiteSummary() if args.skip_tests else run_tests(root)
    findings = run_slither(root) + checks.run(root)
    name = args.name or root.name
    md = report.render_markdown(name, args.client, root, findings, tests, commit=git_commit(root))
    report.write(md, args.out, f"Audit {name}")
    print(f"Rapport écrit : {args.out} et {args.out.with_suffix('.html')} ({len(findings)} constats)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
