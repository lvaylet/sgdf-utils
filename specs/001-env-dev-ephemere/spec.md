# Spécification Fonctionnelle : Environnement de Développement Éphémère Double Option (Nix Flake et Devbox)

**Feature Branch**: `001-env-dev-ephemere`

**Created**: 2026-10-16

**Status**: Draft

**Input**: Description utilisateur : "Mets en place l'environnement de développement éphémère avec deux options en parallèle : `flake.nix` et `devbox.json`, tous les deux activés par `.envrc`."

## Clarifications

### Session 2026-10-16

- Q: Comment le fichier `.envrc` doit-il choisir entre `flake.nix` et `devbox.json` lors de l'entrée dans le dossier ? (FR-004) → A: Détection automatique avec priorité à `flake.nix`, repli sur `devbox.json` si Nix est absent, et bascule via la variable d'environnement `OUTIL_ENVIRONNEMENT` (`flake` ou `devbox`).
- Q: Comment les bibliothèques Python nécessaires aux scripts doivent-elles être fournies dans `flake.nix` et `devbox.json` ? (FR-002) → A: Paquets Python gérés directement par Nix/Devbox (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) prêts dès l'entrée dans le dossier sans `pip` ni `.venv`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Activation automatique de l'environnement à l'ouverture du dossier (Priority: P1)

Un bénévole du groupe SGDF de La Rochelle ouvre un terminal et se déplace dans le dossier du projet pour exécuter ou modifier les scripts d'automatisation. Sans avoir à installer manuellement Python 3 ni aucune bibliothèque sur son système hôte (ni exécuter `pip install` ou créer un `.venv`), l'environnement de travail éphémère s'active automatiquement dès l'entrée dans le répertoire grâce à `.envrc`, mettant immédiatement à disposition l'interpréteur Python 3 et les paquets nécessaires au traitement des fichiers du groupe. Lorsqu'il quitte le dossier, son système hôte retrouve son état initial sans résidu.

**Why this priority**: Il s'agit du besoin fondamental permettant d'utiliser le projet sans friction ni configuration manuelle préalable sur la machine du bénévole, conformément au Principe II de la constitution.

**Independent Test**: Peut être testé de bout en bout en entrant dans le répertoire du projet depuis un terminal disposant d'un gestionnaire d'environnement autorisé, puis en vérifiant que l'environnement Python 3 isolé et ses paquets sont immédiatement accessibles et qu'ils disparaissent de l'environnement actif dès la sortie du répertoire.

**Acceptance Scenarios**:

1. **Given** un bénévole dont le poste dispose de `direnv` autorisé sur le dossier et d'au moins l'un des deux gestionnaires supportés, **When** il entre dans le dossier du projet, **Then** l'environnement éphémère est chargé automatiquement et l'interpréteur Python 3 isolé ainsi que les bibliothèques requises sont immédiatement utilisables sans étape `pip` ni `.venv`.
2. **Given** un bénévole se trouvant dans le dossier du projet avec l'environnement éphémère actif, **When** il quitte le dossier pour revenir au répertoire parent, **Then** l'environnement éphémère est déchargé automatiquement et le système hôte ne conserve aucune modification de ses variables d'environnement globales.

---

### User Story 2 - Utilisation de l'option Nix Flake (`flake.nix`) (Priority: P1)

Un bénévole utilisant un poste équipé de Nix (avec les fonctionnalités modernes et les flakes activés) souhaite disposer d'un environnement de travail strictement reproductible défini par `flake.nix`. En activant cette option via `.envrc` (ou directement), il obtient un environnement complet comprenant Python 3 et l'ensemble des dépendances nécessaires aux scripts SGDF (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`).

**Why this priority**: Première des deux options parallèles exigées par la demande utilisateur et la constitution du projet ; elle garantit une reproductibilité déterministe pour les utilisateurs de l'écosystème Nix.

**Independent Test**: Peut être testé indépendamment en sélectionnant le mode `flake.nix` dans l'activation `.envrc` (ou sur une machine ne disposant que de Nix), puis en vérifiant la disponibilité de Python 3, des outils `pytest`/`ruff` et l'importation réussie des paquets requis.

**Acceptance Scenarios**:

1. **Given** une machine disposant de Nix avec `flakes` et `nix-command` activés, **When** l'environnement est chargé via la définition `flake.nix` déclenchée par `.envrc`, **Then** Python 3 et tous les paquets déclarés (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) sont accessibles dans la session courante sans erreur.
2. **Given** l'environnement `flake.nix` actif, **When** l'utilisateur vérifie l'origine de l'interpréteur Python 3, **Then** celui-ci provient exclusivement de l'environnement éphémère isolé et non de l'installation globale du système hôte.

---

### User Story 3 - Utilisation de l'option Jetify Devbox (`devbox.json`) (Priority: P1)

Un bénévole utilisant Jetify Devbox sur son poste souhaite bénéficier d'un environnement de travail équivalent défini par `devbox.json`. En activant cette option via `.envrc` (ou directement), il obtient exactement les mêmes capacités (Python 3 et paquets `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) que celles fournies par l'option `flake.nix`.

**Why this priority**: Seconde des deux options parallèles exigées par la demande utilisateur ; elle offre une alternative ergonomique de premier plan tout en assurant une parité fonctionnelle totale.

**Independent Test**: Peut être testé indépendamment en sélectionnant le mode `devbox.json` dans l'activation `.envrc` (ou sur une machine utilisant Devbox), puis en vérifiant la disponibilité de Python 3, des outils `pytest`/`ruff` et l'importation réussie des mêmes paquets requis.

**Acceptance Scenarios**:

1. **Given** une machine disposant de Jetify Devbox, **When** l'environnement est chargé via la définition `devbox.json` déclenchée par `.envrc`, **Then** Python 3 et tous les paquets déclarés (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) sont accessibles dans la session courante sans erreur.
2. **Given** les deux définitions `flake.nix` et `devbox.json` présentes dans le dépôt, **When** on compare les capacités fournies par chacune des deux options, **Then** les deux environnements fournissent la même version majeure/mineure de Python 3 et le même ensemble fonctionnel de paquets requis pour les scripts du groupe SGDF.

---

### User Story 4 - Coexistence harmonieuse et bascule simple dans `.envrc` (Priority: P2)

Un bénévole dont la machine dispose à la fois de Nix et de Devbox (ou qui passe d'une machine à une autre n'ayant qu'un seul des deux outils) souhaite que le fichier `.envrc` gère les deux options en parallèle sans conflit, en activant automatiquement `flake.nix` par défaut (ou `devbox.json` en repli si Nix est absent) tout en permettant de basculer facilement vers l'autre option via la variable `OUTIL_ENVIRONNEMENT`.

**Why this priority**: Assure que les deux options parallèles (`flake.nix` et `devbox.json`) ne se neutralisent pas mutuellement lorsqu'elles sont toutes deux présentes et référencées par `.envrc`.

**Independent Test**: Peut être testé en vérifiant le chargement automatique par défaut via `.envrc`, puis en basculant sur l'option alternative via `OUTIL_ENVIRONNEMENT=devbox` (ou `flake`) et en constatant que chaque mode s'active proprement sans conflit de variables d'environnement.

**Acceptance Scenarios**:

1. **Given** un poste où Nix et Devbox sont tous deux installés, **When** `.envrc` est exécuté à l'entrée du dossier sans configuration supplémentaire, **Then** l'option `flake.nix` est activée proprement par défaut sans double chargement conflictuel, et un message en français indique clairement quel mode d'environnement est actif.
2. **Given** un poste où seul Devbox (ou seul Nix) est installé, **When** `.envrc` est exécuté à l'entrée du dossier, **Then** `.envrc` détecte et active automatiquement l'option correspondant à l'outil disponible sur la machine.
3. **Given** un poste où Nix et Devbox sont tous deux installés, **When** l'utilisateur définit explicitement `OUTIL_ENVIRONNEMENT=devbox` (ou `OUTIL_ENVIRONNEMENT=flake`), **Then** `.envrc` active l'option demandée et affiche une confirmation en français.

---

### Edge Cases

- **Absence d'autorisation initiale de `direnv`** : Lorsque le bénévole entre pour la première fois dans le dossier avant d'avoir exécuté `direnv allow`, l'environnement ne s'exécute pas silencieusement ; la documentation en français explique clairement l'unique commande d'autorisation initiale à lancer.
- **Absence simultanée de Nix et de Devbox sur le poste** : Si ni Nix ni Devbox ne sont présents sur la machine hôte lorsque `.envrc` est évalué, un message d'erreur explicite en français est affiché pour indiquer les prérequis manquants sans bloquer le terminal de l'utilisateur.
- **Bascule entre les deux options dans une même session** : Lorsqu'un utilisateur change l'option active via `OUTIL_ENVIRONNEMENT` (de `flake` vers `devbox` ou inversement) et recharge `direnv`, l'ancien environnement est nettoyé avant l'activation du nouveau afin d'éviter toute collision de chemins d'exécution (`PATH` ou `PYTHONPATH`).
- **Protection des fichiers de données locales** : L'initialisation ou l'utilisation de l'environnement éphémère (création éventuelle de dossiers techniques locaux comme `.direnv/` ou `.devbox/`) ne modifie jamais les fichiers d'export SGDF présents dans le répertoire (tels que `ExportIndividus.xls`) et les artefacts techniques locaux sont exclus du suivi de version.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le dépôt DOIT contenir deux définitions d'environnement éphémère maintenues en parallèle à la racine du projet : `flake.nix` (pour Nix Flakes) et `devbox.json` (pour Jetify Devbox).
- **FR-002**: Les deux définitions (`flake.nix` et `devbox.json`) DOIVENT fournir directement via Nix/Devbox (sans recourir à `pip` ni à un `.venv` séparé) un environnement fonctionnellement équivalent comprenant Python 3 ainsi que les paquets Python et outils suivants : `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl` (pour la lecture/écriture des exports SGDF `.xls`/HTML et `.xlsx`), ainsi que `pytest` et `ruff` (pour les tests et la qualité du code).
- **FR-003**: Le fichier `.envrc` à la racine du projet DOIT prendre en charge l'activation automatique par `direnv` des deux options (`flake.nix` et `devbox.json`) dès l'entrée dans le dossier.
- **FR-004**: Le mécanisme d'activation dans `.envrc` DOIT détecter automatiquement les outils disponibles en donnant la priorité par défaut à `flake.nix`, basculer automatiquement en repli sur `devbox.json` si seul Devbox est installé, et permettre à l'utilisateur de forcer le choix de l'option via la variable d'environnement `OUTIL_ENVIRONNEMENT` (`flake` ou `devbox`).
- **FR-005**: Lors de l'activation de l'environnement (ou en cas d'erreur de prérequis), les messages d'information et de diagnostic affichés à l'utilisateur ainsi que l'ensemble des commentaires et de la documentation associée DOIVENT être rédigés intégralement en français, conformément au Principe I de la constitution.
- **FR-006**: Les répertoires et fichiers techniques générés localement par l'activation de l'environnement (caches locaux de `direnv` et `devbox`) ainsi que les fichiers de données personnelles du groupe scout DOIVENT être exclus du suivi de version pour préserver la propreté du dépôt et la confidentialité des familles (Principe IV).
- **FR-007**: Le projet DOIT inclure une documentation concise en français permettant à tout bénévole de comprendre le fonctionnement des deux options (`flake.nix` et `devbox.json`), la manière d'autoriser `.envrc` et la façon de basculer d'une option à l'autre via `OUTIL_ENVIRONNEMENT`.

### Key Entities

- **Définition d'environnement Nix (`flake.nix` et son fichier de verrouillage)** : Déclaration reproductible de l'environnement de développement basée sur Nix Flakes, fournissant directement Python 3, les bibliothèques `pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, les outils `pytest` et `ruff`, et le comportement d'accueil du shell en français.
- **Définition d'environnement Devbox (`devbox.json` et son fichier de verrouillage)** : Déclaration équivalente de l'environnement de développement pour Jetify Devbox, fournissant la même pile Python 3 et les mêmes paquets que `flake.nix` avec des scripts d'initialisation en français.
- **Script d'activation automatique (`.envrc`)** : Point d'entrée évalué par `direnv` à chaque entrée dans le dossier, orchestrant le chargement de l'environnement via `flake.nix` (par défaut) ou `devbox.json` (en repli ou via `OUTIL_ENVIRONNEMENT=devbox`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un bénévole disposant des prérequis (`direnv` + Nix ou Devbox) obtient un environnement Python 3 opérationnel en 0 étape d'installation manuelle de paquets (`pip` ou `.venv`) après l'autorisation initiale du dossier (`direnv allow`).
- **SC-002**: 100 % des paquets Python et outils requis (`pandas`, `beautifulsoup4`, `lxml`, `xlrd`, `openpyxl`, `pytest`, `ruff`) pour manipuler et vérifier le traitement des exports du groupe SGDF (y compris `ExportIndividus.xls` au format HTML/XLS) sont disponibles et importables sans erreur aussi bien via l'option `flake.nix` que via l'option `devbox.json`.
- **SC-003**: 100 % des commentaires, messages d'accueil/erreur de l'environnement et documentations d'utilisation créés pour cette fonctionnalité sont rédigés en langue française.
- **SC-004**: La sortie du répertoire du projet restaure intégralement l'environnement initial du terminal de l'utilisateur (0 paquet ou variable spécifique au projet persistant hors du dossier).

## Assumptions

- La machine de développement dispose déjà de `direnv` installé et intégré au shell de l'utilisateur, ainsi que d'au moins l'un des deux gestionnaires : Nix (avec `flakes` et `nix-command` activés) ou Jetify Devbox.
- Lorsque Nix et Devbox sont tous deux présents sur la machine hôte et qu'aucune préférence explicite n'est indiquée par l'utilisateur, `.envrc` active par défaut `flake.nix` tout en permettant de basculer immédiatement sur `devbox.json` via la variable d'environnement `OUTIL_ENVIRONNEMENT=devbox` (ou via un fichier `.envrc.local` chargé s'il existe).
- Le fichier `ExportIndividus.xls` issu de l'intranet SGDF étant un document HTML portant l'extension `.xls`, l'inclusion conjointe de `pandas`, `beautifulsoup4`, `lxml`, `xlrd` et `openpyxl` directement dans Nix et Devbox couvre à la fois les exports HTML-XLS, les anciens classeurs Excel `.xls` et les classeurs modernes `.xlsx`.
