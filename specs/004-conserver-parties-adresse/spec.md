# Spécification Fonctionnelle : Conservation des Parties Brutes de l'Adresse de Bout en Bout

**Feature Branch**: `004-conserver-parties-adresse`

**Created**: 2026-10-16

**Status**: Draft

**Input**: Description utilisateur : "La gestion des adresses physiques est complexe. L'adresse complète est assemblée une première fois dans l'onglet ContactsParents, sous forme d'un champ unique, avant d'être séparée à nouveau en plusieurs champs dans le fichier ContactsParents.vcf. Conserve les différentes parties brutes de l'adresse pendant l'extraction des contacts des parents et la génération du fichier .vcf pour simplifier le processus de bout en bout."

## Clarifications

### Session 2026-10-16

- Q: Comment les trois lignes d'adresse brutes (`Ligne 1`, `Ligne 2`, `Ligne 3`) issues de l'export SGDF doivent-elles être réparties dans les composantes du champ d'adresse vCard (`ADR`) du fichier `ContactParents.vcf` ? (FR-006) → A: Regrouper les valeurs non vides de `Ligne 1`, `Ligne 2` et `Ligne 3` dans le composant `<rue>` (séparées par `, `), et laisser `<boîte postale>` et `<adresse étendue>` vides.
- Q: Faut-il conserver la valeur brute du champ `Pays` (y compris lorsqu'elle vaut `FRANCE`) et de la `Municipalité` de bout en bout jusque dans `ContactParents.vcf`, ou continuer à omettre `FRANCE` ? (FR-001) → A: Omettre `FRANCE` dès l'extraction dans l'onglet `ContactsParents` (et donc aussi dans `ContactParents.vcf`).
- Q: Quelles colonnes doivent remplacer l'ancienne colonne `Adresse physique` dans l'onglet `ContactsParents` du classeur `ContactsParents.xlsx` ? (FR-002) → A: 3 colonnes sans `Pays` : `Rue` (regroupant `Ligne 1..3`), `Code postal`, `Ville`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conservation des composantes d'adresse séparées (`Rue`, `Code postal`, `Ville`) dans l'onglet `ContactsParents` (Priority: P1)

Un responsable ou secrétaire du groupe scout SGDF de La Rochelle exécute l'extraction des contacts des parents à partir de l'export `ExportIndividus.xls`. Au lieu d'assembler l'ensemble de l'adresse postale en une seule chaîne dans une colonne unique `Adresse physique`, l'outil conserve séparément dans l'onglet `ContactsParents` du classeur `ContactsParents.xlsx` les 3 composantes de l'adresse : `Rue` (regroupant les valeurs non vides de `Adresse.Ligne1`, `Adresse.Ligne2` et `Adresse.Ligne3` séparées par `, `), `Code postal` (`Adresse.CodePostal`) et `Ville` (`Adresse.Municipalite`), en omettant le pays.

**Why this priority**: Supprime l'assemblage d'une adresse complète en un champ unique lors de l'extraction et aligne directement les colonnes de l'onglet `ContactsParents` sur les composantes attendues par le fichier `.vcf`.

**Independent Test**: Peut être testé indépendamment en exécutant l'extraction sur un fichier d'export SGDF et en vérifiant que l'onglet `ContactsParents` comporte les 3 colonnes d'adresse distinctes (`Rue`, `Code postal`, `Ville`) contenant les valeurs attendues pour chaque parent, sans modifier le fichier d'entrée.

**Acceptance Scenarios**:

1. **Given** un fichier d'export SGDF contenant pour chaque représentant légal (et chaque adulte) les champs `Adresse.Ligne1`, `Adresse.Ligne2`, `Adresse.Ligne3`, `Adresse.CodePostal` et `Adresse.Municipalite`, **When** l'extraction génère l'onglet `ContactsParents`, **Then** l'adresse est enregistrée dans 3 colonnes distinctes (`Rue`, `Code postal`, `Ville`) en remplacement de l'ancienne colonne unique `Adresse physique`.
2. **Given** un parent dont seules certaines composantes de l'adresse sont renseignées dans l'export (par exemple `Ligne 1`, `Code postal` et `Municipalite` renseignés, tandis que `Ligne 2` et `Ligne 3` sont vides, ou inversement plusieurs lignes de rue renseignées), **When** sa ligne est écrite dans l'onglet `ContactsParents`, **Then** la colonne `Rue` regroupe les lignes de rue non vides séparées par `, `, et les colonnes `Code postal` et `Ville` conservent leurs valeurs brutes nettoyées des espaces superflus.
3. **Given** un parent rattaché à plusieurs enfants (fratrie) ou disposant également d'une fiche adulte dans l'export, **When** ses coordonnées sont fusionnées lors du dédoublonnage, **Then** le premier bloc d'adresse `(Rue, Code postal, Ville)` non vide disponible est conservé dans son ensemble (sans mélanger la rue d'une fiche avec la ville ou le code postal d'une autre fiche).

---

### User Story 2 - Génération directe de l'adresse structurée dans `ContactParents.vcf` sans redécoupage (Priority: P1)

Lorsqu'un responsable génère le fichier d'import Google Contacts (`ContactParents.vcf`) à partir de l'onglet `ContactsParents` du classeur `ContactsParents.xlsx`, l'outil lit directement les 3 colonnes d'adresse (`Rue`, `Code postal`, `Ville`) et renseigne directement les composantes correspondantes du champ d'adresse postale (`ADR`) dans chaque fiche contact, sans recourir à une analyse ni à un redécoupage textuel.

**Why this priority**: Élimine toute logique complexe et fragile de découpage d'adresse lors de la génération du fichier `.vcf` et garantit une correspondance directe 1 pour 1 entre les 3 colonnes d'adresse de `ContactsParents` et les sous-champs d'adresse de Google Contacts.

**Independent Test**: Peut être testé indépendamment en générant `ContactParents.vcf` à partir d'un classeur `ContactsParents.xlsx` doté des 3 colonnes `Rue`, `Code postal` et `Ville`, et en vérifiant que chaque composante du champ `ADR` de la fiche contact reflète exactement la colonne source correspondante.

**Acceptance Scenarios**:

1. **Given** une ligne de parent dans l'onglet `ContactsParents` possédant au moins une valeur non vide parmi les colonnes `Rue`, `Code postal` et `Ville`, **When** la fiche contact est générée dans `ContactParents.vcf`, **Then** le champ d'adresse postale (`ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;`) est directement construit par affectation directe de `Rue`, `Ville` et `Code postal`, sans analyse par expression régulière ni découpage sur les virgules.
2. **Given** une ligne de parent dans l'onglet `ContactsParents` dont les 3 colonnes `Rue`, `Code postal` et `Ville` sont toutes vides, **When** la fiche contact est générée dans `ContactParents.vcf`, **Then** aucun champ d'adresse postale (`ADR`) vide n'est ajouté à la fiche contact.

---

### User Story 3 - Continuité de bout en bout du traitement des contacts des parents (Priority: P2)

Un responsable du groupe SGDF de La Rochelle exécute successivement l'extraction des contacts depuis `ExportIndividus.xls` vers `ContactsParents.xlsx`, puis la génération du fichier `ContactParents.vcf` depuis `ContactsParents.xlsx`. Le processus complet fonctionne de bout en bout de manière transparente et conserve à l'identique toutes les autres fonctionnalités existantes (dédoublonnage sur `(Nom, Prénom)`, tri alphabétique français, normalisation des téléphones, regroupement des enfants et unités, numéro d'adhérent, remarques et étiquettes `"SGDF"` et `"La Rochelle"`).

**Why this priority**: Garantit que la simplification de la gestion des adresses postales s'intègre sans régression dans la chaîne complète d'automatisation utilisée par les bénévoles du groupe.

**Independent Test**: Peut être testé de bout en bout en enchaînant l'extraction à partir de `ExportIndividus.xls` puis la génération de `ContactParents.vcf` à partir du fichier `ContactsParents.xlsx` produit, et en vérifiant les 134 fiches parents obtenues.

**Acceptance Scenarios**:

1. **Given** le fichier d'export `ExportIndividus.xls` de référence, **When** l'utilisateur exécute l'extraction vers `ContactsParents.xlsx` puis la génération vers `ContactParents.vcf`, **Then** les deux étapes s'exécutent sans erreur et produisent les 134 fiches parents complètes avec leurs adresses structurées issues directement des colonnes `Rue`, `Code postal` et `Ville`.
2. **Given** un fichier `ContactsParents.xlsx` dont les en-têtes de l'onglet `ContactsParents` ne correspondent pas au schéma attendu à 13 colonnes (incluant `Rue`, `Code postal`, `Ville`), **When** l'utilisateur lance la génération du fichier `.vcf`, **Then** un message d'erreur explicite en français indique les en-têtes attendus et le traitement s'arrête proprement avec un code de sortie non nul.

---

### Edge Cases

- **Valeurs brutes contenant uniquement des espaces** : Une composante d'adresse (`Ligne 1..3`, `Code postal` ou `Municipalité`) ne contenant que des espaces blancs dans l'export source est nettoyée et considérée comme vide afin de ne pas produire de champ d'adresse constitué uniquement d'espaces.
- **Adresse partiellement renseignée** : Si un parent ne dispose que d'un code postal et d'une ville (sans rue) ou uniquement d'une rue, seules les composantes présentes sont conservées dans leurs colonnes respectives (`Rue`, `Code postal`, `Ville`) de `ContactsParents` et reportées à leurs positions exactes dans le champ `ADR` du fichier `.vcf`.
- **Adresses comportant des virgules ou points-virgules dans la rue** : Comme la colonne `Rue` n'est plus jamais redécoupée sur la virgule pour tenter d'en extraire le code postal et la ville, toute virgule présente dans `Rue` (ex. `10 Rue du Port, Bâtiment B` ou `12, rue des Mouettes`) est intégralement préservée dans le sous-champ `<rue>` sans risque de décalage avec le code postal ou la ville.
- **Fusion d'adresses lors du dédoublonnage d'une fratrie** : Si la première fiche enfant d'un parent n'a aucune composante d'adresse renseignée (`Rue`, `Code postal` et `Ville` vides) mais que la seconde fiche enfant (ou la fiche adulte du parent) possède une adresse renseignée, le système adopte l'ensemble du premier bloc `(Rue, Code postal, Ville)` non vide rencontré.
- **Caractères spéciaux dans les champs d'adresse du fichier `.vcf`** : Les caractères spéciaux éventuels présents dans chacune des 3 composantes (`Rue`, `Code postal`, `Ville`) continuent d'être échappés individuellement selon la norme vCard 3.0 lors de l'écriture dans `ContactParents.vcf`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Lors de l'extraction des contacts des parents depuis l'export SGDF (`ExportIndividus.xls`), le système DOIT extraire et conserver séparément pour chaque représentant légal et chaque profil adulte les 3 parties de l'adresse postale suivantes (en omettant le pays), toutes normalisées en minuscules avec la première lettre de chaque mot en majuscule :
  1. **Rue** : regroupement des valeurs non vides de `Adresse.Ligne1`, `Adresse.Ligne2` et `Adresse.Ligne3` (nettoyées des espaces superflus, mises en casse titre et séparées par `, `),
  2. **Code postal** : valeur de `Adresse.CodePostal` (nettoyée des espaces superflus et mise en casse titre),
  3. **Ville** : valeur de `Adresse.Municipalite` (nettoyée des espaces superflus et mise en casse titre, ex. `La Rochelle`).
- **FR-002**: Dans l'onglet `ContactsParents` du classeur `ContactsParents.xlsx`, le système DOIT remplacer l'ancienne colonne unique `Adresse physique` par 3 colonnes distinctes dans l'ordre exact suivant :
  1. `Rue`
  2. `Code postal`
  3. `Ville`
  portant le nombre total de colonnes de l'onglet `ContactsParents` à 13 (`Nom`, `Prénom`, `Téléphone portable principal`, `Téléphone portable secondaire`, `Téléphone fixe (domicile)`, `Adresse email`, `Noms des enfants`, `Unités des enfants`, `Rue`, `Code postal`, `Ville`, `Numéro d'adhérent`, `Remarques`).
- **FR-003**: Lors du dédoublonnage d'un parent (fratrie) et de l'enrichissement par sa fiche adulte éventuelle, le système DOIT traiter le triplet `(Rue, Code postal, Ville)` comme un bloc d'adresse indissociable en conservant le premier bloc dont au moins l'une des 3 composantes est non vide.
- **FR-004**: Le système d'extraction NE DOIT PLUS assembler la rue, le code postal et la ville en une seule chaîne d'adresse complète.
- **FR-005**: Lors de la génération du fichier `ContactParents.vcf`, le système DOIT lire et valider les 13 colonnes de l'onglet `ContactsParents` (incluant `Rue`, `Code postal` et `Ville`) depuis `ContactsParents.xlsx` en lecture seule.
- **FR-006**: Lors de la génération du fichier `ContactParents.vcf`, le système NE DOIT PLUS analyser ni redécouper une chaîne d'adresse unique ; il DOIT construire directement le champ d'adresse postale structuré (`ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;`) de chaque fiche contact par affectation directe :
  - la composante `<rue>` reçoit directement la valeur de la colonne `Rue`,
  - la composante `<ville>` reçoit directement la valeur de la colonne `Ville`,
  - la composante `<code_postal>` reçoit directement la valeur de la colonne `Code postal`,
  - les composantes `<boîte postale>`, `<adresse étendue>`, `<région>` et `<pays>` restent vides.
- **FR-007**: Si les 3 colonnes `Rue`, `Code postal` et `Ville` d'un parent sont toutes vides, aucun champ d'adresse postale (`ADR`) NE DOIT être écrit dans sa fiche au sein de `ContactParents.vcf`.
- **FR-008**: Conformément à la constitution du projet (Principes I, III, IV et V), l'ensemble du code, des en-têtes de colonnes, des messages d'exécution ou d'erreur, des tests et de la documentation (`LISEZMOI.md`) DOIT être rédigé intégralement en français, et les fichiers d'entrée DOIVENT demeurer strictement intacts (lecture seule).

### Key Entities

- **Adresse Postale (`Rue`, `Code postal`, `Ville`)** : Triplet cohérent issu des champs d'adresse de l'export SGDF (`Ligne1..3` regroupées dans `Rue`, `CodePostal` dans `Code postal`, `Municipalite` dans `Ville`, sans `Pays`), conservé sous forme de 3 champs distincts dans `ContactsParents.xlsx` puis injecté directement dans le champ `ADR` de `ContactParents.vcf`.
- **Fiche Parent Consolidée (`ContactParent` dans `ContactsParents.xlsx`)** : Entrée unique par parent dédoublonné sur `(Nom, Prénom)`, comportant 13 colonnes dont les 3 colonnes `Rue`, `Code postal` et `Ville`.
- **Fiche Contact vCard (`FicheContactParent` dans `ContactParents.vcf`)** : Fiche de contact destinée à Google Contacts dont le champ `ADR` est alimenté directement par les 3 colonnes `Rue`, `Code postal` et `Ville` de l'onglet `ContactsParents`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des parents extraits dans l'onglet `ContactsParents` (soit les 134 parents uniques de l'export de référence) voient leur adresse répartie dans les 3 colonnes dédiées (`Rue`, `Code postal`, `Ville`) sans concaténation de la rue avec le code postal et la ville.
- **SC-002**: 100 % des adresses postales présentes dans `ContactParents.vcf` sont générées par affectation directe 1 pour 1 des colonnes `Rue`, `Code postal` et `Ville` de l'onglet `ContactsParents` (0 étape de redécoupage par expression régulière ou séparateur).
- **SC-003**: 100 % des adresses contenant des virgules ou compléments dans la rue (ex. `10 Rue du Port, Bâtiment B`) sont restituées intégralement dans le sous-champ `<rue>` sans erreur ni décalage avec `<code_postal>` et `<ville>` dans `ContactParents.vcf`.
- **SC-004**: 100 % des fonctionnalités existantes d'extraction et de génération `.vcf` (134 parents dédoublonnés, tri alphabétique français, téléphones au format international, enfants et unités, numéro d'adhérent, remarques, étiquettes `"SGDF"` et `"La Rochelle"`, lecture seule des fichiers sources) continuent de fonctionner sans aucune régression.
- **SC-005**: La documentation utilisateur (`LISEZMOI.md`) et les suites de tests automatisés reflètent fidèlement le nouveau schéma à 13 colonnes de l'onglet `ContactsParents` et la conservation de bout en bout des parties de l'adresse.

## Assumptions

- Les 3 colonnes d'adresse dans l'onglet `ContactsParents` sont nommées `Rue`, `Code postal` et `Ville`, et remplacent la colonne `Adresse physique` entre `Unités des enfants` et `Numéro d'adhérent`.
- Le champ `Pays` (qui vaut `FRANCE` ou est vide dans les exports du groupe SGDF de La Rochelle) est omis dès l'extraction et n'apparaît ni dans `ContactsParents.xlsx` ni dans `ContactParents.vcf`.
- Dans la colonne `Rue`, lorsque plusieurs lignes d'adresse (`Adresse.Ligne1`, `Adresse.Ligne2`, `Adresse.Ligne3`) sont non vides pour un même parent, elles sont jointes dans l'ordre par `, `, puis transmises telles quelles au sous-champ `<rue>` de la propriété `ADR` dans `ContactParents.vcf`.
