# Sécurité de la chaîne logicielle

## Objectif

Publier les images API et frontend sur GHCR, analyser leurs vulnérabilités,
produire leur inventaire logiciel (SBOM), puis signer les images et
attester leurs SBOM avec Cosign.

## Deux workflows

- `.github/workflows/ci.yml` contrôle les contributions : Gitleaks,
  Ruff, pytest, Semgrep, Hadolint, tests Docker et Trivy.
  Le contrôle obligatoire `CI OK` attend la réussite des cinq jobs.
- `.github/workflows/publish.yml` s'exécute sur les push de `main`.
  Il construit et publie séparément les images API et frontend.
  Il ne publie pas depuis une pull request.

## Étapes de publication

1. Récupérer le code du commit.
2. Construire l'image avec le SHA du commit comme tag.
3. Analyser l'image avec Trivy.
4. Bloquer les vulnérabilités HIGH/CRITICAL disposant d'un correctif.
5. Publier l'image dans GHCR et relever son digest.
6. Générer avec Syft le SBOM de l'image publiée, lue par digest.
7. Signer le digest avec Cosign.
8. Attester le SBOM en l'associant au même digest.
9. Vérifier la signature et l'attestation.
10. Conserver les SBOM, digests et résultats de vérification comme artifacts.

Les mauvaises configurations HIGH/CRITICAL des Dockerfiles sont également
bloquantes dans le job Trivy de la CI.

## Outils et permissions

| Élément | Rôle |
|---|---|
| Trivy 0.74.0 | Analyse des vulnérabilités et des configurations |
| Syft 1.52.0 | Inventaire des composants, export SPDX JSON |
| Cosign 3.1.3 | Signature, attestation et vérification |
| GHCR | Stockage des images et des objets de signature/attestation |
| `contents: read` | Lecture du dépôt |
| `packages: write` | Publication dans GHCR |
| `id-token: write` | Obtention de l'identité OIDC du workflow |

Les binaires téléchargés sont contrôlés avec des SHA-256 épinglés.
La signature utilise une clé éphémère et l'identité OIDC GitHub :
aucune clé privée permanente de signature n'est enregistrée dans
les secrets du dépôt.

## Identité attendue

- Identité :
  `https://github.com/Eachr4f/devsecops-platform/.github/workflows/publish.yml@refs/heads/main`
- Émetteur OIDC :
  `https://token.actions.githubusercontent.com`

## Publication vérifiée le 23 octobre 2026

Commit : `9c511d3e84fa307213246ead04dc54594ff8e21d`.

Exécution :
https://github.com/Eachr4f/devsecops-platform/actions/runs/39983314818

API :

```text
ghcr.io/eachr4f/devsecops-api@sha256:012a4c6606ba52ec53ba72693da72ac6a17e9dfaba129b2a4efba1f158350279
```

Frontend :

```text
ghcr.io/eachr4f/devsecops-frontend@sha256:9a602c809498706567a7d53db368c9d3a8807258bc4072a966f888ee8ff8ba6a
```

| Inventaire | Format | Nombre d'entrées |
|---|---|---:|
| API | SPDX-2.3 | 111 |
| Frontend | SPDX-2.3 | 72 |

Ces nombres représentent des entrées d'inventaire, pas des vulnérabilités
ni nécessairement des composants uniques.

## Vérification indépendante

Depuis une machine équipée de Cosign, renseigner la référence complète :

```bash
REF="ghcr.io/eachr4f/devsecops-api@sha256:012a4c6606ba52ec53ba72693da72ac6a17e9dfaba129b2a4efba1f158350279"
IDENTITY="https://github.com/Eachr4f/devsecops-platform/.github/workflows/publish.yml@refs/heads/main"
ISSUER="https://token.actions.githubusercontent.com"

cosign verify \
  --certificate-identity "$IDENTITY" \
  --certificate-oidc-issuer "$ISSUER" \
  "$REF"

cosign verify-attestation \
  --type spdxjson \
  --certificate-identity "$IDENTITY" \
  --certificate-oidc-issuer "$ISSUER" \
  "$REF"
```

Répéter avec la référence frontend.

## Résultats observés depuis la VM

| Test | Résultat |
|---|---|
| Signature API, identité attendue | Réussite |
| Attestation SBOM API, identité attendue | Réussite |
| Signature frontend, identité attendue | Réussite |
| Attestation SBOM frontend, identité attendue | Réussite |
| Mauvaise identité demandée, API et frontend | Refus, identité du certificat non correspondante, code 1 |
| Ancienne image API accessible mais non signée | Refus `no signatures found`, code 10 |

Image utilisée pour le test sans signature :

```text
ghcr.io/eachr4f/devsecops-api@sha256:8cd66f0d170a152c51418e9f0e20a6511c0c1713ed0fe745bda149c91665b1c2
```

Son accessibilité a été vérifiée avec `docker manifest inspect`
avant le test Cosign.

Preuves : [fichiers de vérification](security/week3/verification/).

Les fichiers `verification-sbom-*.json` sont les sorties de Cosign.
Les fichiers `sbom-*-verifie-1.spdx.json` sont les inventaires extraits
de ces attestations après leur vérification.

## Limites

- Une signature prouve une origine et une intégrité selon la politique
  de vérification ; elle ne garantit pas l'absence de vulnérabilités.
- Le SBOM décrit les composants détectés ; son exhaustivité n'est pas garantie.
- `--ignore-unfixed` exclut du blocage les vulnérabilités sans correctif.
  Il ne les corrige pas. Leur suivi figure dans le rapport de sécurité.
- Les résultats Trivy dépendent de la base de vulnérabilités à la date du scan.
- Publish ne dépend pas de la fin de la CI déclenchée sur le même push.
  Il repose sur les contrôles exigés avant fusion et sur son propre scan.
- La publication précède la signature : un échec ultérieur peut laisser
  une image publiée sans signature.
- Les deux jobs de publication sont indépendants : une réussite partielle
  est possible.

## Validations restantes avant clôture de la semaine 3

- Vérifier la visibilité publique des deux paquets GHCR et leur liaison au dépôt.
- Confirmer les preuves Trivy rouge puis vert et la fermeture de la PR de démonstration.
- Suivi des vulnérabilités sans correctif actualisé le 25 octobre 2026 :
  voir le rapport de sécurité. Les constats API restent ouverts.
- Modifier un élément visible de l'application via une PR, puis vérifier
  le nouveau digest publié après fusion.
- Finaliser la documentation et publier le tag `v0.3.0`.
