# Offre – Audit express de contrats Solidity

Une revue de sécurité rapide et abordable avant le lancement, pour les petits projets qui n'ont
pas le budget d'un cabinet d'audit (souvent de 10 000 à 100 000 $).

## Forfaits

| Forfait | Périmètre | Délai | Prix indicatif |
| --- | --- | --- | --- |
| **Express** | 1 contrat, jusqu'à 300 lignes | 3 jours ouvrables | 300 $ |
| **Standard** | Jusqu'à 1 000 lignes | 5 jours ouvrables | 900 $ |
| **Suivi** | Vérification des corrections après un audit | 2 jours ouvrables | 150 $ |

Les prix sont à ajuster selon ton expérience et la complexité (DeFi, oracles, mises à jour par proxy…).

## Ce que le client reçoit

1. Le rapport (Markdown et HTML) : résumé par gravité, périmètre avec empreintes SHA-256 des fichiers, constats numérotés avec emplacement et recommandation.
2. Les résultats de sa propre suite de tests, et une liste de tests manquants à écrire.
3. Une revue manuelle de la logique métier, ajoutée au rapport généré par `auditx`.
4. Un appel de 30 minutes pour expliquer les constats.

## Déroulement

1. Le client fournit le dépôt et un commit précis : le périmètre est figé par les empreintes.
2. Analyse automatique avec `auditx`, puis revue manuelle (contrôle d'accès, arithmétique, réentrance, oracles, cas limites).
3. Remise du rapport, puis vérification des corrections dans le forfait Suivi.

## Limites, à écrire dans chaque devis

- Un audit réduit le risque mais ne garantit pas l'absence de failles.
- Ce n'est pas un conseil financier ni juridique.
- Le client reste responsable du déploiement et de la gestion de ses clés.
- Recommander un audit complet par un cabinet pour les protocoles qui gèrent des montants importants.

## Où trouver des clients

- Lemon.io, Upwork, Toptal (profil « Solidity Security »)
- Programmes de primes aux bogues : Code4rena, Sherlock et Immunefi bâtissent la réputation
- Communautés de développeurs Web3 (Discord, Telegram), hackathons ETHGlobal
