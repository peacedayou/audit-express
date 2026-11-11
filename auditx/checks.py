"""Détecteurs maison, complémentaires à Slither : rapides, sans compilation."""

from __future__ import annotations

import re
from pathlib import Path

from .models import Finding, Location, Severity

EXCLUDED_DIRS = {"lib", "test", "tests", "script", "node_modules", "out", "cache", ".git"}


def _strip_comments(line: str) -> str:
    return line.split("//", 1)[0]


RULES = [
    {
        "id": "floating-pragma",
        "pattern": re.compile(r"pragma\s+solidity\s*[\^>~]"),
        "severity": Severity.INFORMATIONAL,
        "title": "Version du compilateur non figée",
        "description": "Une version flottante peut compiler le contrat avec un compilateur différent de celui testé.",
        "recommendation": "Utiliser une version exacte pour les contrats déployés (ex. pragma solidity 0.8.28;).",
    },
    {
        "id": "tx-origin",
        "pattern": re.compile(r"\btx\.origin\b"),
        "severity": Severity.HIGH,
        "title": "Utilisation de tx.origin",
        "description": "tx.origin pour l'autorisation permet l'hameçonnage via un contrat intermédiaire.",
        "recommendation": "Utiliser msg.sender.",
    },
    {
        "id": "delegatecall",
        "pattern": re.compile(r"\.delegatecall\s*\("),
        "severity": Severity.MEDIUM,
        "title": "Appel delegatecall",
        "description": "delegatecall exécute du code externe dans le contexte du contrat (stockage et fonds).",
        "recommendation": "N'appeler que des implémentations de confiance et immuables.",
    },
    {
        "id": "selfdestruct",
        "pattern": re.compile(r"\bselfdestruct\s*\("),
        "severity": Severity.MEDIUM,
        "title": "Utilisation de selfdestruct",
        "description": "selfdestruct est obsolète (EIP-6780) et son comportement a changé.",
        "recommendation": "Retirer selfdestruct.",
    },
    {
        "id": "ecrecover",
        "pattern": re.compile(r"\becrecover\s*\("),
        "severity": Severity.LOW,
        "title": "ecrecover utilisé directement",
        "description": "ecrecover accepte des signatures malléables et retourne l'adresse zéro en cas d'échec.",
        "recommendation": "Utiliser la bibliothèque ECDSA d'OpenZeppelin.",
    },
    {
        "id": "unchecked-send",
        "pattern": re.compile(r"^\s*[\w\.\[\]\(\)]+\.(send|call\{[^}]*\}|call)\s*\("),
        "severity": Severity.MEDIUM,
        "title": "Valeur de retour d'un appel ignorée",
        "description": "Un appel de bas niveau dont le résultat n'est pas vérifié peut échouer silencieusement.",
        "recommendation": "Récupérer le booléen de retour et faire revert en cas d'échec.",
    },
    {
        "id": "assembly",
        "pattern": re.compile(r"\bassembly\s*(\(\"memory-safe\"\)\s*)?\{"),
        "severity": Severity.INFORMATIONAL,
        "title": "Bloc assembly",
        "description": "Le code assembleur contourne les vérifications du compilateur.",
        "recommendation": "Revue manuelle approfondie de chaque bloc.",
    },
]


def solidity_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.sol") if not (set(p.relative_to(root).parts[:-1]) & EXCLUDED_DIRS)
    )


def run(root: str | Path) -> list[Finding]:
    root = Path(root)
    by_rule: dict[str, Finding] = {}
    for path in solidity_files(root):
        rel = str(path.relative_to(root))
        for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            line = _strip_comments(raw)
            for rule in RULES:
                if rule["pattern"].search(line):
                    f = by_rule.setdefault(
                        rule["id"],
                        Finding(
                            detector=rule["id"],
                            title=rule["title"],
                            severity=rule["severity"],
                            description=rule["description"],
                            recommendation=rule["recommendation"],
                            confidence="Moyenne",
                            source="auditx",
                        ),
                    )
                    f.locations.append(Location(rel, number))
    return list(by_rule.values())
