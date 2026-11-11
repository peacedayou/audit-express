# Audit Express

![CI](https://github.com/peacedayou/audit-express/actions/workflows/ci.yml/badge.svg)

Génère en une commande un **rapport d'audit professionnel** pour un projet Solidity :
tests Foundry, analyse statique **Slither**, détecteurs complémentaires et rapport en Markdown et HTML,
prêt à être complété par une revue manuelle.

```bash
pip install -e ".[analyse]"        # installe auditx + Slither
auditx ../mon-projet --client "ACME" --out rapport.md
# → rapport.md et rapport.html
```

Un rapport de démonstration complet sur [web3-contract-kit](https://github.com/peacedayou/web3-contract-kit)
est produit à chaque commit : onglet **Actions**, puis le résumé du job `demo` ou l'artefact `rapport-demo`.

## Contenu du rapport

- Résumé par gravité (Critique, Élevée, Moyenne, Faible, Information)
- Périmètre figé : chaque fichier avec son nombre de lignes et son empreinte SHA-256
- Résultat de la suite de tests du projet
- Constats numérotés (H-01, M-01…) avec emplacements précis et recommandations en français
- Méthodologie et avertissement

## Détecteurs maison

En plus des 90+ détecteurs de Slither : `tx.origin`, `delegatecall`, `selfdestruct`, `ecrecover`
brut, appels de bas niveau non vérifiés, pragma flottant, blocs `assembly`. Les dépendances
(`lib/`), les tests et les commentaires sont ignorés.

## Sécurité de l'outil

- Les outils externes sont lancés sans shell, avec un délai maximal.
- Le contenu du rapport HTML est échappé (pas d'injection de code depuis les sources analysées).
- Aucune donnée n'est envoyée sur Internet.

## Offre de service

Voir [docs/OFFRE.md](docs/OFFRE.md) : forfaits, déroulement et limites à indiquer aux clients.

## Développement

```bash
pip install -e ".[dev]"
ruff check . && pytest
```
