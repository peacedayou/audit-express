import json
from pathlib import Path

from auditx import checks, report, slither_parse
from auditx.cli import main
from auditx.models import Finding, Location, Severity, SuiteSummary

FIX = Path(__file__).parent / "fixtures"


def test_slither_parse_maps_severity_and_skips_dependencies():
    findings = slither_parse.parse_file(FIX / "slither.json")
    assert [f.detector for f in findings] == ["reentrancy-eth", "timestamp"]
    assert findings[0].severity == Severity.HIGH
    assert findings[0].locations == [Location("src/Vault.sol", 20)]
    assert "nonReentrant" in findings[0].recommendation


def test_slither_parse_handles_empty_results():
    assert slither_parse.parse({"success": True, "results": {}}) == []


def test_custom_checks_find_known_issues_and_ignore_lib_and_comments():
    found = {f.detector: f for f in checks.run(FIX / "contracts")}
    assert {"tx-origin", "delegatecall", "ecrecover", "unchecked-send", "floating-pragma"} <= set(found)
    # Seule la vraie ligne compte (pas le commentaire, pas lib/)
    assert [loc.line for loc in found["tx-origin"].locations] == [9]
    assert all("lib/" not in str(loc) for f in found.values() for loc in f.locations)


def test_numbering_orders_by_severity():
    fs = [
        Finding("a", "A", Severity.LOW, "d"),
        Finding("b", "B", Severity.HIGH, "d"),
        Finding("c", "C", Severity.HIGH, "d"),
    ]
    assert [f.id for f in report.number(fs)] == ["H-01", "H-02", "L-01"]


def test_markdown_report_contains_summary_scope_and_findings(tmp_path):
    findings = checks.run(FIX / "contracts")
    md = report.render_markdown("Démo", "Client X", FIX / "contracts", findings, SuiteSummary(ran=True, passed=3, failed=0))
    assert "# Rapport d'audit express – Démo" in md
    assert "| Élevée | 1 |" in md
    assert "`Vulnerable.sol`" in md
    assert "H-01 – Utilisation de tx.origin" in md
    assert "3 réussis, 0 en échec" in md


def test_html_escapes_content():
    html = report.markdown_to_html("# Titre <script>alert(1)</script>\n\n| a | b |\n| --- | --- |\n| `x` | **y** |", "t")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<code>x</code>" in html and "<strong>y</strong>" in html


def test_cli_end_to_end_without_external_tools(tmp_path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    out = tmp_path / "rapport.md"
    assert main([str(FIX / "contracts"), "--client", "ACME", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "ACME" in text and "tx.origin" in text
    assert out.with_suffix(".html").exists()


def test_fixture_is_valid_json():
    json.loads((FIX / "slither.json").read_text())
