# Spécification Fonctionnelle : Génération du Fichier d'Import Google Contacts (`ContactParents.vcf`)

**Feature Branch**: `003-generer-contacts-vcf`

**Created**: 2026-10-16

**Status**: Draft

**Input**: Description utilisateur : "Écris un script responsable de créer un fichier que je pourrai importer dans Google Contacts. Le fichier doit contenir toute la liste des parents avec leurs numéros de téléphone, leur adresse email, et leur adresse physique. Les informations complémentaires contiendront la liste des enfants avec leurs unités, ainsi que le numéro d'adhérent (s'il existe) et d'éventuelles remarques. Enfin, tous les parents doivent avoir les étiquettes "SGDF" et "La Rochelle". Le fichier de sortie doit s'appeler "ContactParents.vcf"."

## Clarifications

### Session 2026-10-16

- Q: Quel fichier source le script doit-il utiliser en entrée pour générer `ContactParents.vcf` ? (FR-001) → A: Lire uniquement `ContactsParents.xlsx` (onglet `ContactsParents`) et exiger son existence préalable.
- Q: Comment les informations complémentaires (enfants et unités, numéro d'adhérent, remarques) doivent-elles être structurées dans la note de chaque contact ? (FR-007) → A: Une ligne par rubrique non vide : `Enfants : Prénom NOM (Unité), ...` / `Numéro d'adhérent : ...` / `Remarques : ...`.
- Q: Quel format d'affichage du nom complet du parent souhaitez-vous voir apparaître dans Google Contacts ? (FR-003) → A: `Prénom NOM` (ex. `Jean-Pierre DUPONT`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exportation complète des parents et de leurs coordonnées vers `ContactParents.vcf` (Priority: P1)

Un responsable ou secrétaire du groupe scout SGDF de La Rochelle souhaite importer en une seule opération l'ensemble des parents des jeunes du groupe dans Google Contacts. À partir de la liste consolidée des parents présente dans l'onglet `ContactsParents` du classeur `ContactsParents.xlsx`, il lance l'outil de génération et obtient un fichier nommé `ContactParents.vcf` directement importable dans Google Contacts. Chaque fiche contact créée contient l'identité du parent (nom et prénom), tous ses numéros de téléphone renseignés (portable principal, portable secondaire, fixe domicile), son adresse courriel et son adresse postale complète.

**Why this priority**: Il s'agit du besoin fondamental permettant d'alimenter Google Contacts sans saisie manuelle fiche par fiche pour les familles du groupe scout.

**Independent Test**: Peut être testé indépendamment en exécutant la génération sur la liste des parents de référence, en vérifiant que le fichier `ContactParents.vcf` est créé sans modifier le fichier d'entrée et qu'il contient exactement une fiche par parent avec ses téléphones, son adresse courriel et son adresse physique.

**Acceptance Scenarios**:

1. **Given** la liste consolidée des parents contenant leurs coordonnées, **When** l'utilisateur exécute la génération du fichier de contacts, **Then** un fichier nommé `ContactParents.vcf` est créé et contient une fiche de contact distincte pour chacun des parents de la liste.
2. **Given** un parent disposant d'un téléphone portable principal, d'un téléphone portable secondaire, d'un téléphone fixe, d'une adresse email et d'une adresse physique, **When** sa fiche est générée dans `ContactParents.vcf`, **Then** chacun de ces numéros de téléphone est présent avec sa qualification (mobile ou domicile), accompagné de son adresse courriel et de son adresse postale complète.
3. **Given** un parent pour lequel certaines coordonnées sont absentes (par exemple pas de téléphone secondaire, pas de téléphone fixe ou pas d'adresse courriel), **When** sa fiche est générée dans `ContactParents.vcf`, **Then** seules les coordonnées effectivement renseignées sont incluses, sans champs vides ni valeurs fictives.
4. **Given** le fichier source utilisé en entrée, **When** la génération de `ContactParents.vcf` se termine, **Then** le fichier source demeure strictement intact (lecture seule).

---

### User Story 2 - Inclusion des informations complémentaires (enfants et unités, numéro d'adhérent, remarques) (Priority: P1)

Lorsqu'un responsable consulte la fiche d'un parent dans Google Contacts (sur téléphone ou sur ordinateur), il souhaite voir immédiatement dans les informations complémentaires (champ note de la fiche contact) la liste des enfants rattachés à ce parent avec leurs unités respectives (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`), ainsi que le numéro d'adhérent du parent (uniquement s'il en possède un) et les éventuelles remarques (rôle au sein du groupe comme `Parent Animateur Farfadet`, ou statut d'inscription particulier d'un enfant comme `Pré-inscrit(e)` ou `Invité(e)`).

**Why this priority**: Permet d'identifier instantanément de quel(s) jeune(s) et de quelle(s) unité(s) une personne est parent lors d'un appel téléphonique, d'un message ou de la constitution des groupes WhatsApp d'unités.

**Independent Test**: Peut être testé en inspectant les fiches générées dans `ContactParents.vcf` pour un parent ayant un ou plusieurs enfants, un numéro d'adhérent et/ou des remarques, et en vérifiant que le champ d'informations complémentaires regroupe lisiblement ces trois éléments (et omet le numéro d'adhérent ou les remarques lorsqu'ils sont absents).

**Acceptance Scenarios**:

1. **Given** un parent rattaché à un ou plusieurs enfants avec leurs unités courtes respectives, **When** sa fiche est écrite dans `ContactParents.vcf`, **Then** les informations complémentaires de la fiche mentionnent explicitement chaque enfant associé à son unité (par exemple `Lucas BERNARD (Louveteaux-Jeannettes), Chloé BERNARD (Farfadets)`).
2. **Given** un parent possédant un numéro d'adhérent renseigné, **When** sa fiche est écrite dans `ContactParents.vcf`, **Then** son numéro d'adhérent figure clairement dans les informations complémentaires de la fiche ; à l'inverse, si le parent n'a pas de numéro d'adhérent, aucune mention vide de numéro d'adhérent n'est affichée.
3. **Given** un parent disposant de remarques non vides (rôle adulte dans le groupe et/ou statut `Pré-inscrit(e)` ou `Invité(e)` d'un enfant), **When** sa fiche est écrite dans `ContactParents.vcf`, **Then** ces remarques figurent dans les informations complémentaires de la fiche ; si aucune remarque n'existe pour ce parent, aucune ligne de remarque vide n'est ajoutée.

---

### User Story 3 - Attribution automatique des étiquettes `"SGDF"` et `"La Rochelle"` à tous les parents (Priority: P1)

Afin de retrouver, filtrer et gérer facilement les contacts du groupe scout au milieu d'un carnet d'adresses Google Contacts pouvant contenir d'autres contacts personnels ou professionnels, le responsable souhaite que tous les parents importés depuis `ContactParents.vcf` portent systématiquement les deux étiquettes `"SGDF"` et `"La Rochelle"`.

**Why this priority**: Indispensable pour regrouper et isoler les contacts de parents du groupe scout dans Google Contacts dès l'importation.

**Independent Test**: Peut être testé en vérifiant que 100 % des fiches présentes dans `ContactParents.vcf` comportent les deux étiquettes `"SGDF"` et `"La Rochelle"` et qu'elles sont reconnues lors de l'importation dans Google Contacts.

**Acceptance Scenarios**:

1. **Given** n'importe quel parent de la liste, **When** sa fiche est générée dans `ContactParents.vcf`, **Then** elle inclut systématiquement les deux étiquettes `"SGDF"` et `"La Rochelle"`.
2. **Given** le fichier `ContactParents.vcf` importé dans Google Contacts, **When** l'utilisateur filtre ses contacts par étiquette/libellé, **Then** tous les parents importés apparaissent sous les étiquettes `"SGDF"` et `"La Rochelle"`.

---

### Edge Cases

- **Parent avec plusieurs enfants dans des unités différentes** : Chaque enfant listé dans `Noms des enfants` est associé dans le même ordre à son unité correspondante issue de `Unités des enfants` afin que le lien entre chaque enfant et son unité reste explicite dans les informations complémentaires.
- **Numéro d'adhérent ou remarques absents** : La majorité des parents n'ayant ni numéro d'adhérent personnel ni remarque particulière, les informations complémentaires ne doivent contenir que les rubriques effectivement renseignées (toujours les enfants et leurs unités, puis le numéro d'adhérent uniquement s'il existe, puis les remarques uniquement si elles existent).
- **Caractères spéciaux, accents et retours à la ligne** : Les caractères accentués français (`é`, `è`, `ê`, `ç`, `œ`, etc.), les virgules, les points-virgules et les sauts de ligne à l'intérieur des adresses postales ou des informations complémentaires doivent être correctement préservés et échappés pour ne jamais tronquer un champ lors de l'importation dans Google Contacts.
- **Coordonnées téléphoniques multiples** : Lorsqu'un parent possède à la fois un portable principal, un portable secondaire et un fixe domicile, les trois numéros sont conservés sur la même fiche contact sans écrasement mutuel, avec le portable principal marqué comme numéro préféré.
- **Fichier d'entrée manquant ou invalide** : Si le fichier source n'existe pas ou ne contient pas les colonnes attendues, l'outil affiche un message d'erreur explicite en français et s'arrête proprement avec un code de sortie non nul sans créer de fichier `ContactParents.vcf` corrompu ou partiel.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT lire en lecture seule les données des parents uniquement à partir de l'onglet `ContactsParents` du classeur Excel `ContactsParents.xlsx` (ou tout chemin `.xlsx` équivalent fourni en argument) et exiger son existence préalable, sans jamais modifier ni altérer le fichier d'entrée.
- **FR-002**: Le système DOIT générer en sortie un fichier au format standard de carnet d'adresses vCard (`.vcf`) compatible avec l'importation Google Contacts, nommé par défaut `ContactParents.vcf` (ou selon le chemin de sortie spécifié en ligne de commande).
- **FR-003**: Pour chaque parent, la fiche générée dans `ContactParents.vcf` DOIT renseigner l'identité complète du parent à partir de son `Nom` (en MAJUSCULES) et de son `Prénom` (en Casse Titre) dans les composantes structurées du nom et afficher le nom complet sous la forme `Prénom NOM` (ex. `Jean-Pierre DUPONT`).
- **FR-004**: Pour chaque parent, la fiche générée DOIT inclure tous les numéros de téléphone non vides parmi :
  1. Le **téléphone portable principal** (qualifié comme téléphone mobile principal / préféré),
  2. Le **téléphone portable secondaire** (qualifié comme téléphone mobile secondaire),
  3. Le **téléphone fixe (domicile)** (qualifié comme téléphone de domicile).
- **FR-005**: Pour chaque parent disposant d'une adresse courriel renseignée, la fiche générée DOIT inclure cette **adresse email**.
- **FR-006**: Pour chaque parent disposant d'une adresse postale renseignée, la fiche générée DOIT inclure cette **adresse physique** complète.
- **FR-007**: Pour chaque parent, le champ d'**informations complémentaires** (note de la fiche contact) DOIT être structuré à raison d'une ligne par rubrique non vide dans l'ordre suivant :
  1. `Enfants : <Prénom NOM (Unité), ...>` associant chaque enfant de la colonne `Noms des enfants` à son unité correspondante de la colonne `Unités des enfants`,
  2. `Numéro d'adhérent : <numéro>` uniquement si le numéro d'adhérent du parent est renseigné,
  3. `Remarques : <remarques>` uniquement si des remarques sont renseignées.
- **FR-008**: Chaque fiche de parent générée dans `ContactParents.vcf` DOIT comporter les deux étiquettes (catégories/libellés) exactes `"SGDF"` et `"La Rochelle"`.
- **FR-009**: Le fichier `ContactParents.vcf` généré DOIT être encodé en UTF-8 et respecter les règles d'échappement des caractères spéciaux (virgules, points-virgules, retours à la ligne) afin de garantir un affichage intègre des accents français et des notes multi-lignes dans Google Contacts.
- **FR-010**: Conformément à la constitution du projet (Principes I, III et IV), l'outil, ses paramètres, ses messages d'exécution ou d'erreur et sa documentation DOIVENT être rédigés intégralement en français, et les fichiers `.vcf` générés contenant des données personnelles DOIVENT être exclus du suivi de version du projet.

### Key Entities

- **Fiche Contact Parent (`ContactParent` / entrée vCard)** : Représentation d'un parent destinée à Google Contacts, comprenant son identité (`Nom`, `Prénom`), ses numéros de téléphone (portable principal, portable secondaire, fixe domicile), son adresse courriel, son adresse postale, sa note d'informations complémentaires et ses étiquettes (`"SGDF"`, `"La Rochelle"`).
- **Informations Complémentaires (Note de contact)** : Bloc de texte structuré rattaché à la fiche d'un parent, regroupant la liste des enfants associés à leurs unités respectives, le numéro d'adhérent éventuel du parent et les remarques éventuelles.
- **Étiquettes de Contact (`"SGDF"`, `"La Rochelle"`)** : Marqueurs de catégorisation appliqués uniformément à l'ensemble des parents exportés afin de les regrouper sous ces libellés dans Google Contacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des parents présents dans la liste source (soit les 134 parents uniques de l'export de référence) sont exportés dans le fichier `ContactParents.vcf` dans le même ordre alphabétique `(Nom, Prénom)` sans aucune perte ni doublon.
- **SC-002**: 100 % des coordonnées non vides de chaque parent (téléphone portable principal, téléphone portable secondaire, téléphone fixe, adresse email, adresse physique) sont présentes et rattachées au bon type de champ dans `ContactParents.vcf`.
- **SC-003**: 100 % des fiches de `ContactParents.vcf` contiennent dans leurs informations complémentaires la liste complète des enfants du parent avec leurs unités, 100 % des numéros d'adhérent existants y figurent (sans mention superflue lorsqu'il est absent), et 100 % des remarques existantes y sont reportées.
- **SC-004**: 100 % des fiches de `ContactParents.vcf` possèdent exactement les deux étiquettes `"SGDF"` et `"La Rochelle"`.
- **SC-005**: Le fichier `ContactParents.vcf` est généré en moins de 5 secondes pour un groupe scout standard (< 500 fiches), est directement importable dans Google Contacts sans erreur de format ni corruption des caractères accentués français, et laisse les fichiers d'entrée strictement intacts.

## Assumptions

- Le fichier d'entrée par défaut est exclusivement `ContactsParents.xlsx` (onglet `ContactsParents`), dont l'existence préalable est requise (avec la possibilité de fournir en paramètre un autre chemin vers un classeur `.xlsx` possédant l'onglet `ContactsParents`).
- Le fichier de sortie par défaut se nomme exactement `ContactParents.vcf` à la racine du projet (avec possibilité de surcharger le chemin de sortie en paramètre).
- Dans les informations complémentaires de chaque fiche contact, chaque enfant de la colonne `Noms des enfants` est associé par position à son unité correspondante de la colonne `Unités des enfants` sous la forme `Prénom NOM (Unité)` (par exemple `Enfants : Lucas BERNARD (Louveteaux-Jeannettes), Chloé BERNARD (Farfadets)`), suivi sur des lignes distinctes de `Numéro d'adhérent : <numéro>` (si présent) et de `Remarques : <remarques>` (si présentes).
- Le standard vCard 3.0 (UTF-8) est retenu comme format cible du fichier `.vcf`, car il est nativement pris en charge par l'outil d'importation de Google Contacts pour les numéros de téléphone multiples, l'adresse courriel, l'adresse postale, les informations complémentaires et les étiquettes (`"SGDF"` et `"La Rochelle"`).
