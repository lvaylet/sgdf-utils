# Spécification Fonctionnelle : Code en Anglais, Commentaires en Français et Renommage en `README.md`

**Feature Branch**: `005-code-anglais-doc-francais`

**Created**: 2026-10-16

**Status**: Draft

**Input**: Description utilisateur : "Modifie la constitution pour que tout le code, y compris les noms des variables et les noms des fonctions soient en anglais. Le reste de la base de code, par exemple les commentaires ou le fichier README.md, doit rester en français. D'ailleurs, renomme LISEZMOI.md en README.md."

## Clarifications

### Session 2026-10-16

- Q: Faut-il également renommer en anglais les fichiers Python (par exemple `extract_parent_contacts.py`, `generate_contacts_vcf.py` et leurs fichiers `tests/test_*.py`) ainsi que les options en ligne de commande (`--input` et `--output` au lieu de `--entree` et `--sortie`) ? (FR-003) → A: Tout en anglais : renommer les fichiers `.py` (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) et les options CLI (`--input`, `--output`) en anglais.
- Q: Les identifiants présents dans les fichiers de configuration de l'environnement (`.envrc`, `flake.nix` et `devbox.json` : par exemple la variable `OUTIL_ENVIRONNEMENT`, les fonctions shell, les variables Nix et les noms de scripts Devbox) doivent-ils également passer en anglais ou rester tels quels ? (FR-003) → A: Tout le code en anglais, y compris les identifiants dans `.envrc` (`ENV_TOOL`, `activate_flake`, `activate_devbox`), `flake.nix` (`supportedSystems`, `forEachSystem`, `pythonEnv`) et `devbox.json` (`check_environment`, `test`, `check_quality`), avec commentaires et messages `echo` en français.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Renommage de `LISEZMOI.md` en `README.md` avec contenu en français (Priority: P1)

Un bénévole ou un responsable du groupe scout SGDF de La Rochelle qui ouvre le dépôt du projet (localement ou sur une plateforme d'hébergement de code) accède immédiatement au fichier standard `README.md` à la racine du projet. L'ancien fichier `LISEZMOI.md` n'existe plus, et l'intégralité du texte explicatif de `README.md` demeure rédigée en français tout en reflétant les commandes, variables et noms de fichiers à jour (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, options `--input` et `--output`, variable `ENV_TOOL`).

**Why this priority**: Permet la reconnaissance automatique de la documentation d'accueil par l'ensemble des outils standards et des plateformes d'hébergement tout en conservant une documentation 100 % en français pour les bénévoles.

**Independent Test**: Peut être testé indépendamment en vérifiant la présence de `README.md` à la racine du dépôt, l'absence de `LISEZMOI.md`, la rédaction intégrale en français de `README.md` et l'exactitude des commandes qui y sont documentées.

**Acceptance Scenarios**:

1. **Given** le dépôt du projet contenant auparavant `LISEZMOI.md`, **When** la mise en conformité est appliquée, **Then** le fichier `LISEZMOI.md` est renommé en `README.md` à la racine du projet et `LISEZMOI.md` n'existe plus.
2. **Given** le fichier `README.md` renommé, **When** un bénévole le consulte, **Then** toutes les explications, rubriques et instructions d'utilisation sont rédigées en français et mentionnent les noms exacts des scripts (`extract_parent_contacts.py`, `generate_contacts_vcf.py`), options (`--input`, `--output`) et variables (`ENV_TOOL`) en vigueur.

---

### User Story 2 - Passage en anglais de l'ensemble du code et de ses identifiants tout en conservant les commentaires en français (Priority: P1)

Un bénévole ou mainteneur qui inspecte ou modifie les scripts d'automatisation, les fichiers de configuration de l'environnement (`.envrc`, `flake.nix`, `devbox.json`) et la suite de vérification constate que l'intégralité du code (noms des fichiers `.py` de scripts et de tests, des variables, des fonctions, des méthodes, des classes, des constantes, des paramètres, des options CLI `--input` / `--output`, de la variable d'environnement `ENV_TOOL`, des variables Nix et des scripts Devbox) est rédigée en anglais, tandis que tous les commentaires explicatifs dans le code, les textes de documentation interne et les messages affichés à l'utilisateur restent en français.

**Why this priority**: Aligne la base de code sur le Principe I de la constitution v2.0.0 du projet (code en anglais, commentaires et documentation en français).

**Independent Test**: Peut être testé en inspectant l'ensemble des fichiers de code, d'environnement et de tests du dépôt pour vérifier qu'aucun identifiant (nom de fichier `.py`, variable, fonction, classe, constante, paramètre, option CLI, identifiant shell/Nix/Devbox) ne subsiste en français et que tous les commentaires et textes de documentation interne sont rédigés en français.

**Acceptance Scenarios**:

1. **Given** n'importe quel fichier de code, de configuration d'environnement ou de test du projet, **When** on examine son nom de fichier et ses identifiants (variables, fonctions, méthodes, classes, constantes, paramètres, options CLI `--input` / `--output`, identifiants dans `.envrc`, `flake.nix` et `devbox.json`), **Then** 100 % de ces identifiants sont rédigés en anglais et les anciens fichiers `.py` en français n'existent plus.
2. **Given** n'importe quel fichier de code, de test ou de configuration d'environnement du projet, **When** on examine ses commentaires et sa documentation interne, **Then** 100 % des commentaires et descriptions sont rédigés en français.
3. **Given** les outils en ligne de commande du projet (`extract_parent_contacts.py` et `generate_contacts_vcf.py`) ainsi que les messages d'activation de l'environnement, **When** l'utilisateur affiche l'aide (`--help`), active l'environnement ou déclenche une erreur d'utilisation, **Then** les messages d'aide, d'accueil et d'erreur affichés à l'écran restent rédigés en français.

---

### User Story 3 - Continuité fonctionnelle de bout en bout sans régression métier (Priority: P1)

Un responsable du groupe SGDF de La Rochelle exécute le flux complet d'extraction des contacts des parents à partir de `ExportIndividus.xls` vers `ContactsParents.xlsx`, puis de génération du fichier `ContactParents.vcf` destiné à Google Contacts. Les fichiers produits, les en-têtes de colonnes, le dédoublonnage, le tri alphabétique français et le formatage des fiches contacts demeurent strictement identiques à l'existant.

**Why this priority**: Garantit que la mise en conformité linguistique du code ne modifie aucun résultat métier attendu par le groupe scout ni l'intégrité des fichiers traités.

**Independent Test**: Peut être testé de bout en bout en exécutant `extract_parent_contacts.py` sur `ExportIndividus.xls` puis `generate_contacts_vcf.py` pour produire `ContactParents.vcf` et en vérifiant que les 134 fiches parents et les 13 colonnes de `ContactsParents.xlsx` sont produites à l'identique sans altérer le fichier d'entrée.

**Acceptance Scenarios**:

1. **Given** le fichier de référence `ExportIndividus.xls`, **When** `extract_parent_contacts.py` puis `generate_contacts_vcf.py` sont exécutés, **Then** le classeur `ContactsParents.xlsx` (avec ses onglets `ExportIndividus` et `ContactsParents` à 13 colonnes en français) et le fichier `ContactParents.vcf` (contenant les 134 parents avec leurs adresses, notes en français et étiquettes `"SGDF"` et `"La Rochelle"`) sont générés sans aucune régression.
2. **Given** la suite de tests automatisés et le vérificateur de qualité du projet, **When** ils sont exécutés dans l'environnement éphémère, **Then** 100 % des tests réussissent et aucune erreur de qualité ou de style n'est signalée.

---

### Edge Cases

- **Distinction entre identifiants de code et données métiers en français** : Les valeurs métiers issues de l'export SGDF ou produites dans les fichiers de sortie (noms des colonnes Excel comme `Nom`, `Prénom`, `Téléphone portable principal`, `Rue`, `Code postal`, `Ville`, libellés de fonctions comme `Parent Animateur Farfadet`, rubriques de notes comme `Enfants :`, `Numéro d'adhérent :`, `Remarques :`, noms d'onglets `ExportIndividus` et `ContactsParents`) sont des données/libellés métiers destinés aux utilisateurs finaux et DOIVENT rester en français, tandis que les constantes ou variables qui les portent dans le code DOIVENT être nommées en anglais.
- **Arguments en ligne de commande et variables d'environnement** : Les options en ligne de commande (`--input`, `--output`), la variable d'environnement `ENV_TOOL` dans `.envrc` et les scripts Devbox (`check_environment`, `test`, `check_quality`) doivent être cohérents entre le code, les fichiers d'environnement, les tests et le fichier `README.md` afin qu'aucune commande documentée ne soit caduque.
- **Références croisées entre modules et tests** : Le renommage des fonctions, classes, constantes et modules (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) en anglais ne doit laisser aucune importation ni aucun appel cassé ni aucun ancien fichier `.py` en français dans le dépôt.
- **Lecture seule des fichiers sources** : Le fichier d'entrée `ExportIndividus.xls` ne doit subir aucune modification lors de l'exécution des scripts ou des tests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le fichier de documentation principal à la racine du dépôt DOIT être renommé de `LISEZMOI.md` en `README.md`, et l'ancien fichier `LISEZMOI.md` DOIT être supprimé.
- **FR-002**: Le contenu du fichier `README.md` DOIT demeurer intégralement rédigé en français et être mis à jour pour refléter fidèlement les noms en anglais des scripts (`extract_parent_contacts.py`, `generate_contacts_vcf.py`), options (`--input`, `--output`), variables d'environnement (`ENV_TOOL`) et commandes du projet.
- **FR-003**: Dans l'ensemble des fichiers de code source, de configuration d'environnement et de tests du projet, tous les identifiants de code DOIVENT être rédigés en anglais :
  - les fichiers Python sont renommés en anglais (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) et les anciens fichiers `.py` en français sont supprimés,
  - les options en ligne de commande des scripts utilisent `--input` et `--output` (en remplacement de `--entree` et `--sortie`),
  - la totalité des classes, fonctions, méthodes, variables, constantes et paramètres à l'intérieur des fichiers de code et de tests utilise des noms en anglais,
  - les identifiants dans `.envrc` (`ENV_TOOL`, `selected_tool`, `activate_flake`, `activate_devbox`), `flake.nix` (`supportedSystems`, `forEachSystem`, `pythonEnv`, `pythonPackages`) et `devbox.json` (scripts `check_environment`, `test`, `check_quality`) utilisent des noms en anglais.
- **FR-004**: Dans l'ensemble des fichiers du projet (code source, tests, fichiers d'environnement `.envrc` et `flake.nix`), tous les commentaires explicatifs et toutes les chaînes de documentation interne DOIVENT rester rédigés en français.
- **FR-005**: Tous les messages destinés à l'utilisateur final en ligne de commande (descriptions d'aide `--help`, messages d'avancement, messages d'erreur sur les fichiers ou colonnes, messages d'accueil `echo` de l'environnement) DOIVENT rester rédigés en français.
- **FR-006**: Les données et contrats métiers produits en sortie (noms par défaut des fichiers `ExportIndividus.xls`, `ContactsParents.xlsx` et `ContactParents.vcf`, noms des onglets `ExportIndividus` et `ContactsParents`, en-têtes des 13 colonnes en français, libellés des fonctions adultes SGDF, contenu des notes vCard en français et étiquettes `"SGDF"` et `"La Rochelle"`) DOIVENT demeurer strictement inchangés.
- **FR-007**: L'intégralité de la suite de tests automatisés DOIT être mise à jour avec des identifiants de tests, de fonctions auxiliaires, de constantes et de variables en anglais (tout en conservant ses commentaires et descriptions en français) et s'exécuter avec 100 % de réussite sans aucune erreur de vérification de style.

### Key Entities

- **Documentation Principale (`README.md`)** : Point d'entrée documentaire du dépôt à la racine du projet, portant un nom standard en anglais (`README.md`) et un contenu explicatif rédigé en français.
- **Identifiants du Code Source et de l'Environnement** : Ensemble des symboles techniques du code (noms des fichiers de scripts et de tests `.py`, options CLI `--input`/`--output`, classes, fonctions, méthodes, constantes, paramètres, variables locales et identifiants dans `.envrc`, `flake.nix`, `devbox.json`), désormais tous nommés en anglais.
- **Commentaires et Messages Utilisateur** : Ensemble des commentaires de code, blocs de documentation interne et messages d'interface en ligne de commande, maintenus intégralement en français.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Le fichier `README.md` est présent à la racine du projet, `LISEZMOI.md` est absent, et 100 % des sections et explications de `README.md` sont rédigées en français avec des exemples de commandes fonctionnels.
- **SC-002**: 100 % des identifiants du code source, de la configuration d'environnement et des tests (fichiers de scripts et de tests `.py`, options CLI `--input`/`--output`, classes, fonctions, méthodes, constantes, paramètres, variables et identifiants `.envrc`/`flake.nix`/`devbox.json`) sont rédigés en anglais (0 identifiant ni fichier `.py` en français restant dans le code).
- **SC-003**: 100 % des commentaires de code, des textes de documentation interne et des messages affichés à l'utilisateur sont rédigés en français.
- **SC-004**: 100 % des tests automatisés de la suite de vérification s'exécutent avec succès et le contrôleur de qualité du code rapporte 0 anomalie.
- **SC-005**: L'exécution de bout en bout sur `ExportIndividus.xls` produit exactement les 134 parents dédoublonnés dans `ContactsParents.xlsx` (13 colonnes en français) et les 134 fiches contacts dans `ContactParents.vcf` sans modifier le fichier source.

## Assumptions

- Les fichiers de scripts et de tests (`extract_parent_contacts.py`, `generate_contacts_vcf.py`, `tests/test_environment.py`, `tests/test_extract_parent_contacts.py`, `tests/test_generate_contacts_vcf.py`) ainsi que les identifiants dans les fichiers de configuration d'environnement (`.envrc`, `flake.nix` et `devbox.json`) font partie du code et voient leurs identifiants nommés en anglais, tandis que leurs commentaires et messages affichés à l'écran restent en français.
- Les noms des fichiers de données métiers (`ExportIndividus.xls`, `ContactsParents.xlsx`, `ContactParents.vcf`), les noms des onglets (`ExportIndividus`, `ContactsParents`) et les 13 en-têtes de colonnes de l'onglet `ContactsParents` font partie du contrat métier utilisateur et restent inchangés.
- Les options en ligne de commande des scripts Python adoptent des identifiants standards en anglais (`--input` / `--output`) avec des descriptions d'aide en français, et sont documentées comme telles dans `README.md`.
