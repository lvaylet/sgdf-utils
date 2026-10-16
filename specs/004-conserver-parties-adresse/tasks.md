---

description: "Liste des tâches pour la conservation des parties brutes de l'adresse de bout en bout"
---

# Tasks: Conservation des Parties Brutes de l'Adresse de Bout en Bout

**Input**: Documents de conception depuis `/specs/004-conserver-parties-adresse/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-colonnes-et-vcard.md`, `quickstart.md`

**Tests**: Inclus conformément au plan d'implémentation (`tests/test_extraire_contacts_parents.py` et `tests/test_generer_contacts_vcf.py`) pour valider unitairement et de bout en bout les 3 User Stories sans exposer de données personnelles.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Script d'extraction Excel** : `extraire_contacts_parents.py`
- **Script de génération vCard** : `generer_contacts_vcf.py`
- **Tests automatisés** : `tests/test_extraire_contacts_parents.py`, `tests/test_generer_contacts_vcf.py`
- **Documentation** : `LISEZMOI.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Alignement des constantes d'en-têtes de l'onglet `ContactsParents` sur le nouveau schéma à 13 colonnes (`Rue`, `Code postal`, `Ville`)

- [X] T001 Mettre à jour la constante `EN_TETES_CONTACTS_PARENTS` avec les 13 colonnes (`"Rue"`, `"Code postal"`, `"Ville"` en remplacement de `"Adresse physique"`) dans `extraire_contacts_parents.py`
- [X] T002 [P] Mettre à jour la constante `EN_TETES_CONTACTS_PARENTS` avec les 13 colonnes (`"Rue"`, `"Code postal"`, `"Ville"` en remplacement de `"Adresse physique"`) dans `generer_contacts_vcf.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mise à jour des modèles de données (`ProfilAdulteGroupe`, `ContactParent`, `FicheContactParent`) pour porter séparément `rue`, `code_postal` et `ville`

**⚠️ CRITICAL**: Ce socle est requis par toutes les User Stories

- [X] T003 Mettre à jour les classes de données `ProfilAdulteGroupe` (contraintes de `data-model.md` : `"Regroupement des valeurs non vides de Individu.Adresse.Ligne1, Ligne2 et Ligne3 séparées par , ."` pour `rue`, `"Valeur brute nettoyée de Individu.Adresse.CodePostal."` pour `code_postal`, `"Valeur brute nettoyée de Individu.Adresse.Municipalite."` pour `ville`) et `ContactParent` (contraintes de `data-model.md` : `"Lignes Adresse.Ligne1..3 non vides jointes par , . Conservé avec code_postal et ville comme premier bloc d'adresse non vide."` pour `rue`, `"Valeur brute nettoyée de Adresse.CodePostal. Conservé au sein du premier bloc d'adresse non vide."` pour `code_postal`, `"Valeur brute nettoyée de Adresse.Municipalite. Conservé au sein du premier bloc d'adresse non vide."` pour `ville`) dans `extraire_contacts_parents.py`
- [X] T004 [P] Mettre à jour la classe de données `FicheContactParent` en remplaçant `adresse_physique` par `rue`, `code_postal` et `ville` (contraintes de `data-model.md` : `"Affectation directe (échappée RFC 2426) sans découpage."` pour `rue`, `"Affectation directe (échappée RFC 2426)."` pour `code_postal` et `ville`) dans `generer_contacts_vcf.py`

**Checkpoint**: Les structures de données portent désormais les 3 composantes `rue`, `code_postal` et `ville` dans les deux scripts.

---

## Phase 3: User Story 1 - Conservation des composantes d'adresse séparées (`Rue`, `Code postal`, `Ville`) dans l'onglet `ContactsParents` (Priority: P1) 🎯 MVP

**Goal**: Extraire et conserver séparément `Rue` (`Ligne1..3`), `Code postal` et `Ville` (en omettant `Pays`), les fusionner comme un bloc indissociable lors du dédoublonnage, et écrire les 13 colonnes dans l'onglet `ContactsParents` de `ContactsParents.xlsx`.

**Independent Test**: Exécuter l'extraction sur un export SGDF et vérifier que l'onglet `ContactsParents` contient les 13 colonnes avec `Rue`, `Code postal` et `Ville` correctement renseignés et fusionnés sans modifier le fichier source.

### Tests for User Story 1

- [X] T005 [P] [US1] Mettre à jour les tests unitaires et d'intégration d'extraction (`assembler_rue`, fusion atomique du premier bloc `(rue, code_postal, ville)` non vide et vérification des 13 colonnes de l'onglet `ContactsParents`) dans `tests/test_extraire_contacts_parents.py`

### Implementation for User Story 1

- [X] T006 [US1] Remplacer `assembler_adresse_physique` par `assembler_rue(ligne1, ligne2, ligne3)` et adapter `construire_index_adultes`, `extraire_et_regrouper_parents`, `ContactParent.fusionner_coordonnees` et `ContactParent.vers_ligne_excel` pour extraire, fusionner d'un seul tenant et sérialiser `rue`, `code_postal` et `ville` (en omettant `Adresse.Pays`) dans `extraire_contacts_parents.py`

**Checkpoint**: L'extraction vers `ContactsParents.xlsx` avec les 3 colonnes d'adresse (`Rue`, `Code postal`, `Ville`) est fonctionnelle et testable indépendamment (`pytest tests/test_extraire_contacts_parents.py`).

---

## Phase 4: User Story 2 - Génération directe de l'adresse structurée dans `ContactParents.vcf` sans redécoupage (Priority: P1)

**Goal**: Supprimer toute logique de redécoupage d'adresse (`decomposer_adresse_postale`) et alimenter directement le champ `ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;` à partir des colonnes `Rue`, `Ville` et `Code postal` de l'onglet `ContactsParents`.

**Independent Test**: Générer un bloc vCard ou un fichier `.vcf` à partir de fiches dotées de `rue`, `code_postal` et `ville` (y compris avec des virgules dans `rue` ou des champs vides) et vérifier l'affectation directe 1 pour 1 dans `ADR`.

### Tests for User Story 2

- [X] T007 [P] [US2] Mettre à jour les tests unitaires de génération vCard (suppression des tests de `decomposer_adresse_postale`, vérification de l'affectation directe de `rue`, `ville` et `code_postal` dans `ADR;TYPE=HOME`, préservation des virgules dans `rue`, et omission de `ADR` lorsque les 3 champs sont vides) dans `tests/test_generer_contacts_vcf.py`

### Implementation for User Story 2

- [X] T008 [US2] Supprimer `decomposer_adresse_postale` et adapter `lire_contacts_parents_excel` et `formater_vcard_parent` pour lire les 13 colonnes et construire directement `ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;` (uniquement si au moins l'un des 3 champs est non vide) dans `generer_contacts_vcf.py`

**Checkpoint**: La génération directe du champ `ADR` sans redécoupage (US2) est opérationnelle et vérifiée unitairement.

---

## Phase 5: User Story 3 - Continuité de bout en bout du traitement des contacts des parents (Priority: P2)

**Goal**: Garantir l'enchaînement complet sans régression entre `extraire_contacts_parents.py` (`ExportIndividus.xls` → `ContactsParents.xlsx` à 13 colonnes) et `generer_contacts_vcf.py` (`ContactsParents.xlsx` → `ContactParents.vcf` avec 134 fiches).

**Independent Test**: Exécuter successivement l'extraction et la génération `.vcf` sur l'export de référence et vérifier que 100 % des tests d'intégration passent sur les 134 parents.

### Tests for User Story 3

- [X] T009 [P] [US3] Mettre à jour les tests CLI et d'intégration de bout en bout (classeurs synthétiques à 13 colonnes et vérification de non-régression sur `ContactsParents.xlsx` réel) dans `tests/test_generer_contacts_vcf.py`

### Implementation for User Story 3

- [X] T010 [US3] Exécuter la chaîne complète (`extraire_contacts_parents.py` puis `generer_contacts_vcf.py`) pour régénérer `ContactsParents.xlsx` (13 colonnes) et `ContactParents.vcf` (134 fiches) à partir de `ExportIndividus.xls`

**Checkpoint**: Le flux complet de bout en bout (US1 + US2 + US3) est opérationnel et vérifié.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mise à jour de la documentation utilisateur en français et validation qualité finale

- [X] T011 [P] Mettre à jour la liste des 13 colonnes de l'onglet `ContactsParents` (`Rue`, `Code postal`, `Ville`) et la description de l'adresse dans `LISEZMOI.md`
- [X] T012 Exécuter `ruff check .` et `pytest -v` pour valider la conformité PEP 8 et le passage de 100 % des tests conformément à `specs/004-conserver-parties-adresse/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — démarre immédiatement (`T001`, `T002` en parallèle).
- **Foundational (Phase 2)** : Dépend de la Phase 1 — met à jour les dataclasses dans `extraire_contacts_parents.py` (`T003`) et `generer_contacts_vcf.py` (`T004`).
- **User Story 1 (Phase 3 - P1)** : Dépend de la Phase 2 — implémente et teste l'extraction des 3 colonnes `Rue`, `Code postal`, `Ville` dans `extraire_contacts_parents.py` (`T005`, `T006`).
- **User Story 2 (Phase 4 - P1)** : Dépend de la Phase 2 — implémente et teste l'affectation directe `ADR` sans redécoupage dans `generer_contacts_vcf.py` (`T007`, `T008`). Peut être réalisée en parallèle de US1.
- **User Story 3 (Phase 5 - P2)** : Dépend de US1 (Phase 3) et US2 (Phase 4) — valide l'enchaînement complet de bout en bout (`T009`, `T010`).
- **Polish (Phase 6)** : Dépend des Phases 3 à 5 (`T011`, `T012`).

### Parallel Opportunities

- `T001` (`extraire_contacts_parents.py`) et `T002` (`generer_contacts_vcf.py`) portent sur deux fichiers distincts.
- `T003` (`extraire_contacts_parents.py`) et `T004` (`generer_contacts_vcf.py`) portent sur deux fichiers distincts.
- La Phase 3 (US1 sur `extraire_contacts_parents.py` / `tests/test_extraire_contacts_parents.py`) et la Phase 4 (US2 sur `generer_contacts_vcf.py` / `tests/test_generer_contacts_vcf.py`) portent sur des fichiers disjoints et peuvent être menées en parallèle.

---

## Parallel Example: User Story 1 & User Story 2

```bash
# Exécution en parallèle des mises à jour d'extraction (US1) et de génération vCard (US2) :
Task: "T006 [US1] Adapter l'extraction vers Rue, Code postal, Ville dans extraire_contacts_parents.py"
Task: "T008 [US2] Supprimer decomposer_adresse_postale et affecter directement ADR dans generer_contacts_vcf.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Compléter Phase 1 (`T001`, `T002`) et Phase 2 (`T003`, `T004`)
2. Compléter Phase 3 (`T005`, `T006` — US1 : extraction des 3 colonnes `Rue`, `Code postal`, `Ville` dans `ContactsParents.xlsx`)
3. **STOP et VALIDATION** : Vérifier `pytest tests/test_extraire_contacts_parents.py`

### Incremental Delivery

1. Ajouter Phase 4 (`T007`, `T008` — US2 : génération directe `ADR` dans `generer_contacts_vcf.py`)
2. Ajouter Phase 5 (`T009`, `T010` — US3 : continuité de bout en bout sur les fichiers réels)
3. Compléter Phase 6 (`T011`, `T012` — documentation `LISEZMOI.md`, `ruff check .` et `pytest -v`)
