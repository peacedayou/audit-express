"""Transforme la sortie JSON de Slither en constats lisibles."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Finding, Location, Severity

CONFIDENCE = {"High": "Élevée", "Medium": "Moyenne", "Low": "Faible"}

# Recommandations rédigées pour les détecteurs les plus fréquents
RECOMMENDATIONS = {
    "reentrancy-eth": "Appliquer le motif checks-effects-interactions et ajouter un verrou nonReentrant.",
    "reentrancy-no-eth": "Mettre à jour l'état avant tout appel externe ou utiliser nonReentrant.",
    "arbitrary-send-eth": "Restreindre la destination des transferts d'ETH à des adresses autorisées.",
    "unchecked-transfer": "Utiliser SafeERC20 (safeTransfer / safeTransferFrom).",
    "unchecked-lowlevel": "Vérifier la valeur de retour de chaque appel de bas niveau.",
    "tx-origin": "Utiliser msg.sender pour l'autorisation, jamais tx.origin.",
    "suicidal": "Supprimer selfdestruct ou le protéger par un contrôle d'accès strict.",
    "controlled-delegatecall": "Ne jamais faire de delegatecall vers une adresse fournie par l'utilisateur.",
    "timestamp": "Éviter block.timestamp pour des décisions critiques à la seconde près.",
    "missing-zero-check": "Refuser l'adresse zéro pour les paramètres d'adresse sensibles.",
    "divide-before-multiply": "Multiplier avant de diviser, ou utiliser Math.mulDiv.",
    "uninitialized-state": "Initialiser explicitement les variables d'état.",
    "locked-ether": "Ajouter une fonction de retrait ou retirer payable.",
    "solc-version": "Fixer une version récente et précise du compilateur.",
    "low-level-calls": "Documenter et vérifier chaque appel de bas niveau.",
}


def _locations(element_list: list[dict], root: str) -> list[Location]:
    seen, out = set(), []
    for el in element_list:
        mapping = el.get("source_mapping") or {}
        path = mapping.get("filename_relative") or mapping.get("filename_short") or ""
        lines = mapping.get("lines") or []
        if not path:
            continue
        loc = Location(path.removeprefix(root).lstrip("/"), lines[0] if lines else None)
        if loc not in seen:
            seen.add(loc)
            out.append(loc)
    return out


def parse(data: dict, root: str = "", exclude_prefixes=("lib/", "test/", "script/", "node_modules/")) -> list[Finding]:
    detectors = (data.get("results") or {}).get("detectors") or []
    findings = []
    for d in detectors:
        locs = _locations(d.get("elements") or [], root)
        if locs and all(str(loc.file).startswith(exclude_prefixes) for loc in locs):
            continue  # constat uniquement dans les dépendances ou les tests
        check = d.get("check", "inconnu")
        findings.append(
            Finding(
                detector=check,
                title=check.replace("-", " ").capitalize(),
                severity=Severity.from_slither(d.get("impact", "informational")),
                description=(d.get("description") or "").strip(),
                recommendation=RECOMMENDATIONS.get(check, "Analyser le contexte et corriger si le risque est confirmé."),
                confidence=CONFIDENCE.get(d.get("confidence", "Medium"), "Moyenne"),
                source="slither",
                locations=locs,
            )
        )
    return findings


def parse_file(path: str | Path, root: str = "") -> list[Finding]:
    return parse(json.loads(Path(path).read_text(encoding="utf-8")), root)
