---

description: "Liste des tâches pour la génération du fichier d'import Google Contacts (ContactParents.vcf)"
---

# Tasks: Génération du Fichier d'Import Google Contacts (`ContactParents.vcf`)

**Input**: Documents de conception depuis `/specs/003-generer-contacts-vcf/`

**Prerequisites**: `plan.md` (requis), `spec.md` (requis pour les récits utilisateurs), `research.md`, `data-model.md`, `contracts/contrat-cli-et-vcard.md`, `quickstart.md`

**Tests**: Inclus conformément au plan d'implémentation (`tests/test_generer_contacts_vcf.py`) pour valider unitairement et en intégration les 3 User Stories sans exposer de données personnelles.

**Organization**: Les tâches sont organisées par récit utilisateur (User Story) afin que chaque incrément puisse être implémenté et testé indépendamment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Exécutable en parallèle (fichiers distincts, aucune dépendance sur une tâche inachevée)
- **[Story]**: Récit utilisateur auquel appartient la tâche (`[US1]`, `[US2]`, `[US3]`)
- Chaque description inclut le chemin exact du fichier concerné

## Path Conventions

- **Script principal** : `generer_contacts_vcf.py`
- **Tests automatisés** : `tests/test_generer_contacts_vcf.py`
- **Exclusion Git (RGPD)** : `.gitignore`
- **Documentation** : `LISEZMOI.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Protection RGPD des fichiers `.vcf` et initialisation du module principal et du module de tests

- [X] T001 Mettre à jour les règles d'exclusion Git pour ignorer les fichiers vCard contenant des données personnelles (`*.vcf` et `ContactParents.vcf`) dans `.gitignore`
- [X] T002 [P] Créer le squelette du script avec ses constantes métier (`FICHIER_ENTREE_DEFAUT = "ContactsParents.xlsx"`, `FICHIER_SORTIE_DEFAUT = "ContactParents.vcf"`, `NOM_ONGLET_PARENTS = "ContactsParents"`, `ETIQUETTES_DEFAUT = ("SGDF", "La Rochelle")`, `EN_TETES_CONTACTS_PARENTS`) et l'exception métier `ErreurGenerationVcf` dans `generer_contacts_vcf.py`
- [X] T003 [P] Créer le squelette du module de tests unitaires et d'intégration avec un générateur de classeur Excel `ContactsParents.xlsx` synthétique anonymisé dans `tests/test_generer_contacts_vcf.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modèle de données `FicheContactParent`, échappement RFC 2426 et lecteur en lecture seule de l'onglet `ContactsParents`

**⚠️ CRITICAL**: Ce socle est requis par toutes les User Stories

- [X] T004 Implémenter la classe de données `FicheContactParent` (respectant les contraintes de `data-model.md` : `"Obligatoire (au moins nom ou prenom non vide). Conservé en MAJUSCULES."` pour `nom`, `"Conservé en Casse Titre. Nom affiché FN = f\"{prenom} {nom}\".strip()."` pour `prenom`, et `"Toujours égal à (\"SGDF\", \"La Rochelle\") pour 100 % des parents (FR-008)."` pour `etiquettes`) ainsi que la fonction d'échappement RFC 2426 (`echapper_valeur_vcard` échappant `\`, `;`, `,` et `\n`) dans `generer_contacts_vcf.py`
- [X] T005 Implémenter le lecteur Excel en lecture seule (`lire_contacts_parents_excel`) qui vérifie l'existence préalable du fichier `ContactsParents.xlsx`, la présence de l'onglet `ContactsParents`, la conformité des 11 en-têtes de colonnes et retourne la liste ordonnée des `FicheContactParent` dans `generer_contacts_vcf.py`

**Checkpoint**: La structure de données, l'échappement vCard 3.0 et la lecture seule de `ContactsParents.xlsx` sont prêts.

---

## Phase 3: User Story 1 - Exportation complète des parents et de leurs coordonnées vers `ContactParents.vcf` (Priority: P1) 🎯 MVP

**Goal**: Générer le fichier `ContactParents.vcf` à partir de l'onglet `ContactsParents` de `ContactsParents.xlsx` avec l'identité (`N`, `FN`), les numéros de téléphone non vides (`TEL`), l'adresse email (`EMAIL`) et l'adresse physique (`ADR`) de chaque parent.

**Independent Test**: Exécuter la génération sur un classeur `ContactsParents.xlsx` et vérifier que `ContactParents.vcf` est créé sans modifier le fichier source et contient une fiche vCard 3.0 par parent avec ses coordonnées non vides.

### Tests for User Story 1

- [X] T006 [P] [US1] Ajouter les tests unitaires et d'intégration de lecture de `ContactsParents.xlsx` (erreurs fichier/onglet/colonnes manquants, intégrité SHA-256 en lecture seule) et de sérialisation vCard 3.0 de l'identité (`N:NOM;Prénom;;;`, `FN:Prénom NOM`), des téléphones (`CELL,VOICE,PREF`, `CELL,VOICE`, `HOME,VOICE`), du courriel (`EMAIL;TYPE=INTERNET,HOME`) et de l'adresse postale (`ADR;TYPE=HOME`) dans `tests/test_generer_contacts_vcf.py`

### Implementation for User Story 1

- [X] T007 [US1] Implémenter la décomposition d'adresse postale (`decomposer_adresse_postale` selon la contrainte `"Inclus uniquement si non vide. Décomposé en (rue, ville, code_postal, pays) si possible, sinon placé dans <rue>."`), la sérialisation vCard 3.0 des coordonnées (`formater_vcard_parent` appliquant `"Inclus uniquement si non vide."` sur `telephone_portable_principal`, `telephone_portable_secondaire`, `telephone_fixe`, `adresse_email` et `adresse_physique`), l'écriture UTF-8 de `ContactParents.vcf` (`ecrire_fichier_vcf`) et l'interface CLI `argparse` (`--entree`, `--sortie`) dans `generer_contacts_vcf.py`

**Checkpoint**: L'exportation des parents et de leurs coordonnées dans `ContactParents.vcf` (US1) est fonctionnelle et testable indépendamment.

---

## Phase 4: User Story 2 - Inclusion des informations complémentaires (enfants et unités, numéro d'adhérent, remarques) (Priority: P1)

**Goal**: Structurer le champ `NOTE` de chaque fiche vCard à raison d'une ligne par rubrique non vide : `Enfants : Prénom NOM (Unité), ...`, puis `Numéro d'adhérent : ...` (s'il existe), puis `Remarques : ...` (si elles existent).

**Independent Test**: Vérifier sur des fiches parents avec un ou plusieurs enfants, avec ou sans numéro d'adhérent et avec ou sans remarques, que la propriété `NOTE` dans `ContactParents.vcf` contient exactement les lignes attendues sans rubrique vide.

### Tests for User Story 2

- [X] T008 [P] [US2] Ajouter les tests unitaires et d'intégration de formatage des enfants avec leurs unités (`Enfants : Prénom NOM (Unité), ...`), d'inclusion conditionnelle de `Numéro d'adhérent : ...` et `Remarques : ...`, et d'échappement RFC 2426 de la propriété `NOTE` dans `tests/test_generer_contacts_vcf.py`

### Implementation for User Story 2

- [X] T009 [US2] Implémenter l'association enfants/unités (`formater_enfants_et_unites` selon les contraintes `"Liste séparée par ,  associée par position à unites_enfants."` et `"Liste séparée par ,  associée par position à noms_enfants sous la forme Prénom NOM (Unité)."`) et la construction de la note multi-lignes (`construire_note_parent` respectant `"Inclus dans NOTE uniquement si non vide."` pour `numero_adherent` et `remarques`) intégrée dans `formater_vcard_parent` dans `generer_contacts_vcf.py`

**Checkpoint**: Les informations complémentaires structurées (US2) sont opérationnelles et vérifiées.

---

## Phase 5: User Story 3 - Attribution automatique des étiquettes `"SGDF"` et `"La Rochelle"` à tous les parents (Priority: P1)

**Goal**: Attribuer systématiquement les deux étiquettes `"SGDF"` et `"La Rochelle"` (`CATEGORIES:SGDF,La Rochelle`) à 100 % des fiches de parents générées dans `ContactParents.vcf`.

**Independent Test**: Vérifier que chacune des 134 fiches générées dans `ContactParents.vcf` comporte la ligne `CATEGORIES:SGDF,La Rochelle`.

### Tests for User Story 3

- [X] T010 [P] [US3] Ajouter les tests unitaires et d'intégration vérifiant la présence systématique de `CATEGORIES:SGDF,La Rochelle` sur 100 % des fiches générées dans `tests/test_generer_contacts_vcf.py`

### Implementation for User Story 3

- [X] T011 [US3] Implémenter l'émission systématique de la propriété `CATEGORIES:SGDF,La Rochelle` (selon la contrainte `"Toujours égal à (\"SGDF\", \"La Rochelle\") pour 100 % des parents (FR-008)."`) dans `formater_vcard_parent` dans `generer_contacts_vcf.py`

**Checkpoint**: Toutes les User Stories (US1, US2, US3) sont complètes et vérifiées.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation utilisateur en français, exécution réelle sur `ContactsParents.xlsx` et validation qualité finale

- [X] T012 [P] Mettre à jour la documentation utilisateur en français avec la présentation de `generer_contacts_vcf.py`, les commandes d'exécution et les instructions d'importation de `ContactParents.vcf` dans Google Contacts dans `LISEZMOI.md`
- [X] T013 Exécuter `ruff check .` sur l'ensemble du dépôt pour vérifier la conformité PEP 8 et l'absence d'avertissement de qualité dans `generer_contacts_vcf.py` et `tests/test_generer_contacts_vcf.py`
- [X] T014 Exécuter `pytest -v` et lancer `python3 generer_contacts_vcf.py` dans l'environnement éphémère pour générer et valider `ContactParents.vcf` (134 fiches) conformément à `specs/003-generer-contacts-vcf/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)** : Aucune dépendance — démarre immédiatement (`T001`, `T002`, `T003`).
- **Foundational (Phase 2)** : Dépend de la Phase 1 — met en place `FicheContactParent`, l'échappement RFC 2426 (`T004`) et le lecteur Excel en lecture seule (`T005`).
- **User Stories (Phases 3 à 5)** : S'appuient sur la Phase 2 :
  - **US1 (Phase 3)** : Exportation des fiches vCard avec identité, téléphones, email, adresse postale et CLI (`T006`, `T007`).
  - **US2 (Phase 4)** : Construction et intégration de la note structurée (`Enfants`, `Numéro d'adhérent`, `Remarques`) (`T008`, `T009`).
  - **US3 (Phase 5)** : Attribution systématique des étiquettes `"SGDF"` et `"La Rochelle"` (`CATEGORIES:SGDF,La Rochelle`) (`T010`, `T011`).
- **Polish (Phase 6)** : Dépend des Phases 3 à 5 (`T012`, `T013`, `T014`).

### Parallel Opportunities

- En Phase 1, `T001` (`.gitignore`), `T002` (`generer_contacts_vcf.py`) et `T003` (`tests/test_generer_contacts_vcf.py`) portent sur trois fichiers distincts et peuvent être exécutées en parallèle.
- Dans chaque phase User Story, les tâches de tests (`T006`, `T008`, `T010` dans `tests/test_generer_contacts_vcf.py`) portent sur un fichier distinct des tâches d'implémentation (`T007`, `T009`, `T011` dans `generer_contacts_vcf.py`).
- En Phase 6, `T012` (`LISEZMOI.md`) peut être réalisée en parallèle des vérifications de code.

---

## Parallel Example: User Story 1

```bash
# Écriture en parallèle des tests et de l'implémentation sur deux fichiers distincts :
Task: "T006 [P] [US1] Ajouter les tests unitaires et d'intégration dans tests/test_generer_contacts_vcf.py"
Task: "T007 [US1] Implémenter la sérialisation vCard 3.0 et l'interface CLI dans generer_contacts_vcf.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Compléter Phase 1 (Setup : `.gitignore`, squelettes)
2. Compléter Phase 2 (Foundational : modèle `FicheContactParent`, échappement RFC 2426, lecture `ContactsParents.xlsx`)
3. Compléter Phase 3 (US1 : génération de `ContactParents.vcf` avec identité et coordonnées)
4. **STOP et VALIDATION** : Tester US1 indépendamment

### Incremental Delivery

1. Ajouter Phase 4 (US2 : informations complémentaires structurées dans `NOTE`) → Tester
2. Ajouter Phase 5 (US3 : étiquettes `"SGDF"` et `"La Rochelle"` dans `CATEGORIES`) → Tester
3. Compléter Phase 6 (Polish : documentation `LISEZMOI.md`, `ruff check .`, `pytest -v` et génération réelle de `ContactParents.vcf`)
