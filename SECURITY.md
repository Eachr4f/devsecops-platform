# Politique de sécurité

## Périmètre

DevSecOps Platform est un projet personnel d'apprentissage.
Il n'est pas destiné à un usage en production.
Les contrôles automatisés ne garantissent pas l'absence de vulnérabilités.

## Signaler une vulnérabilité

Privilégiez le signalement privé GitHub :
https://github.com/Eachr4f/devsecops-platform/security/advisories/new

Si cette fonctionnalité n'est pas disponible, ouvrez une issue demandant
uniquement un canal de contact privé, sans publier de détail exploitable,
de secret ou de donnée sensible.

Un signalement utile précise le commit concerné, le composant affecté,
l'impact estimé et les étapes de reproduction dans un environnement de test.

## Contrôles mis en place

- Gitleaks en hook pre-commit et dans GitHub Actions.
- Ruff, tests pytest et seuil de couverture de 70 %.
- Analyse statique avec Semgrep.
- Vérifications Docker dans la CI.
- Protection de main avec contrôles obligatoires.
- Conteneurs non-root et mesures de durcissement Docker Compose.

## Limites et suivi

Trivy a été utilisé localement. Son intégration au pipeline est prévue
en semaine 3, avec le SBOM, la signature des images et leur publication.

Les résultats, exclusions et vulnérabilités encore présentes sont
documentés dans docs/vulnerability-report.md.

Les exemples volontairement vulnérables restent sur des branches de
démonstration et ne doivent pas être fusionnés dans main.

En cas d'exposition d'un véritable secret, révoquez-le ou remplacez-le
immédiatement. Supprimer le fichier ne supprime pas le secret de l'historique.
