# Spécification Fonctionnelle : Persistance Locale des Contacts Parents et Calcul de Différentiel d'Import

**Feature Branch**: `008-persistance-sqlite-differentiel`

**Created**: 2026-10-26

**Status**: Draft

**Input**: Description utilisateur : "Travaille sur https://github.com/lvaylet/sgdf-utils/issues/4 dans une branche dédiée, avec une Pull Request avec un titre en anglais."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stockage persistant des parents et de leurs enfants avec calcul automatique des nouveautés et modifications à chaque import (Priority: P1)

Un responsable ou bénévole du groupe scout SGDF de La Rochelle qui reçoit régulièrement un nouvel export des adhérents (`ExportIndividus.xls`) peut importer et synchroniser ces données dans un stockage local durable des contacts parents et de leurs enfants rattachés. À chaque import, le système rapproche automatiquement les parents existants (par leur identité ou leur numéro d'adhérent), met à jour leurs coordonnées, leurs enfants et leurs remarques, désactive de manière réversible les parents qui ne figurent plus dans le nouvel export (tout en préservant leurs métadonnées externes comme l'indicateur de présence sur messagerie instantanée), et fournit un rapport détaillé de différentiel distinguant les parents nouvellement créés, les parents modifiés (avec le détail exact des champs ayant changé), les parents inchangés et les parents désactivés.

**Why this priority**: Permet de suivre l'évolution des familles du groupe au fil de l'année scoute sans perdre les métadonnées enrichies localement et sans avoir à comparer manuellement deux exports successifs.

**Independent Test**: Peut être testé indépendamment en important une première fois l'export des adhérents dans un stockage vierge, en vérifiant que tous les parents sont signalés comme créés, puis en ré-important le même export (qui doit signaler uniquement des parents inchangés), et enfin en important un export modifié (ajout d'un parent, changement de téléphone ou d'unité d'un enfant, retrait d'un parent) et en vérifiant que le rapport de différentiel remonte exactement les créations, modifications détaillées et désactivations attendues.

**Acceptance Scenarios**:

1. **Given** un stockage local initialisé et vide ainsi qu'un export d'adhérents valide (`ExportIndividus.xls`), **When** l'import est exécuté, **Then** l'ensemble des parents extraits et leurs enfants rattachés sont enregistrés comme actifs, leurs dates de première apparition et de mise à jour sont renseignées, et le rapport de différentiel liste tous les parents dans les créations (`created`), avec zéro modification (`updated`), zéro inchangé (`unchanged`) et zéro désactivation (`deactivated`).
2. **Given** un stockage local déjà alimenté par un premier export d'adhérents, **When** le même export est importé une seconde fois sans changement, **Then** l'opération est strictement idempotente : aucun doublon de parent ni d'enfant n'est créé, et le rapport de différentiel indique `0 created`, `0 updated`, `0 deactivated` et la totalité des parents dans `unchanged`.
3. **Given** un stockage local contenant des parents actifs (dont certains disposent d'une métadonnée externe de présence sur messagerie instantanée déjà renseignée), **When** un nouvel export contenant un nouveau parent, un parent existant dont le téléphone ou l'unité d'un enfant a changé, et l'absence d'un parent précédemment présent est importé, **Then** le rapport de différentiel détaille précisément le parent créé, le parent mis à jour avec les valeurs avant/après des champs modifiés, les parents inchangés et le parent désactivé (`is_active = False`), tout en conservant intacte la métadonnée de messagerie instantanée sur les parents mis à jour ou désactivés.

---

### User Story 2 - Consultation, filtrage et recherche rapide des parents stockés (Priority: P1)

Un bénévole ou un service d'automatisation du groupe SGDF peut interroger directement le stockage local pour lister les parents actifs selon le tri alphabétique français habituel, filtrer les parents selon l'unité scoute d'au moins un de leurs enfants, selon le statut d'inscription d'un enfant ou selon la présence d'un numéro de téléphone portable valide, ou encore retrouver immédiatement la fiche d'un parent à partir d'un numéro de téléphone (qu'il s'agisse de son portable principal, de son portable secondaire ou de son téléphone fixe).

**Why this priority**: Évite de devoir relire et ré-analyser le fichier d'export brut à chaque besoin opérationnel (envoi de messages ciblés par unité, identification d'un appelant ou d'un expéditeur par son numéro de téléphone).

**Independent Test**: Peut être testé indépendamment sur un stockage alimenté en exécutant les différentes recherches (liste complète triée, filtre par unité comme `LOUVETEAUX-JEANNETTES`, filtre par statut d'inscription, filtre par présence de portable valide, et recherche par numéro de téléphone sur les trois champs téléphoniques) et en vérifiant que les parents retournés correspondent exactement aux critères.

**Acceptance Scenarios**:

1. **Given** un stockage local contenant plusieurs parents actifs et inactifs, **When** on demande la liste des parents actifs, **Then** seuls les parents actifs sont retournés, triés par ordre alphabétique français sans sensibilité à la casse ni aux accents (nom de famille puis prénom), accompagnés de leurs enfants rattachés.
2. **Given** un stockage local contenant des parents dont les enfants appartiennent à différentes unités et ont différents statuts d'inscription, **When** on filtre par unité courte (ex. `FARFADETS`), par statut d'inscription (ex. `Pré-inscrit(e)`) ou par présence d'un numéro de portable valide, **Then** seuls les parents actifs répondant exactement aux critères demandés sont retournés.
3. **Given** un parent enregistré avec un portable principal, un portable secondaire et/ou un téléphone fixe, **When** on recherche un parent à partir de l'un quelconque de ces trois numéros (fourni au format normalisé ou brut), **Then** la fiche correspondante du parent est retrouvée.

---

### User Story 3 - Régénération directe des fichiers d'export (`ContactParents.vcf` et `ContactsParents.xlsx`) depuis le stockage local (Priority: P1)

Un responsable du groupe SGDF peut régénérer à la demande le fichier de contacts pour téléphone/messagerie (`ContactParents.vcf`) ainsi que le classeur tableur (`ContactsParents.xlsx`) directement à partir des parents actifs enregistrés dans le stockage local, sans avoir besoin de relire le fichier d'export original `ExportIndividus.xls`.

**Why this priority**: Garantit que le stockage local contient l'intégralité des informations métier nécessaires pour produire à tout moment les livrables de contacts utilisés par le groupe scout.

**Independent Test**: Peut être testé indépendamment en important `ExportIndividus.xls` dans le stockage local, puis en générant `ContactParents.vcf` et l'onglet `ContactsParents` de `ContactsParents.xlsx` uniquement à partir des données lues depuis le stockage local, et en vérifiant que les fiches des parents produites sont identiques à celles issues d'une extraction directe.

**Acceptance Scenarios**:

1. **Given** un stockage local alimenté à partir de l'export de référence `ExportIndividus.xls`, **When** on reconvertit les parents actifs du stockage local en entités du domaine pour générer le fichier `ContactParents.vcf`, **Then** le contenu vCard 3.0 généré est strictement identique aux 134 fiches produites directement depuis l'export original.
2. **Given** un stockage local alimenté à partir de l'export de référence `ExportIndividus.xls`, **When** on génère un classeur `ContactsParents.xlsx` directement depuis les parents actifs du stockage local sans disposer du fichier `ExportIndividus.xls`, **Then** le classeur est généré avec succès et son onglet `ContactsParents` contient exactement les 134 parents et les 13 colonnes attendues avec les mêmes valeurs qu'un export direct.

---

### Edge Cases

- **Rapprochement d'un parent qui acquiert un numéro d'adhérent lors d'un import ultérieur** : Si un parent était initialement enregistré sans numéro d'adhérent (rapproché par son couple `(nom, prénom)`) et qu'un nouvel export lui attribue désormais un numéro d'adhérent (`member_id`), le système doit reconnaître ce parent existant, mettre à jour son `member_id` sans créer de doublon, et signaler ce changement dans `updated`.
- **Rapprochement d'un parent par numéro d'adhérent dont le nom ou prénom a été légèrement corrigé** : Si un parent possède déjà un `member_id` non vide connu dans le stockage et que ce même `member_id` réapparaît dans un nouvel export, le rapprochement par `member_id` permet de mettre à jour la fiche existante plutôt que de la désactiver et d'en créer une nouvelle.
- **Réactivation d'un parent précédemment désactivé** : Lorsqu'un parent marqué inactif (`is_active = False`) lors d'un import précédent réapparaît dans un nouvel export, sa fiche existante est réactivée (`is_active = True`), ses métadonnées externes (`has_whatsapp`) et sa date de première apparition (`first_seen_at`) sont conservées, et il est comptabilisé dans les parents mis à jour (`updated`).
- **Fratries et parents partageant les mêmes enfants** : Lorsque deux parents (ex. père et mère) partagent un ou plusieurs enfants, chaque enfant est stocké sans duplication inutile et lié aux deux parents via une relation plusieurs-à-plusieurs ; la modification de l'unité ou du statut d'inscription d'un enfant met correctement à jour l'enfant et signale les parents concernés dans le rapport de différentiel.
- **Atomicité en cas d'erreur d'import** : Si une erreur survient au cours d'une opération d'import, l'ensemble de la transaction est annulé afin que le stockage local ne se retrouve jamais dans un état partiellement modifié.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT fournir un module de persistance locale au sein du package `sgdf_contacts` (`sgdf_contacts.persistence`) permettant de stocker durablement les parents, les enfants et leurs liens de rattachement dans une base de données relationnelle locale fichier ou mémoire.
- **FR-002**: Lors de toute connexion à une base locale SQLite, le système DOIT activer automatiquement l'application des clés étrangères (`PRAGMA foreign_keys=ON;`) ainsi que le journal d'écriture anticipée (`PRAGMA journal_mode=WAL;`) pour garantir l'intégrité référentielle et les performances en lecture/écriture concurrente.
- **FR-003**: Le modèle de persistance DOIT représenter trois ensembles de données liés :
  1. Les parents (`parents`) comportant : identifiant technique (`id`), numéro d'adhérent (`member_id`), nom (`last_name`), prénom (`first_name`), téléphone portable principal (`primary_mobile_phone`), téléphone portable secondaire (`secondary_mobile_phone`), téléphone fixe (`landline_phone`), adresse courriel (`email_address`), rue (`street`), code postal (`postal_code`), ville (`city`), remarques consolidées (`notes`), indicateur optionnel de présence WhatsApp (`has_whatsapp` : vrai, faux ou inconnu `None`), horodatage de première apparition (`first_seen_at`), horodatage de dernière modification (`updated_at`) et indicateur d'activité (`is_active`),
  2. Les enfants (`children`) comportant : identifiant technique (`id`), prénom (`first_name`), nom (`last_name`), unité scoute courte (`short_unit`) et statut d'inscription (`registration_status`),
  3. Les liens de rattachement (`parent_child_links`) assurant la relation plusieurs-à-plusieurs entre `parents` et `children`.
- **FR-004**: Le système DOIT fournir une opération d'import et de synchronisation transactionnelle acceptant une collection de fiches `ParentContact` (ou directement un export `ExportIndividus.xls`), réconciliant chaque parent sur son numéro d'adhérent (`member_id`) lorsqu'il est renseigné ou sur le couple `(last_name, first_name)`, et retournant un rapport de différentiel structuré (`ImportDiffReport`).
- **FR-005**: Le rapport de différentiel (`ImportDiffReport`) DOIT recenser précisément :
  - `created` : les nouveaux parents ajoutés lors de l'import,
  - `updated` : les parents existants dont au moins une coordonnée, le numéro d'adhérent, les remarques, le statut d'activité (`is_active`) ou la liste/unité/statut des enfants rattachés a changé, accompagnés du détail des champs modifiés (valeurs avant et après modification),
  - `unchanged` : les parents actifs présents dans l'export dont aucune donnée issue de l'export n'a changé,
  - `deactivated` : les parents précédemment actifs qui sont absents du nouvel export et qui ont été marqués `is_active = False`.
- **FR-006**: Lors d'une mise à jour ou d'une désactivation d'un parent, le système DOIT préserver les métadonnées enrichies en dehors de l'export SGDF (notamment `has_whatsapp` et `first_seen_at`) sans jamais les écraser ni supprimer physiquement la fiche du parent.
- **FR-007**: Le dépôt de persistance (`repository`) DOIT offrir des méthodes de consultation permettant :
  - de lister tous les parents actifs triés selon l'ordre alphabétique français (nom puis prénom, sans sensibilité aux accents ni à la casse),
  - de filtrer les parents actifs par unité courte d'enfant (`short_unit`), par statut d'inscription d'enfant (`registration_status`), ou par présence d'un numéro de téléphone portable valide,
  - de rechercher un parent à partir d'un numéro de téléphone sur l'un quelconque de ses trois champs téléphoniques (`primary_mobile_phone`, `secondary_mobile_phone`, `landline_phone`), que le numéro fourni soit déjà normalisé ou brut.
- **FR-008**: Le système DOIT permettre de convertir les parents stockés en base vers les entités du domaine (`ParentContact` / `ParentContactCard`) et de régénérer directement les fichiers `ContactParents.vcf` et `ContactsParents.xlsx` depuis la base de données sans avoir à relire le fichier `ExportIndividus.xls` d'origine.
- **FR-009**: Conformément à la constitution du projet, toute dépendance requise pour la persistance DOIT être déclarée dans l'environnement déclaratif du projet (`flake.nix` et `devbox.json`), l'intégralité des identifiants du code DOIT être rédigée en anglais, et l'ensemble des commentaires, docstrings et documentations DOIT être rédigé en français.

### Key Entities

- **`ParentRecord` (`parents`)** : Enregistrement persistant d'un parent de jeune(s) scout(s), conservant ses coordonnées normalisées, ses remarques, son état d'activité (`is_active`), ses dates de suivi (`first_seen_at`, `updated_at`), son indicateur externe `has_whatsapp` (`bool | None`) et sa relation plusieurs-à-plusieurs avec ses enfants.
- **`ChildRecord` (`children`)** : Enregistrement persistant d'un jeune scout rattaché à un ou plusieurs parents, identifié par son prénom et son nom normalisés et caractérisé par son unité courte (`short_unit`) et son statut d'inscription (`registration_status`).
- **`ParentChildLink` (`parent_child_links`)** : Lien d'association plusieurs-à-plusieurs reliant un parent (`parent_id`) et un enfant (`child_id`) en préservant l'ordre ou l'unicité des rattachements.
- **`ImportDiffReport` & `ParentUpdateDiff`** : Structures de rapport restituées à l'issue d'une synchronisation, listant les parents créés, mis à jour (avec le dictionnaire ou la liste des champs modifiés et leurs valeurs avant/après), inchangés et désactivés.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: L'import initial du fichier de référence `ExportIndividus.xls` dans une base vierge enregistre exactement les 134 parents uniques et leurs enfants rattachés, et retourne un rapport de différentiel indiquant `134 created`, `0 updated`, `0 unchanged` et `0 deactivated`.
- **SC-002**: La ré-importation immédiate du même fichier `ExportIndividus.xls` est 100 % idempotente et retourne `0 created`, `0 updated`, `134 unchanged` et `0 deactivated`.
- **SC-003**: Lors de l'import d'un jeu de données modifié (ajout de parent, modification de coordonnées ou d'enfants, retrait de parent), 100 % des créations, des champs modifiés et des désactivations sont détectés et restitués dans `ImportDiffReport` tout en conservant intacte la valeur de `has_whatsapp`.
- **SC-004**: Les fichiers `ContactParents.vcf` et l'onglet `ContactsParents` de `ContactsParents.xlsx` régénérés directement depuis la base de données contiennent 100 % des 134 parents et produisent des fiches strictement identiques à celles générées directement depuis `ExportIndividus.xls`.
- **SC-005**: 100 % des tests unitaires et d'intégration (incluant la vérification du mode WAL, des clés étrangères, du calcul de différentiel, des filtres de recherche et de la régénération des exports) s'exécutent avec succès dans l'environnement éphémère du projet.

## Assumptions

- Lorsqu'un classeur `ContactsParents.xlsx` est régénéré directement depuis la base locale sans disposer des lignes brutes de `ExportIndividus.xls`, l'écriture du classeur accepte des en-têtes/lignes sources optionnels (ou omet/laisse vide l'onglet `ExportIndividus` si aucune donnée source brute n'est fournie) tout en produisant l'onglet `ContactsParents` complet et formaté à l'identique.
- La clé de réconciliation d'un parent lors d'un import privilégie le `member_id` (s'il est non vide et correspond à un parent déjà doté de ce `member_id`), puis se replie sur le couple normalisé `(last_name, first_name)` afin de gérer de manière transparente le cas où un parent existant acquiert un numéro d'adhérent lors d'un import ultérieur.
- L'ordre de rattachement des enfants à un parent est déterministe afin que la régénération des colonnes `Enfants` et `Unités` ainsi que des notes vCard depuis la base de données produise un résultat strictement identique à l'extraction en mémoire.
