---

description: "Liste des tâches pour l'extraction et le regroupement des contacts des parents SGDF"
---

# Tasks: Extraction et Regroupement des Contacts des Parents SGDF

**Input**: Documents de conception depuis `/specs/002-extraire-contacts-parents/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-cli-et-colonnes.md`, `quickstart.md`

**Tests**: Inclus conformément au plan d'implémentation (`tests/test_extraire_contacts_parents.py`) pour valider unitairement et en intégration les 4 User Stories sans exposer de données personnelles.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`, `[US4]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Script principal** : `extraire_contacts_parents.py`
- **Tests automatisés** : `tests/test_extraire_contacts_parents.py`
- **Documentation** : `LISEZMOI.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialisation du module d'extraction et du fichier de tests dédiés

- [X] T001 Créer le squelette du module d'extraction avec ses constantes de colonnes (`EN_TETES_CONTACTS_PARENTS` : `Nom`, `Prénom`, `Téléphone portable principal`, `Téléphone portable secondaire`, `Téléphone fixe (domicile)`, `Adresse email`, `Noms des enfants`, `Unités des enfants`, `Adresse physique`, `Numéro d'adhérent`, `Remarques`) dans `extraire_contacts_parents.py`
- [X] T002 [P] Créer le squelette du module de tests unitaires et d'intégration avec un générateur de tableau HTML SGDF synthétique anonymisé dans `tests/test_extraire_contacts_parents.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modèles de données (`EnfantRattache`, `ProfilAdulteGroupe`, `ContactParent`), fonctions de normalisation du texte et lecteur HTML/XLS en lecture seule

**⚠️ CRITICAL**: Ce socle est requis par toutes les User Stories

- [X] T003 Implémenter les classes de données `EnfantRattache`, `ProfilAdulteGroupe` et `ContactParent` ainsi que les fonctions de normalisation (`normaliser_nom` en MAJUSCULES, `normaliser_prenom` avec première lettre de chaque partie en majuscule et reste en minuscules, `normaliser_unite_courte` vers `Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`, et `assembler_adresse_physique` regroupant `Ligne1`, `Ligne2`, `Ligne3`, `CodePostal Municipalite` et `Pays` si différent de `FRANCE`) dans `extraire_contacts_parents.py`
- [X] T004 Implémenter le lecteur HTML/XLS en lecture seule (`lire_tableau_export_individus`) basé sur `BeautifulSoup(..., "lxml")` qui extrait l'en-tête de 97 colonnes et les lignes de données sous forme de chaînes de caractères (préservant le `0` initial des numéros de téléphone et codes adhérents) dans `extraire_contacts_parents.py`

**Checkpoint**: Les structures de données, la normalisation et la lecture seule du fichier `ExportIndividus.xls` sont prêtes.

---

## Phase 3: User Story 1 - Extraction complète des coordonnées des parents depuis l'export SGDF (Priority: P1) 🎯 MVP

**Goal**: Extraire les représentants légaux (`RepresentantLegal1`, `RepresentantLegal2`, `RepresentantLegal3`) de tous les jeunes scouts (`Fonction.CategorieMembre == "0"`, statuts `Inscrit(e)`, `Pré-inscrit(e)` et `Invité(e)`) avec les 11 champs normalisés.

**Independent Test**: Extraire les représentants légaux d'un tableau SGDF et vérifier que seuls les jeunes (`CategorieMembre == "0"`) génèrent des entrées de parents, que les 11 champs sont peuplés et que `NOM` et `Prénom` respectent la casse imposée.

### Tests for User Story 1

- [X] T005 [P] [US1] Ajouter les tests unitaires de normalisation (`normaliser_nom`, `normaliser_prenom` avec prénoms composés, `normaliser_unite_courte`, `assembler_adresse_physique`) et d'extraction des représentants légaux 1, 2 et 3 dans `tests/test_extraire_contacts_parents.py`

### Implementation for User Story 1

- [X] T006 [US1] Implémenter l'extraction des représentants légaux (`RepresentantLegal1`, `2`, `3`) sur les lignes de jeunes (`Fonction.CategorieMembre == "0"`) avec repli de `CourrielPersonnel` vers `CourrielDédiéSGDF` et formatage de l'enfant (`Prénom` si `enfant.nom == parent.nom`, sinon `Prénom NOM`) dans `extraire_contacts_parents.py`

**Checkpoint**: L'extraction brute et normalisée des parents de jeunes (US1) est fonctionnelle et testée.

---

## Phase 4: User Story 2 - Dédoublonnage des parents et regroupement des fratries et unités (Priority: P1)

**Goal**: Dédoublonner les parents selon la clé unique `(nom, prenom)` normalisée, regrouper sans doublon tous les enfants et leurs unités courtes (triées selon la progression d'âge SGDF `Farfadets` → `Louveteaux-Jeannettes` → `Scouts-Guides` → `Pionniers-Caravelles` → `Compagnons`), et conserver la première valeur non vide pour chaque coordonnée.

**Independent Test**: Vérifier sur une fratrie multi-unités et sur l'export `ExportIndividus.xls` que chaque couple `(Nom, Prénom)` n'apparaît qu'une seule fois (134 parents uniques) avec tous ses enfants et toutes ses unités regroupés.

### Tests for User Story 2

- [X] T007 [P] [US2] Ajouter les tests de dédoublonnage sur `(Nom, Prénom)`, de fusion des coordonnées partielles et de regroupement des fratries et unités courtes dans `tests/test_extraire_contacts_parents.py`

### Implementation for User Story 2

- [X] T008 [US2] Implémenter la logique de dédoublonnage et de fusion par clé `(nom, prenom)` conservant la première coordonnée non vide et concaténant sans doublon `noms_enfants` (séparés par `, `) et `unites_enfants` (triées dans l'ordre `Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`) dans `extraire_contacts_parents.py`

**Checkpoint**: Le dédoublonnage des parents et le regroupement des fratries (US2) sont opérationnels.

---

## Phase 5: User Story 3 - Enrichissement des remarques et du numéro d'adhérent du parent (Priority: P2)

**Goal**: Enrichir chaque fiche `ContactParent` en croisant son `(Nom, Prénom)` avec les lignes adultes de l'export (`Fonction.CategorieMembre != "0"`) pour renseigner le `Numéro d'adhérent` et les `Remarques` (rôle adulte accordé selon la civilité, ex. `Parent Animateur Farfadet`, délégation éventuelle, ainsi que le statut `Pré-inscrit(e)` ou `Invité(e)` des enfants).

**Independent Test**: Vérifier que les 18 Parents Animateurs Farfadets (code `271`) et les autres parents bénévoles inscrits comme adultes dans `ExportIndividus.xls` ont bien leur numéro d'adhérent et leur rôle dans `Remarques`, et que les statuts `Pré-inscrit(e)` / `Invité(e)` y figurent.

### Tests for User Story 3

- [X] T009 [P] [US3] Ajouter les tests d'enrichissement du `Numéro d'adhérent` et de la colonne `Remarques` (rôles adultes `Parent Animateur Farfadet`, accord masculin/féminin selon `IndividuCivilite.NomCourt`, délégations et statuts d'enfants `Pré-inscrit(e)` / `Invité(e)`) dans `tests/test_extraire_contacts_parents.py`

### Implementation for User Story 3

- [X] T010 [US3] Implémenter la construction de l'index des profils adultes (`construire_index_adultes`) et l'enrichissement des fiches `ContactParent` (numéro d'adhérent, rôle adulte formaté en français, délégations et mention `Enfant <Prénom> : <Statut>` si `Inscriptions.Type != "Inscrit(e)"`, séparés par ` ; `) dans `extraire_contacts_parents.py`

**Checkpoint**: L'enrichissement des remarques et des numéros d'adhérents (US3) est complet et vérifié.

---

## Phase 6: User Story 4 - Sauvegarde triée dans l'onglet `ContactsParents` (Priority: P1)

**Goal**: Trier les parents par ordre alphabétique français (insensible aux accents en clé primaire) sur `(Nom, Prénom)`, écrire le classeur Excel `ContactsParents.xlsx` contenant les onglets `ExportIndividus` et `ContactsParents` (cellules au format texte `@`), et exposer l'interface CLI en français (`--entree`, `--sortie`).

**Independent Test**: Exécuter `python3 extraire_contacts_parents.py` et vérifier que `ContactsParents.xlsx` contient les onglets `ExportIndividus` (153 lignes) et `ContactsParents` (134 parents triés alphabétiquement sur `(Nom, Prénom)`), sans altérer `ExportIndividus.xls`.

### Tests for User Story 4

- [X] T011 [P] [US4] Ajouter les tests du tri alphabétique français (avec caractères accentués `É`, `È`, `Ç`), de la génération du classeur Excel multi-onglets (`ExportIndividus` et `ContactsParents`), de l'interface CLI (`--entree`, `--sortie`) et de l'intégrité SHA-256 de `ExportIndividus.xls` dans `tests/test_extraire_contacts_parents.py`

### Implementation for User Story 4

- [X] T012 [US4] Implémenter le tri alphabétique français (`cle_tri_parent` basée sur `unicodedata.normalize("NFD", ...)`), la génération du classeur Excel `.xlsx` (`ecrire_classeur_contacts_parents` créant les onglets `ExportIndividus` et `ContactsParents` avec format texte `@` et colonnes ajustées) et l'interface CLI `argparse` en français (`--entree`, `--sortie`) dans `extraire_contacts_parents.py`

**Checkpoint**: Toutes les User Stories (US1 à US4) sont complètes et le script `extraire_contacts_parents.py` est opérationnel de bout en bout.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation utilisateur en français, exécution réelle sur `ExportIndividus.xls` et validation qualité finale

- [X] T013 [P] Mettre à jour la documentation utilisateur en français avec les instructions d'utilisation de `extraire_contacts_parents.py`, la description des 11 colonnes de l'onglet `ContactsParents` et des exemples de commandes dans `LISEZMOI.md`
- [X] T014 Exécuter `ruff check` sur l'ensemble du dépôt (`extraire_contacts_parents.py` et `tests/`) pour vérifier la conformité PEP 8 et l'absence d'avertissement de qualité dans `extraire_contacts_parents.py`
- [X] T015 Exécuter `pytest -v` et lancer `python3 extraire_contacts_parents.py` dans l'environnement éphémère pour générer et valider `ContactsParents.xlsx` conformément à `specs/002-extraire-contacts-parents/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — démarre immédiatement (`T001`, `T002`).
- **Foundational (Phase 2)** : Dépend de la Phase 1 — met en place les structures de données (`T003`) et le lecteur HTML/XLS (`T004`).
- **User Stories (Phases 3 à 6)** : S'enchaînent de manière incrémentale dans `extraire_contacts_parents.py` et `tests/test_extraire_contacts_parents.py` :
  - **US1 (Phase 3)** : Extraction et normalisation des parents de jeunes.
  - **US2 (Phase 4)** : Dédoublonnage sur `(Nom, Prénom)` et regroupement des fratries et unités courtes.
  - **US3 (Phase 5)** : Croisement avec les fiches adultes (numéro d'adhérent + rôle dans `Remarques`) et statuts `Pré-inscrit(e)` / `Invité(e)`.
  - **US4 (Phase 6)** : Tri alphabétique français, écriture du classeur `ContactsParents.xlsx` (`ExportIndividus` + `ContactsParents`) et CLI.
- **Polish (Phase 7)** : Dépend des Phases 3 à 6 (`T013` à `T015`).

### Parallel Opportunities

- `T001` (`extraire_contacts_parents.py`) et `T002` (`tests/test_extraire_contacts_parents.py`) peuvent être exécutées en parallèle.
- Dans chaque phase User Story, l'écriture des tests dans `tests/test_extraire_contacts_parents.py` (`T005`, `T007`, `T009`, `T011`) porte sur un fichier distinct du script principal `extraire_contacts_parents.py` (`T006`, `T008`, `T010`, `T012`).
- `T013` (`LISEZMOI.md`) peut être exécutée en parallèle des vérifications finales.

---

## Parallel Example: User Story 1

```bash
# Écriture en parallèle du test et de l'implémentation sur deux fichiers distincts :
Tâche T005 [P] [US1]: "Ajouter les tests unitaires de normalisation et d'extraction dans tests/test_extraire_contacts_parents.py"
Tâche T006 [US1]: "Implémenter l'extraction des représentants légaux dans extraire_contacts_parents.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 4)

1. Compléter Phase 1 (Setup) et Phase 2 (Foundational)
2. Compléter Phase 3 (US1 : Extraction) et Phase 4 (US2 : Dédoublonnage fratries/unités)
3. Ajouter Phase 5 (US3 : Enrichissement rôles adultes et remarques) et Phase 6 (US4 : Tri + sauvegarde `ContactsParents.xlsx`)
4. **STOP et VALIDATION** : Exécuter `pytest -v`, `ruff check .` et vérifier `ContactsParents.xlsx`.
