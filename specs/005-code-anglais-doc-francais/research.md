# Recherche et Décisions Techniques (Phase 0) : Code en Anglais, Commentaires en Français et Renommage en `README.md`

## Décision 1 : Noms en anglais des fichiers Python (scripts et tests) et des options CLI

- **Decision**:
  - Renommer les scripts principaux à la racine :
    - `extraire_contacts_parents.py` → `extract_parent_contacts.py`
    - `generer_contacts_vcf.py` → `generate_contacts_vcf.py`
  - Renommer les modules de tests sous `tests/` :
    - `tests/test_environnement.py` → `tests/test_environment.py`
    - `tests/test_extraire_contacts_parents.py` → `tests/test_extract_parent_contacts.py`
    - `tests/test_generer_contacts_vcf.py` → `tests/test_generate_contacts_vcf.py`
  - Remplacer les options CLI `-e` / `--entree` et `-s` / `--sortie` par `-i` / `--input` et `-o` / `--output` (les attributs `argparse.Namespace` deviennent `args.input` et `args.output`), tout en maintenant les textes `description` et `help` d'`argparse` en français.
- **Rationale**:
  En Python, le nom du fichier `.py` est également l'identifiant du module lors des instructions `import` (ex. `import extract_parent_contacts`, `import generate_contacts_vcf`). Utiliser des noms de fichiers et d'options CLI en anglais élimine tout mélange français/anglais dans le code et les tests.
- **Alternatives considered**:
  - Conserver les noms de fichiers `.py` en français et ne traduire que les symboles internes : rejeté lors de la clarification car cela laissait des identifiants de modules en français dans toutes les importations Python.

## Décision 2 : Identifiants dans les fichiers d'environnement (`.envrc`, `flake.nix`, `devbox.json`)

- **Decision**:
  - Dans `.envrc` :
    - Variable d'environnement de sélection : `ENV_TOOL` (au lieu de `OUTIL_ENVIRONNEMENT`), stockée localement dans `selected_tool` (au lieu de `outil_choisi`).
    - Fonctions shell : `activate_flake` et `activate_devbox` (au lieu de `activer_option_flake` et `activer_option_devbox`).
    - Tous les commentaires `# ...` et messages `echo "..."` restent en français.
  - Dans `flake.nix` :
    - Variables locales Nix : `supportedSystems`, `forEachSystem`, `system`, `pythonEnv`, `pythonPackages` (au lieu de `systemesSupportes`, `pourChaqueSysteme`, `systeme`, `environnementPython`, `paquetsPython`).
    - La `description`, les commentaires `# ...` et le message d'accueil `shellHook` restent en français.
  - Dans `devbox.json` :
    - Noms des scripts : `check_environment`, `test`, `check_quality` (au lieu de `verifier_environnement`, `tester`, `verifier_qualite`).
    - Les messages `init_hook` et le message affiché par `check_environment` restent en français.
- **Rationale**:
  Assure une cohérence totale avec la règle « tout le code en anglais, les commentaires et messages en français » sur l'ensemble du dépôt et dans `tests/test_environment.py`.
- **Alternatives considered**:
  - Ne toucher qu'aux fichiers `.py` : rejeté lors de la clarification pour éviter des incohérences entre les scripts et les tests d'environnement.

## Décision 3 : Frontière stricte entre identifiants de code (en anglais) et chaînes métiers / messages utilisateur (en français)

- **Decision**:
  - **En anglais** : tous les noms de constantes, classes, attributs, méthodes, fonctions, paramètres et variables locales (ex. `DEFAULT_INPUT_FILE`, `DEFAULT_OUTPUT_FILE`, `SOURCE_SHEET_NAME`, `PARENTS_SHEET_NAME`, `PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `ContactExtractionError`, `AttachedChild`, `AdultGroupProfile`, `ParentContact`, `VcfGenerationError`, `ParentContactCard`, etc.).
  - **En français** :
    - Tous les commentaires (`# ...`) et toutes les docstrings (`"""..."""`) de modules, classes, méthodes et fonctions.
    - Toutes les chaînes métiers lues ou écrites dans les fichiers (`ExportIndividus.xls`, `ContactsParents.xlsx`, `ContactParents.vcf`, onglets `ExportIndividus` et `ContactsParents`, les 13 en-têtes `Nom`, `Prénom`, ..., `Remarques`, les libellés de rôles adultes comme `Parent Animateur Farfadet`, les notes vCard `Enfants :`, `Numéro d'adhérent :`, `Remarques :`, et les étiquettes `"SGDF"`, `"La Rochelle"`).
    - Tous les messages CLI (`--help` et messages sur `stdout` / `stderr`).
- **Rationale**:
  Garantit 0 régression fonctionnelle sur les fichiers générés pour les bénévoles du groupe SGDF de La Rochelle tout en respectant intégralement le Principe I de la constitution v2.0.0.
- **Alternatives considered**:
  - Traduire aussi les en-têtes Excel ou les messages d'erreur en anglais : rejeté car contraire à la constitution v2.0.0 et aux contrats métiers des fonctionnalités 002, 003 et 004.

## Décision 4 : Renommage de `LISEZMOI.md` en `README.md`

- **Decision**:
  Renommer `LISEZMOI.md` en `README.md` (et supprimer `LISEZMOI.md`), conserver l'intégralité de son texte en français et mettre à jour toutes les références aux commandes :
  - `ENV_TOOL` à la place de `OUTIL_ENVIRONNEMENT`,
  - `extract_parent_contacts.py` (options `--input` / `--output`) à la place de `extraire_contacts_parents.py` (`--entree` / `--sortie`),
  - `generate_contacts_vcf.py` (options `--input` / `--output`) à la place de `generer_contacts_vcf.py` (`--entree` / `--sortie`).
- **Rationale**:
  Répond directement à la demande explicite de l'utilisateur et aux conventions standards des dépôts Git tout en gardant la documentation en français.
- **Alternatives considered**:
  - Conserver un lien symbolique `LISEZMOI.md` : inutile et contraire à la demande explicite de renommer `LISEZMOI.md` en `README.md`.
