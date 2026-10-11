# DevSecOps Platform

Projet pédagogique de construction progressive d'une plateforme DevSecOps.
L'application permet d'ajouter des éléments et de consulter leur liste.

## Architecture actuelle

- Frontend : HTML, CSS et JavaScript servis par Nginx.
- API : Flask exécuté avec Gunicorn.
- Données : SQLite, conservé dans un volume Docker.
- Exécution : Docker Compose dans une VM Ubuntu Server.

Nginx sert la page et transmet les requêtes `/api/` à l'API.
Seul le port du frontend est publié sur la VM.

## Démarrer l'application

Prérequis : Docker Engine et le plugin Docker Compose.

```bash
docker compose up --build -d --wait --wait-timeout 120
docker compose ps
```

Dans le laboratoire, l'application est accessible à :

**http://192.168.56.30:8080**

Pour démarrer sur une autre machine en utilisant son adresse de boucle locale :

```bash
FRONTEND_BIND_IP=127.0.0.1 docker compose up --build -d --wait --wait-timeout 120
```

Consulter l'état et les journaux :

```bash
docker compose ps
docker compose logs -f
```

Arrêter les services :

```bash
docker compose down
```

Le volume Docker conserve les données après l'arrêt des conteneurs.
L'option `--volumes` supprime ce volume et les données associées.

## Fonctionnement de l'application

Le navigateur charge les fichiers HTML, CSS et JavaScript servis par Nginx.
Le frontend communique avec l'API via le chemin `/api/`.

Nginx joue également le rôle de reverse proxy : il transmet ces requêtes
au service Flask sur le réseau interne Docker Compose.

L'API traite les demandes et stocke les éléments dans une base SQLite.
Le fichier de base de données est placé dans un volume Docker afin de
conserver les informations lors de la recréation des conteneurs.

| Requête | Fonction |
|---|---|
| `GET /api/items` | Consulter les éléments |
| `POST /api/items` | Ajouter un élément |

Exemples :

```bash
curl --fail --silent --show-error \
  http://192.168.56.30:8080/api/items

curl --fail --silent --show-error \
  -X POST http://192.168.56.30:8080/api/items \
  -H 'Content-Type: application/json' \
  -d '{"name":"Premier élément"}'
```

## Organisation du dépôt

```text
.
├── .githooks/
│   └── pre-commit
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── security/
├── services/
│   ├── api/
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   └── tests/
│   │       └── test_app.py
│   └── frontend/
│       ├── Dockerfile
│       ├── nginx.conf
│       ├── index.html
│       ├── style.css
│       └── app.js
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

| Fichier ou répertoire | Rôle |
|---|---|
| `services/api/app.py` | Logique de l'API et accès aux données |
| `services/api/tests/` | Tests automatisés de l'API |
| `services/api/requirements.txt` | Dépendances de l'application |
| `services/api/requirements-dev.txt` | Dépendances nécessaires au développement et aux tests |
| `services/frontend/nginx.conf` | Configuration du serveur web, du proxy et des en-têtes HTTP |
| `docker-compose.yml` | Services, réseau, stockage et paramètres de durcissement |
| `pyproject.toml` | Configuration des outils Python |
| `.githooks/pre-commit` | Détection locale de secrets avant un commit |
| `.github/workflows/ci.yml` | Pipeline d'intégration continue |
| `.github/dependabot.yml` | Configuration des mises à jour de dépendances |
| `docs/security/` | Rapports conservés comme preuves des analyses |

## Qualité du code et tests

L'API dispose de tests automatisés avec pytest.
Ruff vérifie la qualité et le formatage du code Python.
pytest-cov mesure la couverture des instructions de l'application.

Depuis la racine du dépôt :

```bash
cd services/api

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt

.venv/bin/ruff check .
.venv/bin/ruff format --check .

.venv/bin/python -m pytest -q \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=70
```

Derniers résultats locaux observés :

- Vérification Ruff réussie.
- Vérification du formatage réussie.
- 16 tests réussis.
- Couverture des instructions de `app.py` : **100 %**.
- Seuil minimal de couverture configuré : **70 %**.

Une couverture de 100 % signifie que toutes les instructions mesurées ont
été exécutées pendant les tests. Elle ne garantit pas que tous les scénarios,
les erreurs possibles ou les vulnérabilités sont couverts.

## Durcissement des conteneurs

La configuration applique plusieurs mesures pour limiter les privilèges
et les possibilités de modification des conteneurs :

- Exécution de l'API et du frontend avec des utilisateurs non root.
- Systèmes de fichiers racine en lecture seule.
- Suppression des capabilities Linux.
- Activation de `no-new-privileges`.
- Utilisation de tmpfs pour les répertoires temporaires.
- Limitation des ressources CPU et mémoire.
- Healthchecks pour surveiller l'état des services.
- Publication du seul port frontend sur l'hôte.
- Stockage persistant séparé du système de fichiers de l'API.

Au niveau applicatif, la validation des entrées et les requêtes SQL
paramétrées participent à la sécurisation des échanges avec la base.

Nginx ajoute notamment les en-têtes suivants :

| En-tête | Objectif |
|---|---|
| `Content-Security-Policy` | Restreindre les sources de contenu autorisées |
| `X-Content-Type-Options` | Empêcher l'interprétation automatique d'un type de contenu différent |
| `X-Frame-Options` | Limiter l'intégration des pages dans des frames |

Ces mesures réduisent certains risques ; elles ne constituent pas une
garantie de sécurité complète.

## Détection de secrets

Gitleaks est utilisé à deux niveaux :

- **Localement** : le hook pre-commit contrôle les modifications préparées.
- **Dans la CI** : le job dédié analyse l'historique Git accessible depuis
  le commit testé.

Après installation de Gitleaks, activer le hook pour ce clone :

```bash
git config core.hooksPath .githooks
```

Exécuter manuellement le contrôle local :

```bash
.githooks/pre-commit
```

Les derniers contrôles des fichiers préparés n'ont détecté aucun secret.

Le fichier `.gitignore` exclut notamment l'environnement Python,
les caches, les fichiers `.env` et les bases SQLite locales.

## Analyses de sécurité

| Outil | Utilisation |
|---|---|
| Gitleaks | Détection de secrets |
| Semgrep | Analyse statique du code |
| Hadolint | Analyse des Dockerfiles |
| Trivy | Analyse des vulnérabilités des images Docker |
| actionlint | Validation statique du workflow GitHub Actions |

Les rapports locaux sont conservés dans `docs/security/`.

### Résultats Trivy observés

**Frontend :** le scan initial signalait trois vulnérabilités HIGH.
Après mise à jour des paquets de l'image, le rapport de contrôle ne
signalait plus de vulnérabilité HIGH ou CRITICAL.

**API :** le rafraîchissement de l'image de base n'a pas supprimé les
44 occurrences HIGH signalées dans les paquets système.
Ces constats restent ouverts. Le contrôle filtré sur CRITICAL
ne signalait aucun résultat.

Ces résultats décrivent les images analysées au moment des scans.
Une nouvelle construction ou une mise à jour de la base de vulnérabilités
peut modifier les résultats.

**Trivy a été utilisé localement ; il n'est pas encore intégré au workflow
CI décrit ci-dessous.**

## Pipeline d'intégration continue

Le workflow `.github/workflows/ci.yml` est configuré pour s'exécuter :

- Lors d'un push sur `main`.
- Lors d'une pull request.
- Sur déclenchement manuel.

Il contient quatre jobs de contrôle et un job de synthèse :

| Job | Contrôles |
|---|---|
| `secrets-scan` | Installation de Gitleaks avec vérification SHA-256 et analyse de l'historique Git |
| `lint-test` | Ruff, formatage, tests pytest et couverture minimale de 70 % |
| `sast` | Analyse Semgrep avec sélection des résultats de sévérité ERROR |
| `docker` | Hadolint, construction, démarrage, tests HTTP et contrôles de durcissement |
| `ci-ok` | Vérification de la réussite des quatre jobs précédents |

### Analyse Semgrep

Semgrep utilise les ensembles de règles `p/default`, `p/python`,
`p/flask` et `p/dockerfile`.

La configuration actuelle utilise `--error --severity ERROR` :
les constats de sévérité ERROR provoquent un échec de l'analyse.
Les autres niveaux sont exclus du rapport produit par cette commande.

Le workflow prévoit l'envoi du rapport SARIF vers GitHub Code scanning.
La disponibilité de cette fonctionnalité et les permissions nécessaires
restent à vérifier sur le dépôt cible.

### Vérifications Docker

Le job Docker :

1. Analyse les deux Dockerfiles avec Hadolint.
2. Construit et démarre les services avec Docker Compose.
3. Attend leur disponibilité.
4. Teste la consultation et l'ajout d'un élément via HTTP.
5. Vérifie les utilisateurs non root et le mode lecture seule.
6. Vérifie la présence de l'en-tête CSP.
7. Affiche les journaux en cas d'échec.
8. Supprime les ressources temporaires du runner.

La variable `FRONTEND_BIND_IP` permet d'utiliser `127.0.0.1` dans la CI,
tout en conservant l'adresse du laboratoire comme valeur par défaut.

### État de validation

Le workflow a passé actionlint localement avec un **code de sortie 0**.

Cette validation vérifie statiquement le workflow ; elle ne prouve pas
que les actions, téléchargements, permissions et services fonctionneront
sur GitHub.

Le pipeline a été exécuté avec succès sur GitHub Actions :
les cinq jobs ont réussi, pour une durée totale observée de 44 secondes.

## Gestion des dépendances

Dependabot est configuré pour proposer des mises à jour hebdomadaires :

- Des dépendances Python de l'API.
- De l'image de base du Dockerfile API.
- De l'image de base du Dockerfile frontend.
- Des actions GitHub utilisées dans le workflow.

Les mises à jour sont proposées sous forme de pull requests.
Aucune fusion automatique n'est configurée.

## Avancement

| Étape | État |
|---|---|
| Application Flask et frontend Nginx | Réalisée localement |
| Conteneurisation avec Docker Compose | Réalisée localement |
| Persistance des données SQLite | Vérifiée localement |
| Tests Python et qualité du code | Validés localement |
| Analyses et durcissement | Réalisés, avec constats HIGH ouverts sur l'API |
| Workflow CI et Dependabot | Configurés |
| Validation statique actionlint | Réussie |
| Exécution complète de la CI sur GitHub | Réussie : cinq jobs validés |
| Protection de `main` avec le contrôle obligatoire `CI OK` | À configurer |
| Démonstrations de blocage dans la CI | À réaliser |
| Déploiement Kubernetes, GitOps et observabilité | Étapes ultérieures |

## Objectif pédagogique

Cette étape du projet établit une base applicative conteneurisée,
testée et accompagnée de contrôles de sécurité.

La suite consiste à valider le pipeline sur GitHub, à protéger la branche
principale, puis à poursuivre vers le déploiement Kubernetes,
l'automatisation et l'observabilité.
