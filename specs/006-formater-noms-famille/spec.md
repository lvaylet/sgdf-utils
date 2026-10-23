# Feature Specification: Formatage des Noms de Famille en Casse Titre Comme les Prénoms

**Feature Branch**: `006-formater-noms-famille`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "Je préfère formater les noms de famille en minuscules, avec la première lettre de chaque mot en minuscules, comme les prénoms."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Formatage des noms de famille des parents et des enfants comme les prénoms lors de l'extraction (Priority: P1)

Un responsable ou secrétaire du groupe scout SGDF de La Rochelle exécute l'extraction des contacts des parents à partir de l'export des adhérents (`ExportIndividus.xls`). Au lieu d'afficher les noms de famille intégralement en majuscules, l'outil formate tous les noms de famille selon la même règle que les prénoms : en minuscules avec la première lettre de chaque mot ou partie en majuscule (par exemple `Dupont`, `Dupont-Moretti`, `Le Goff`, `D'Artagnan`). Ce formatage s'applique aussi bien à la colonne `Nom` du parent qu'aux noms de famille des enfants dans la colonne `Noms des enfants` (affichés sous la forme `Prénom Nom`, par exemple `Lucas Bernard, Chloé Bernard`), tout en préservant à l'identique le dédoublonnage des fratries, le rapprochement avec les fiches adultes du groupe et le tri alphabétique français.

**Why this priority**: Il s'agit du besoin central exprimé par l'utilisateur pour uniformiser la présentation visuelle des noms de famille et des prénoms dès la constitution de la liste des parents dans `ContactsParents.xlsx`.

**Independent Test**: Peut être testé indépendamment en exécutant l'extraction sur un export contenant des noms simples, composés, à particule ou avec apostrophe dans différentes casses (majuscules, minuscules, mixte) et en vérifiant que l'onglet `ContactsParents` présente tous les noms de famille des parents et des enfants avec une majuscule initiale sur chaque mot et le reste en minuscules.

**Acceptance Scenarios**:

1. **Given** un fichier d'export SGDF contenant des parents et des jeunes dont les noms de famille sont saisis en majuscules, en minuscules ou en casse mixte (ex. `BERNARD`, `dupont-moretti`, `LE GOFF`, `d'artagnan`), **When** l'utilisateur génère le classeur `ContactsParents.xlsx`, **Then** la colonne `Nom` de l'onglet `ContactsParents` contient les noms de famille formatés comme les prénoms (`Bernard`, `Dupont-Moretti`, `Le Goff`, `D'Artagnan`).
2. **Given** un parent rattaché à un ou plusieurs enfants dans l'export SGDF, **When** la colonne `Noms des enfants` est renseignée dans l'onglet `ContactsParents`, **Then** le nom de chaque enfant est formaté sous la forme `Prénom Nom` avec le nom de famille suivant la même règle que le prénom (ex. `Lucas Bernard, Chloé Bernard`).
3. **Given** un parent présent sur plusieurs fiches d'enfants (fratrie) et/ou disposant d'une fiche adulte dans l'export avec des saisies de casse différentes pour son nom de famille (ex. `bernard` sur une fiche et `BERNARD` sur une autre), **When** l'extraction regroupe et enrichit les fiches, **Then** les entrées sont correctement fusionnées sous la même fiche parent (`Bernard`, `Élodie`) avec son numéro d'adhérent et ses remarques adultes.
4. **Given** l'onglet `ExportIndividus` du classeur `ContactsParents.xlsx` et le fichier source `ExportIndividus.xls`, **When** l'extraction se termine, **Then** le fichier source demeure intact et l'onglet `ExportIndividus` conserve fidèlement les données brutes d'origine.

---

### User Story 2 - Cohérence des noms de famille dans le fichier d'import Google Contacts (`ContactParents.vcf`) et la documentation (Priority: P1)

Lorsqu'un responsable génère le fichier `ContactParents.vcf` à partir de `ContactsParents.xlsx` pour l'importer dans Google Contacts, les fiches contacts produites présentent le nom de famille du parent et les noms des enfants dans ce même format homogène (nom complet du parent sous la forme `Prénom Nom` tel que `Jean-Pierre Dupont`, composantes du nom `Dupont;Jean-Pierre`, et note mentionnant `Enfants : Lucas Bernard (Scouts-Guides), Chloé Bernard (Farfadets)`). La documentation du projet reflète également cette convention de formatage.

**Why this priority**: Garantit que l'objectif final d'importation dans Google Contacts bénéficie d'un affichage homogène `Prénom Nom` sur toutes les fiches et dans les notes, et que la documentation destinée aux bénévoles décrit exactement le résultat obtenu.

**Independent Test**: Peut être testé en enchaînant l'extraction puis la génération de `ContactParents.vcf` et en vérifiant que chaque fiche contact affiche le nom du parent et ceux de ses enfants avec la première lettre de chaque mot en majuscule et le reste en minuscules, et que la documentation décrit ce format.

**Acceptance Scenarios**:

1. **Given** un classeur `ContactsParents.xlsx` généré avec les noms de famille formatés comme les prénoms, **When** l'utilisateur génère le fichier `ContactParents.vcf`, **Then** chaque fiche contact comporte le nom structuré et le nom complet affiché sous la forme `Prénom Nom` (ex. `Jean-Pierre Dupont`) ainsi que la liste des enfants sous la forme `Enfants : Prénom Nom (Unité), ...` (ex. `Enfants : Lucas Bernard (Scouts-Guides), Chloé Bernard (Farfadets)`).
2. **Given** la documentation principale du projet (`README.md`), **When** un bénévole consulte la description des colonnes de `ContactsParents` et du contenu de `ContactParents.vcf`, **Then** les explications et exemples indiquent que les noms de famille sont formatés en minuscules avec la première lettre de chaque mot en majuscule, comme les prénoms.

---

### Edge Cases

- **Noms de famille composés avec trait d'union** : Un nom composé comme `DUPONT-MORETTI` ou `martin-laval` doit avoir une majuscule au début de chaque segment séparé par un trait d'union et le reste en minuscules (`Dupont-Moretti`, `Martin-Laval`).
- **Noms de famille à plusieurs mots séparés par des espaces** : Un nom comportant un ou plusieurs espaces (ex. `LE GOFF`, `DE LA FONTAINE`) doit avoir les espaces superflus nettoyés et chaque mot formaté avec sa première lettre en majuscule et les suivantes en minuscules (`Le Goff`, `De La Fontaine`).
- **Noms de famille avec apostrophe** : Un nom comportant une apostrophe (ex. `D'ARTAGNAN`, `l'héritier`) doit avoir une majuscule avant et après l'apostrophe et le reste en minuscules (`D'Artagnan`, `L'Héritier`), exactement comme pour les prénoms.
- **Noms de famille avec caractères accentués français** : Les lettres accentuées en première position ou en milieu de mot (ex. `ÉVRARD`, `BÉLANGER`, `FRANÇOIS`) doivent conserver leurs accents en majuscule initiale comme en minuscule (`Évrard`, `Bélanger`, `François`), et le tri alphabétique français doit continuer à classer correctement les noms accentués.
- **Chaînes vides ou composées uniquement d'espaces** : Un champ nom vide ou ne contenant que des espaces blancs doit produire une chaîne vide sans erreur.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Lors de l'extraction des contacts depuis l'export SGDF, le système DOIT formater tous les noms de famille selon la même règle de casse que les prénoms : nettoyage des espaces superflus, conversion en minuscules et mise en majuscule de la première lettre de chaque mot ou segment délimité par un espace, un trait d'union (`-`) ou une apostrophe (`'`).
- **FR-002**: Ce formatage des noms de famille DOIT s'appliquer uniformément :
  1. Au nom de famille de chaque représentant légal dans la colonne `Nom` de l'onglet `ContactsParents`,
  2. Au nom de famille de chaque jeune dans la colonne `Noms des enfants` de l'onglet `ContactsParents` (affiché sous la forme `Prénom Nom`),
  3. Au nom de famille des profils adultes utilisés pour le rapprochement et l'enrichissement (numéro d'adhérent et rôles adultes dans `Remarques`) sur le couple `(Nom, Prénom)`.
- **FR-003**: Le dédoublonnage des parents sur le couple `(Nom, Prénom)` et le tri alphabétique français sur `(Nom, Prénom)` DOIVENT continuer à produire exactement le même regroupement de familles et le même ordre de classement, quelle que soit la casse d'origine dans le fichier d'export.
- **FR-004**: Dans le fichier `ContactParents.vcf` généré à partir de `ContactsParents.xlsx`, le nom structuré du parent, le nom complet affiché (`Prénom Nom`) et la rubrique des enfants dans la note (`Enfants : Prénom Nom (Unité), ...`) DOIVENT conserver et restituer ce formatage des noms de famille.
- **FR-005**: L'onglet `ExportIndividus` du classeur `ContactsParents.xlsx` DOIT continuer à reproduire les données d'origine sans modifier la casse brute issue de `ExportIndividus.xls`, et le fichier source `ExportIndividus.xls` DOIT demeurer strictement intact (lecture seule).
- **FR-006**: La documentation utilisateur (`README.md`) ainsi que les descriptions et commentaires associés DOIVENT être mis à jour en français pour refléter le formatage des noms de famille identique à celui des prénoms (ex. `Prénom Nom`, `Lucas Bernard`).

### Key Entities

- **Nom de Famille Normalisé (`Nom`)** : Nom patronymique d'un parent, d'un jeune scout ou d'un adulte du groupe, formaté en minuscules avec la première lettre de chaque mot ou partie (séparée par espace, trait d'union ou apostrophe) en majuscule, à l'identique des prénoms.
- **Fiche Parent Consolidée (`ContactsParents`)** : Entrée unique par parent dédoublonné sur `(Nom, Prénom)`, présentant désormais son `Nom` et la liste `Noms des enfants` (`Prénom Nom`) avec les noms de famille en casse titre.
- **Fiche Contact Destinée à Google Contacts (`ContactParents.vcf`)** : Fiche de contact reprenant le `Nom` et le `Prénom` du parent sous la forme `Prénom Nom` ainsi que les enfants sous la forme `Prénom Nom (Unité)`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des noms de famille des parents dans la colonne `Nom` et des enfants dans la colonne `Noms des enfants` de l'onglet `ContactsParents` sont formatés en minuscules avec la première lettre de chaque mot ou segment en majuscule (0 nom de famille restant intégralement en majuscules pour les noms de plus d'une lettre).
- **SC-002**: L'extraction sur l'export de référence `ExportIndividus.xls` continue d'extraire exactement les 134 parents uniques dédoublonnés et les 20 parents ayant le rôle `Parent Animateur Farfadet` sans aucune perte de rapprochement entre représentants légaux et fiches adultes.
- **SC-003**: 100 % des 134 fiches générées dans `ContactParents.vcf` présentent le nom complet du parent et les noms des enfants dans la note au format `Prénom Nom` (ex. `Élodie Bernard`, `Lucas Bernard (Scouts-Guides)`).
- **SC-004**: 100 % des vérifications automatisées du projet s'exécutent avec succès et les fichiers sources (`ExportIndividus.xls`) demeurent strictement intacts.

## Assumptions

- Dans la demande utilisateur (« formater les noms de famille en minuscules, avec la première lettre de chaque mot en minuscules, comme les prénoms »), la référence explicite « comme les prénoms » fait foi : il s'agit de mettre l'ensemble des lettres en minuscules à l'exception de la première lettre de chaque mot ou segment (séparé par un espace, un trait d'union ou une apostrophe) qui est mise en majuscule (casse titre identique au formatage des prénoms).
- Le changement de formatage concerne tous les noms de famille affichés dans les sorties consolidées (`Nom` du parent et `Noms des enfants` dans l'onglet `ContactsParents` de `ContactsParents.xlsx`, ainsi que l'identité du parent et la liste des enfants dans `ContactParents.vcf`).
- L'onglet `ExportIndividus` de `ContactsParents.xlsx` étant une copie fidèle des données brutes d'entrée, ses cellules ne sont pas reformatées.
