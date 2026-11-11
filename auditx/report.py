"""Génère le rapport d'audit en Markdown et en HTML."""

from __future__ import annotations

import hashlib
import html
from datetime import date
from pathlib import Path

from .checks import solidity_files
from .models import Finding, Severity, SuiteSummary

PREFIX = {Severity.CRITICAL: "C", Severity.HIGH: "H", Severity.MEDIUM: "M", Severity.LOW: "L", Severity.INFORMATIONAL: "I"}


def number(findings: list[Finding]) -> list[Finding]:
    ordered = sorted(findings, key=lambda f: (-f.severity, f.detector))
    counters: dict[Severity, int] = {}
    for f in ordered:
        counters[f.severity] = counters.get(f.severity, 0) + 1
        f.id = f"{PREFIX[f.severity]}-{counters[f.severity]:02d}"
    return ordered


def scope(root: Path) -> list[tuple[str, int, str]]:
    rows = []
    for p in solidity_files(root):
        data = p.read_bytes()
        rows.append((str(p.relative_to(root)), data.count(b"\n") + 1, hashlib.sha256(data).hexdigest()[:16]))
    return rows


def render_markdown(project: str, client: str, root: Path, findings: list[Finding], tests: SuiteSummary,
                    commit: str = "") -> str:
    findings = number(findings)
    counts = {s: sum(1 for f in findings if f.severity == s) for s in Severity}
    out = [
        f"# Rapport d'audit express – {project}",
        "",
        f"**Client :** {client}  ",
        f"**Date :** {date.today().isoformat()}  ",
        f"**Version analysée :** `{commit or 'non précisée'}`",
        "",
        "## Résumé",
        "",
        "| Gravité | Nombre |",
        "| --- | --- |",
        *[f"| {s.label} | {counts[s]} |" for s in sorted(Severity, reverse=True)],
        "",
    ]
    if tests.ran:
        status = "réussis" if tests.failed == 0 else "en échec"
        out += [f"Tests du projet : **{tests.passed} réussis, {tests.failed} en échec** ({status}).", ""]
    out += ["## Périmètre", "", "| Fichier | Lignes | SHA-256 (16 premiers caractères) |", "| --- | --- | --- |"]
    out += [f"| `{f}` | {n} | `{h}` |" for f, n, h in scope(root)]
    out += [
        "",
        "## Méthodologie",
        "",
        "1. Compilation et exécution de la suite de tests du projet (Foundry).",
        "2. Analyse statique avec Slither (plus de 90 détecteurs).",
        "3. Détecteurs complémentaires audit-express (tx.origin, delegatecall, appels non vérifiés, etc.).",
        "4. Revue manuelle des constats et de la logique métier par l'auditeur.",
        "",
        "## Constats",
        "",
    ]
    if not findings:
        out += ["Aucun constat automatique.", ""]
    for f in findings:
        out += [
            f"### {f.id} – {f.title}",
            "",
            f"**Gravité :** {f.severity.label} · **Confiance :** {f.confidence} · **Source :** {f.source} (`{f.detector}`)",
            "",
            f.description,
            "",
            "**Emplacements :** " + ", ".join(f"`{loc}`" for loc in f.locations[:10])
            + (f" et {len(f.locations) - 10} autres" if len(f.locations) > 10 else ""),
            "",
            f"**Recommandation :** {f.recommendation}",
            "",
        ]
    out += [
        "## Avertissement",
        "",
        "Ce rapport combine des outils automatiques et une revue manuelle limitée dans le temps. Il ne garantit pas "
        "l'absence de vulnérabilités et ne remplace pas un audit complet pour des montants importants. Il ne "
        "constitue pas un conseil financier ou juridique.",
        "",
    ]
    return "\n".join(out)


def markdown_to_html(md: str, title: str) -> str:
    """Conversion minimale (titres, tableaux, listes, gras, code) sans dépendance externe."""
    import re

    def inline(text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    body, in_table, in_list = [], False, False
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-", " "} for c in cells):
                continue
            if not in_table:
                body.append("<table>")
                in_table = True
                body.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                body.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            body.append("</table>")
            in_table = False
        m = re.match(r"^\d+\. (.*)", line)
        if m:
            if not in_list:
                body.append("<ol>")
                in_list = True
            body.append(f"<li>{inline(m.group(1))}</li>")
            continue
        if in_list:
            body.append("</ol>")
            in_list = False
        if line.startswith("### "):
            body.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{inline(line[2:])}</h1>")
        elif line.strip():
            body.append(f"<p>{inline(line.rstrip())}</p>")
    if in_table:
        body.append("</table>")
    if in_list:
        body.append("</ol>")
    style = (
        "body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1d2433;line-height:1.5}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #dde1e8;padding:.4rem .6rem;text-align:left}"
        "th{background:#f3f5f9}code{background:#f3f5f9;padding:0 .25rem;border-radius:3px}h3{margin-top:2rem}"
    )
    return (
        f"<!DOCTYPE html><html lang=\"fr\"><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title>"
        f"<style>{style}</style></head><body>{''.join(body)}</body></html>"
    )


def write(md: str, out: Path, title: str) -> None:
    out.write_text(md, encoding="utf-8")
    out.with_suffix(".html").write_text(markdown_to_html(md, title), encoding="utf-8")
