# Spécification Fonctionnelle : Extraction et Regroupement des Contacts des Parents SGDF

**Feature Branch**: `002-extraire-contacts-parents`

**Created**: 2026-10-16

**Status**: Draft

**Input**: Description utilisateur : "Écris un script qui extrait les contacts des parents des jeunes scouts SGDF listés dans @ExportIndividus.xls. Cette liste de contacts servira à mettre à jour Google Contacts et préparera la gestion des groupes WhatsApp dédiés aux différentes unités. Pour chaque parent, l'idéal est d'avoir : le nom (en majuscules), le prénom (en minuscules, sauf la première lettre), le numéro de téléphone portable principal, le numéro de téléphone portable secondaire, le numéro de téléphone fixe (domicile), l'adresse email, les noms des enfants, les unités des enfants, l'adresse physique, le numéro d'adhérent, et un champ libre avec des remarques (par exemple un rôle de Parent Accompagnateur Farfadet). Le dédoublonnage des entrées, pour regrouper correctement les enfants, doit se faire sur le nom et le prénom du parent. La liste des parents sera sauvegardé dans un onglet appelé "ContactsParents". La liste des parents devra être triée alphabétiquement, d'abord sur le nom puis sur le prénom, pour regrouper visuellement les familles."

## Clarifications

### Session 2026-10-16

- Q: Dans quel fichier tableur l'onglet `"ContactsParents"` doit-il être enregistré ? (FR-007) → A: Créer un fichier Excel `ContactsParents.xlsx` contenant un premier onglet avec les données d'origine (`ExportIndividus`) et un second onglet `"ContactsParents"` (sans modifier `ExportIndividus.xls`).
- Q: Quels jeunes doivent être pris en compte selon leur statut d'inscription (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) dans `ExportIndividus.xls` ? (FR-002) → A: Inclure tous les jeunes (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) et mentionner le statut dans `Remarques` s'il est différent de `Inscrit(e)`.
- Q: Comment les unités des enfants doivent-elles être affichées dans la colonne `Unités des enfants` ? (FR-004) → A: Noms d'unités courts et lisibles (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extraction complète des coordonnées des parents depuis l'export SGDF (Priority: P1)

Un responsable ou secrétaire du groupe scout SGDF de La Rochelle dispose du fichier d'export des adhérents (`ExportIndividus.xls`) issu de l'intranet SGDF. Il lance l'outil d'extraction afin d'obtenir automatiquement la liste structurée de tous les représentants légaux (parents) des jeunes du groupe (qu'ils soient `Inscrit(e)`, `Pré-inscrit(e)` ou `Invité(e)`) avec leurs informations complètes : nom en majuscules, prénom avec initiale majuscule et reste en minuscules, téléphone portable principal, téléphone portable secondaire, téléphone fixe (domicile), adresse courriel, noms des enfants, unités des enfants (sous forme courte : `Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`), adresse postale complète, numéro d'adhérent éventuel et remarques.

**Why this priority**: Il s'agit de la fonctionnalité centrale qui remplace le travail manuel fastidieux de copie et de mise en forme des coordonnées des parents à partir de l'export brut.

**Independent Test**: Peut être testé indépendamment en exécutant l'extraction sur `ExportIndividus.xls` et en vérifiant que chaque parent rattaché à au moins un jeune figure dans le résultat avec les 11 champs attendus correctement normalisés, sans modifier le fichier source.

**Acceptance Scenarios**:

1. **Given** le fichier `ExportIndividus.xls` contenant les inscriptions des jeunes (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) et jusqu'à trois représentants légaux par jeune, **When** l'utilisateur exécute l'extraction, **Then** tous les parents renseignés (`Représentant Légal 1`, `2` ou `3`) des jeunes sont extraits avec les 11 colonnes demandées.
2. **Given** un parent dont le nom ou le prénom dans l'export original présente une casse hétérogène (tout en majuscules, tout en minuscules ou mixte), **When** la fiche du parent est générée, **Then** son nom de famille est converti intégralement en majuscules et son prénom est formaté avec la première lettre de chaque partie en majuscule et les suivantes en minuscules (ex. `DUPONT` et `Jean-Pierre`).
3. **Given** le fichier `ExportIndividus.xls` utilisé en entrée, **When** l'extraction se termine, **Then** le fichier `ExportIndividus.xls` d'origine demeure strictement intact (lecture seule).

---

### User Story 2 - Dédoublonnage des parents et regroupement des fratries et unités (Priority: P1)

Lorsqu'un même parent a plusieurs enfants dans le groupe scout (dans la même unité ou dans des unités différentes : `Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`), le responsable souhaite qu'une seule ligne soit créée pour ce parent. Cette ligne unique doit regrouper l'ensemble de ses enfants et l'ensemble des unités correspondantes afin d'éviter les doublons dans Google Contacts et de savoir immédiatement à quels groupes WhatsApp d'unités rattacher ce parent.

**Why this priority**: Indispensable pour éviter les fiches dupliquées dans Google Contacts et pour rattacher chaque parent aux bons groupes WhatsApp d'unités lorsqu'une fratrie est répartie sur plusieurs tranches d'âge.

**Independent Test**: Peut être testé en vérifiant sur un parent ayant plusieurs enfants dans `ExportIndividus.xls` qu'il n'apparaît qu'une seule fois dans l'onglet final, avec la liste complète de ses enfants et de leurs unités courtes respectives sans doublon.

**Acceptance Scenarios**:

1. **Given** deux ou plusieurs jeunes ayant un parent portant le même couple `(Nom, Prénom)` (après normalisation de la casse et des espaces), **When** l'extraction regroupe les entrées, **Then** une seule entrée est produite pour ce parent dans la liste finale.
2. **Given** un parent rattaché à plusieurs enfants, **When** ses informations sont consolidées, **Then** le champ des enfants contient les prénoms (et noms si différents) de tous ses enfants et le champ des unités mentionne toutes les unités courtes correspondantes (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`) sans perte d'information.
3. **Given** un parent présent sur plusieurs fiches d'enfants où certaines coordonnées (ex. téléphone secondaire, fixe ou courriel) ne sont renseignées que sur l'une des fiches, **When** le dédoublonnage est effectué, **Then** la fiche consolidée conserve les valeurs non vides les plus complètes.

---

### User Story 3 - Enrichissement des remarques et du numéro d'adhérent du parent (Priority: P2)

Certains parents de jeunes s'investissent également comme membres ou bénévoles au sein du groupe (par exemple en tant que Parent Animateur / Accompagnateur Farfadet, responsable ou membre d'équipe de groupe), ou ont un enfant dont l'inscription est encore en statut `Pré-inscrit(e)` ou `Invité(e)`. Le responsable souhaite que le numéro d'adhérent du parent, son rôle éventuel au sein du groupe ainsi que tout statut d'inscription particulier de l'enfant (`Pré-inscrit(e)` ou `Invité(e)`) soient automatiquement reportés dans le champ numéro d'adhérent et dans le champ libre de remarques.

**Why this priority**: Permet d'identifier immédiatement dans la liste des contacts les parents qui ont un rôle actif dans le groupe (notamment les Parents Accompagnateurs Farfadets) ainsi que les familles en cours d'inscription ou à l'essai, sans avoir à croiser manuellement les lignes.

**Independent Test**: Peut être testé en vérifiant que les parents également inscrits comme adultes dans `ExportIndividus.xls` (ex. fonction `271 - PARENT ANIMATEUR FARFADET`) disposent bien de leur numéro d'adhérent et de la mention de leur rôle dans la colonne des remarques, et que les parents d'enfants `Pré-inscrit(e)` ou `Invité(e)` ont cette précision dans leurs remarques.

**Acceptance Scenarios**:

1. **Given** un parent de jeune dont le numéro d'adhérent figure sur la fiche du représentant légal ou sur une fiche individuelle adulte portant les mêmes nom et prénom, **When** la liste est générée, **Then** son numéro d'adhérent SGDF est renseigné dans la colonne dédiée.
2. **Given** un parent de jeune qui possède également une inscription adulte dans l'export (par exemple `PARENT ANIMATEUR FARFADET`, `RESPONSABLE DE GROUPE`, `TRESORIER DE GROUPE`, `SECRETAIRE DE GROUPE`, `CHARGE DE MISSION DU GROUPE`), **When** la liste est générée, **Then** cette fonction (ainsi que toute délégation éventuelle) est inscrite dans le champ libre de remarques.
3. **Given** un parent dont l'un des enfants a un statut `Inscriptions.Type` différent de `Inscrit(e)` (c.-à-d. `Pré-inscrit(e)` ou `Invité(e)`), **When** la liste est générée, **Then** cette information est mentionnée dans le champ libre de remarques.

---

### User Story 4 - Sauvegarde triée dans l'onglet `ContactsParents` (Priority: P1)

Le responsable souhaite que la liste finale soit enregistrée dans un classeur Excel `ContactsParents.xlsx` comprenant un premier onglet `ExportIndividus` (reprenant les données d'origine) et un second onglet nommé exactement `ContactsParents`, dans lequel les lignes sont triées par ordre alphabétique d'abord sur le nom de famille puis sur le prénom du parent, afin de regrouper visuellement les membres d'une même famille.

**Why this priority**: Garantit un fichier de sortie directement exploitable par l'équipe de groupe pour les imports Google Contacts et le pointage des groupes WhatsApp tout en conservant les données sources en regard.

**Independent Test**: Peut être testé en ouvrant le classeur `ContactsParents.xlsx` généré, en vérifiant la présence des onglets `ExportIndividus` et `ContactsParents`, l'ordre exact des colonnes et le tri alphabétique strict sur `(Nom, Prénom)`.

**Acceptance Scenarios**:

1. **Given** l'ensemble des parents extraits et dédoublonnés, **When** le fichier de sortie `ContactsParents.xlsx` est écrit, **Then** il contient l'onglet `ExportIndividus` (données d'origine) et l'onglet nommé exactement `ContactsParents`.
2. **Given** les lignes présentes dans l'onglet `ContactsParents`, **When** on parcourt la liste du haut vers le bas, **Then** toutes les entrées sont triées par ordre alphabétique croissant sur le nom du parent, puis sur le prénom du parent en cas d'égalité de nom.

---

### Edge Cases

- **Prénoms ou noms composés et caractères accentués** : Un prénom composé (ex. `JEAN-BAPTISTE` ou `marie claire`) doit conserver la majuscule sur chaque composant (`Jean-Baptiste`, `Marie Claire`), et le tri alphabétique doit gérer correctement les lettres accentuées françaises (`É`, `È`, `Ç`, etc.) sans reléguer les noms accentués en fin de liste.
- **Représentant légal partiellement renseigné ou absent** : Si un jeune n'a qu'un seul représentant légal renseigné (`Représentant Légal 1` présent, `Représentant Légal 2` et `3` vides), seuls les représentants légaux ayant au moins un nom ou un prénom non vide sont créés.
- **Parents d'une même fratrie portant des noms de famille différents** : Chaque parent est trié selon son propre `(Nom, Prénom)` tout en listant la totalité de ses enfants rattachés ; si un enfant porte un nom de famille différent de celui du parent, le nom de famille de l'enfant peut être précisé à côté de son prénom pour éviter toute confusion.
- **Coordonnées téléphoniques ou courriels multiples / formatés différemment** : Les numéros de téléphone (portable 1, portable 2, fixe) et adresses courriel (personnel ou dédié SGDF) sont nettoyés des espaces superflus et préservés au format texte (avec le `0` initial ou l'indicatif `+33` intact, sans conversion en nombre entier qui ferait disparaître le `0` de tête).
- **Jeunes majeurs ou adultes sans représentant légal** : Les lignes d'adultes (chefs, responsables, membres Impeesa) qui n'ont pas de représentant légal renseigné ne génèrent pas de parent fictif ; seules les fiches ayant des représentants légaux renseignés produisent des entrées de parents, tandis que les fiches adultes servent à enrichir le numéro d'adhérent et les remarques des parents correspondants.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT lire en lecture seule le fichier d'export SGDF (`ExportIndividus.xls` par défaut, ou tout chemin fourni en argument) sans jamais modifier ni altérer le fichier d'entrée.
- **FR-002**: Le système DOIT extraire l'ensemble des représentants légaux (`Représentant Légal 1`, `Représentant Légal 2` et `Représentant Légal 3`) renseignés sur toutes les lignes de jeunes (`Fonction.CategorieMembre == 0`, quel que soit leur statut `Inscrit(e)`, `Pré-inscrit(e)` ou `Invité(e)`).
- **FR-003**: Le système DOIT dédoublonner les parents selon la clé unique composée du couple `(Nom normalisé, Prénom normalisé)` du parent, afin de regrouper sous une seule entrée tous les enfants et toutes les unités rattachés à ce parent.
- **FR-004**: Pour chaque parent dédoublonné, le système DOIT produire les 11 champs suivants dans l'onglet de sortie :
  1. **Nom** : Nom de famille du parent intégralement en MAJUSCULES.
  2. **Prénom** : Prénom du parent en minuscules avec la première lettre de chaque mot/partie en majuscule.
  3. **Téléphone portable principal** : Numéro de portable principal (`TelephonePortable1`), conservé sous forme de texte.
  4. **Téléphone portable secondaire** : Numéro de portable secondaire (`TelephonePortable2`), conservé sous forme de texte.
  5. **Téléphone fixe (domicile)** : Numéro de téléphone domicile (`TelephoneDomicile`), conservé sous forme de texte.
  6. **Adresse email** : Adresse courriel du parent (`CourrielPersonnel`, complétée ou remplacée par `CourrielDédiéSGDF` si le courriel personnel est vide).
  7. **Noms des enfants** : Liste dédoublonnée des enfants rattachés à ce parent.
  8. **Unités des enfants** : Liste dédoublonnée des unités fréquentées par les enfants de ce parent, normalisées sous forme courte et lisible (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`).
  9. **Adresse physique** : Adresse postale complète du parent regroupant les lignes d'adresse, le code postal, la municipalité et le pays (s'il est différent de `FRANCE`).
  10. **Numéro d'adhérent** : Code adhérent SGDF du parent s'il en possède un (issu du champ `RepresentantLegalX.CodeAdherent` ou de sa propre ligne d'inscription adulte dans l'export).
  11. **Remarques** : Champ libre regroupant les informations complémentaires utiles au groupe : d'une part le rôle éventuel du parent au sein du groupe scout (ex. `Parent Animateur Farfadet` / `Parent Accompagnateur Farfadet`, fonction de groupe ou délégation) lorsqu'il figure également parmi les inscrits adultes de l'export, et d'autre part le statut d'inscription de l'enfant s'il est `Pré-inscrit(e)` ou `Invité(e)`.
- **FR-005**: Lors de la fusion de plusieurs occurrences d'un même parent (cas d'une fratrie), le système DOIT conserver la première valeur non vide disponible pour chaque coordonnée individuelle (téléphones, courriel, adresse, numéro d'adhérent) et concaténer sans doublon les enfants, leurs unités et les remarques.
- **FR-006**: Le système DOIT trier la liste finale des parents par ordre alphabétique croissant sur le **Nom**, puis sur le **Prénom** (selon l'ordre alphabétique français prenant en compte les caractères accentués).
- **FR-007**: Le système DOIT sauvegarder le résultat dans un classeur Excel `.xlsx` (par défaut `ContactsParents.xlsx`) comprenant un premier onglet `ExportIndividus` (copie tabulaire des données d'origine) et un second onglet nommé exactement `ContactsParents` (tout en laissant `ExportIndividus.xls` intact).
- **FR-008**: Le script, sa documentation, ses arguments en ligne de commande, ses messages d'exécution/erreur, ses noms de fichiers, de variables et de fonctions DOIVENT être rédigés intégralement en français conformément au Principe I de la constitution.

### Key Entities

- **Jeune Scout (`Individu` jeune)** : Enfant ou adolescent inscrit dans une unité du groupe SGDF de La Rochelle, caractérisé par son nom, son prénom, son unité normalisée (`Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`), son type d'inscription (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) et ses représentants légaux (`1`, `2`, `3`).
- **Parent / Représentant Légal (`ContactParent`)** : Adulte responsable d'un ou plusieurs jeunes scouts, identifié de manière unique par son couple `(Nom, Prénom)`, possédant des coordonnées de contact (portables 1 et 2, fixe, courriel, adresse physique), la liste de ses enfants et de leurs unités courtes, ainsi qu'éventuellement un numéro d'adhérent SGDF et un rôle bénévole dans le groupe (remarques).
- **Fiche Adulte du Groupe** : Enregistrement dans `ExportIndividus.xls` correspondant à un adulte inscrit dans le groupe (ex. `PARENT ANIMATEUR FARFADET`, responsable ou équipier de groupe), permettant d'enrichir la fiche `ContactParent` correspondante avec son numéro d'adhérent et sa fonction dans la colonne `Remarques`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des représentants légaux renseignés sur les fiches des jeunes de `ExportIndividus.xls` sont extraits et regroupés sans aucun doublon de couple `(Nom, Prénom)` dans l'onglet `ContactsParents` (soit les 134 parents uniques présents dans l'export de référence).
- **SC-002**: 100 % des parents ayant plusieurs enfants inscrits dans `ExportIndividus.xls` voient la totalité de leurs enfants et des unités courtes associées regroupés sur leur ligne unique.
- **SC-003**: 100 % des parents également inscrits comme adultes dans l'export (notamment les 18 Parents Animateurs/Accompagnateurs Farfadets) ont leur numéro d'adhérent et leur rôle renseignés dans les colonnes `Numéro d'adhérent` et `Remarques`.
- **SC-004**: 100 % des lignes de l'onglet `ContactsParents` respectent le formatage imposé (Nom en MAJUSCULES, Prénom en Casse Titre, numéros de téléphone avec zéro initial préservé, unités courtes) et sont triées alphabétiquement sur `(Nom, Prénom)`.
- **SC-005**: L'exécution complète de l'extraction sur un export de groupe SGDF standard (< 500 lignes) s'effectue en moins de 5 secondes et laisse le fichier source `ExportIndividus.xls` strictement inchangé.

## Assumptions

- Le fichier de sortie par défaut est `ContactsParents.xlsx` à la racine du projet (exclu du suivi Git par `.gitignore`), contenant un premier onglet `ExportIndividus` et un second onglet `ContactsParents`, avec possibilité de spécifier un chemin de fichier d'entrée et de sortie différent en ligne de commande.
- Dans la colonne `Noms des enfants`, chaque enfant est affiché sous la forme `Prénom` (ou `Prénom NOM` si le nom de famille de l'enfant diffère de celui du parent) séparé par une virgule lorsque le parent a plusieurs enfants, et les unités courtes dans `Unités des enfants` sont dédoublonnées et séparées par une virgule.
- Lorsqu'un parent figure également comme membre adulte dans `ExportIndividus.xls` (ex. `PARENT ANIMATEUR FARFADET`, `RESPONSABLE DE GROUPE`, etc.), sa fonction officielle SGDF (et sa délégation éventuelle) est automatiquement ajoutée dans le champ `Remarques`, tout comme le statut `Pré-inscrit(e)` ou `Invité(e)` d'un enfant.
