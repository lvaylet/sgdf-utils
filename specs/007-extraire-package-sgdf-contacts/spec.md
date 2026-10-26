# Spécification Fonctionnelle : Extraction du Cœur Métier dans un Package Modulaire `sgdf_contacts`

**Feature Branch**: `007-extraire-package-sgdf-contacts`

**Created**: 2026-10-26

**Status**: Draft

**Input**: Description utilisateur : "Travaille sur https://github.com/lvaylet/sgdf-utils/issues/3 dans une branche dédiée."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mutualisation du cœur métier, des règles de normalisation et des constantes partagées (Priority: P1)

Un mainteneur ou bénévole du groupe scout SGDF de La Rochelle qui fait évoluer les règles de gestion des contacts des parents dispose désormais d'une source unique de vérité regroupant les entités métier (parents, enfants rattachés, profils adultes du groupe, fiches de contact), les constantes partagées (en-têtes des 13 colonnes de l'onglet `ContactsParents`, libellés des fonctions adultes, étiquettes par défaut) et les règles de normalisation des coordonnées. Aucune règle ni constante n'est dupliquée entre l'outil d'extraction et l'outil de génération des contacts. En outre, chaque fiche parent expose directement son identifiant de conversation de messagerie instantanée calculé à partir de son téléphone portable principal (par exemple `33687966975@c.us` pour `+33687966975`), prêt pour les automatisations futures du groupe.

**Why this priority**: Élimine toute duplication de logique et de constantes entre les outils existants et constitue le socle indispensable pour les futures évolutions d'automatisation du groupe SGDF sans risque de divergence entre les traitements.

**Independent Test**: Peut être testé indépendamment en vérifiant que les entités, les constantes et les règles de normalisation proviennent d'un emplacement unique partagé, qu'aucune définition en doublon ne subsiste dans les scripts en ligne de commande et que l'identifiant de messagerie est correctement dérivé du numéro portable principal normalisé.

**Acceptance Scenarios**:

1. **Given** les règles de normalisation (noms, prénoms, numéros de téléphone, unités scoutes courtes, rôles adultes, délégations, adresses postales, tri alphabétique français) et les constantes métier (en-têtes des 13 colonnes `ContactsParents`, libellés des rôles adultes, étiquettes `"SGDF"` et `"La Rochelle"`), **When** on inspecte les deux outils du projet, **Then** ces définitions existent en un seul exemplaire partagé et aucune duplication ne subsiste entre les scripts.
2. **Given** une fiche parent possédant un numéro de téléphone portable principal valide (ex. `+33687966975`), **When** on consulte son identifiant de conversation de messagerie, **Then** la valeur retournée correspond au numéro dépourvu du signe `+` suivi du suffixe `@c.us` (`33687966975@c.us`).
3. **Given** une fiche parent dépourvue de numéro de téléphone portable principal, **When** on consulte son identifiant de conversation de messagerie, **Then** la valeur retournée est vide (`""`).

---

### User Story 2 - Lecture et génération des contacts en mémoire ou sur disque sans fichier intermédiaire obligatoire (Priority: P1)

Un processus d'automatisation du groupe SGDF ou un utilisateur avancé peut lire un export d'adhérents (`ExportIndividus.xls`) aussi bien depuis un fichier sur disque que directement depuis un contenu binaire en mémoire, et peut générer les fiches de contacts (`.vcf` pour Google Contacts ou `.xlsx` pour tableur) aussi bien dans des fichiers sur disque qu'en mémoire, y compris la génération directe des fiches contacts `.vcf` à partir de la liste des parents extraits sans devoir écrire ni relire un classeur `.xlsx` intermédiaire sur le disque.

**Why this priority**: Permet d'enchaîner l'extraction et la génération de contacts directement en mémoire et prépare l'intégration avec des flux d'automatisation externes sans dépendre de fichiers temporaires sur le système de fichiers.

**Independent Test**: Peut être testé indépendamment en fournissant le contenu d'un export SGDF sous forme de flux en mémoire pour extraire la liste des parents, puis en produisant à la fois le classeur en mémoire et le contenu vCard directement depuis cette liste de parents en mémoire, et en vérifiant que les résultats sont strictement identiques à ceux produits via des fichiers sur disque.

**Acceptance Scenarios**:

1. **Given** le contenu brut d'un export SGDF `ExportIndividus.xls` fourni directement en mémoire (sans chemin de fichier sur disque), **When** l'analyse et le regroupement des parents sont exécutés, **Then** les en-têtes, les lignes de données et la liste consolidée des parents extraits sont strictement identiques à ceux obtenus en lisant le même fichier depuis le disque.
2. **Given** une liste de parents extraits en mémoire, **When** on génère les fiches de contacts au format vCard 3.0 directement depuis cette liste de parents (sans passer par un fichier `ContactsParents.xlsx` intermédiaire), **Then** le contenu `.vcf` produit est strictement identique (identité, téléphones, courriel, adresse postale, note structurée avec enfants/unités/numéro d'adhérent/remarques, et étiquettes `"SGDF"` et `"La Rochelle"`) à celui généré en relisant le classeur `ContactsParents.xlsx`.
3. **Given** les données extraites d'un export SGDF, **When** on demande la génération du classeur `ContactsParents` dans un flux en mémoire, **Then** le classeur produit en mémoire contient exactement les deux onglets `ExportIndividus` et `ContactsParents` avec la même structure, les mêmes 13 colonnes et le même formatage que lors d'une écriture sur disque.

---

### User Story 3 - Rétrocompatibilité totale des commandes en ligne de commande et des résultats produits (Priority: P1)

Un bénévole ou secrétaire du groupe SGDF de La Rochelle qui utilise les commandes habituelles `python3 extract_parent_contacts.py` et `python3 generate_contacts_vcf.py` (avec ou sans les options `--input` et `--output`, ou `--help`) continue d'exécuter exactement les mêmes commandes à la racine du dépôt et obtient des fichiers `ContactsParents.xlsx` et `ContactParents.vcf` ainsi que des messages en français strictement identiques à ceux produits avant la réorganisation.

**Why this priority**: Garantit qu'aucune habitude des bénévoles ni aucun script ou test existant n'est perturbé par la structuration modulaire interne du projet.

**Independent Test**: Peut être testé de bout en bout en exécutant les commandes habituelles sur l'export de référence `ExportIndividus.xls` ainsi que l'intégralité de la suite de tests existante, et en vérifiant que les 134 parents uniques, les 13 colonnes du tableur et les 134 fiches vCard sont produits sans aucune régression.

**Acceptance Scenarios**:

1. **Given** les scripts `extract_parent_contacts.py` et `generate_contacts_vcf.py` présents à la racine du projet, **When** un bénévole les exécute en ligne de commande avec les options par défaut ou personnalisées (`-i`/`--input`, `-o`/`--output`, `--help`), **Then** le comportement, les codes de retour, les messages d'aide et d'erreur en français et les fichiers générés (`ContactsParents.xlsx` et `ContactParents.vcf`) sont strictement inchangés.
2. **Given** l'ensemble des tests automatisés existants et nouveaux du projet, **When** la suite de vérification est lancée dans l'environnement éphémère du projet, **Then** 100 % des tests et des contrôles de qualité réussissent sans erreur.

---

### Edge Cases

- **Flux binaire vide ou invalide en mémoire** : Lorsqu'un flux binaire vide ou dépourvu de tableau d'export SGDF valide (absence de lignes ou de la colonne `Individu.Nom`) est fourni en mémoire au lecteur d'export, une erreur métier explicite en français doit être signalée exactement comme pour un fichier invalide sur disque.
- **Parent sans numéro de téléphone portable principal** : Lorsqu'un parent ne possède qu'un numéro de téléphone fixe ou aucune coordonnée téléphonique, son identifiant de conversation de messagerie doit retourner une chaîne vide (`""`) sans provoquer d'erreur.
- **Numéro de téléphone portable déjà dépourvu ou muni du préfixe `+`** : L'identifiant de conversation de messagerie doit normaliser ou retirer proprement le préfixe `+` éventuel afin de toujours produire le format `<chiffres>@c.us` (ex. `33687966975@c.us`) uniquement lorsqu'un numéro portable principal est présent.
- **Génération directe de vCard depuis une liste de parents vide** : Si la liste de parents fournie est vide, la génération vCard (sur disque ou en mémoire) doit produire un résultat vide valide sans erreur.
- **Intégrité des fichiers sources** : Que la lecture s'effectue depuis un chemin sur disque ou depuis un flux en mémoire, le fichier source `ExportIndividus.xls` et le fichier `ContactsParents.xlsx` (lorsqu'il est lu en entrée) ne doivent jamais être modifiés.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT regrouper dans un package modulaire partagé (`sgdf_contacts`) l'ensemble de la logique métier, des parseurs d'entrée et des générateurs de sortie, séparés en trois sous-ensembles distincts :
  1. Le domaine métier pur (`domain`) contenant les entités (`ParentContact`, `AttachedChild`, `AdultGroupProfile`, `ParentContactCard`), les constantes partagées (`PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`) et toutes les fonctions pures de nettoyage, de normalisation et de tri,
  2. Les parseurs d'entrée (`parsers`) contenant la lecture de l'export `ExportIndividus.xls`, l'indexation des profils adultes, l'extraction/regroupement des parents et la lecture du classeur `ContactsParents.xlsx`,
  3. Les générateurs de sortie (`exporters`) contenant l'écriture du classeur `ContactsParents.xlsx` et la génération des fiches de contacts au format vCard 3.0 (`ContactParents.vcf`).
- **FR-002**: Aucune duplication de constantes (`PARENT_CONTACTS_HEADERS`, `ADULT_ROLE_LABELS`, `DEFAULT_CATEGORIES`), d'entités ou de fonctions de normalisation NE DOIT subsister entre `extract_parent_contacts.py` et `generate_contacts_vcf.py`.
- **FR-003**: L'entité représentant un parent (`ParentContact`) DOIT exposer une propriété `waha_chat_id` qui convertit son numéro de téléphone portable principal normalisé (ex. `+33687966975`) en identifiant de messagerie au format `<chiffres>@c.us` (ex. `33687966975@c.us`), ou retourne une chaîne vide (`""`) si le parent n'a pas de numéro portable principal.
- **FR-004**: Le parseur de l'export d'adhérents (`read_individuals_export_table`) DOIT accepter en entrée aussi bien un chemin de fichier (`Path`) qu'un contenu binaire en mémoire (`bytes` ou flux binaire), en appliquant les mêmes validations et en levant la même erreur métier explicite en français en cas de contenu invalide.
- **FR-005**: Le générateur de classeur Excel (`write_parent_contacts_workbook`) DOIT permettre d'écrire le classeur complet (onglets `ExportIndividus` et `ContactsParents`) aussi bien vers un chemin de fichier sur disque (`Path`) que vers un flux binaire en mémoire.
- **FR-006**: Le générateur vCard 3.0 DOIT permettre de convertir et d'exporter directement une liste d'entités `ParentContact` en mémoire (en plus d'une liste de `ParentContactCard` lue depuis `ContactsParents.xlsx`) vers un fichier `.vcf` ou en mémoire, en produisant un résultat vCard 3.0 strictement identique.
- **FR-007**: Les scripts `extract_parent_contacts.py` et `generate_contacts_vcf.py` à la racine du dépôt DOIVENT être conservés comme points d'entrée en ligne de commande délégant les traitements au package partagé tout en préservant l'intégralité des arguments CLI (`-i`/`--input`, `-o`/`--output`, `--help`), des messages utilisateur en français, des codes de sortie et des symboles importés par les tests existants.
- **FR-008**: Conformément à la constitution du projet, tous les identifiants du code (noms des modules, classes, fonctions, méthodes, constantes, variables et paramètres) DOIVENT être rédigés en anglais, tandis que tous les commentaires, docstrings, messages utilisateur et la documentation (`README.md`) DOIVENT être rédigés en français.

### Key Entities

- **`ParentContact` (Fiche Parent Consolidée)** : Entité du domaine regroupant l'identité normalisée d'un parent, ses coordonnées téléphoniques, électroniques et postales, ses enfants rattachés (`AttachedChild`), leurs unités, son numéro d'adhérent éventuel, ses remarques consolidées, sa conversion en ligne de tableur ou en fiche de contact vCard, ainsi que son identifiant `waha_chat_id`.
- **`AttachedChild` (Enfant Rattaché)** : Entité immuable représentant un jeune scout rattaché à un parent (prénom normalisé, nom normalisé, unité courte et statut d'inscription).
- **`AdultGroupProfile` (Profil Adulte du Groupe)** : Entité représentant l'inscription adulte d'un membre du groupe SGDF (numéro d'adhérent, rôles et délégations, coordonnées) servant à enrichir la fiche d'un parent.
- **`ParentContactCard` (Carte de Contact vCard)** : Entité immuable prête pour la sérialisation au format vCard 3.0 (identité, téléphones, courriel, adresse postale, enfants et unités formatés, numéro d'adhérent, remarques et catégories `"SGDF"`, `"La Rochelle"`), pouvant être construite directement depuis un `ParentContact` ou depuis une ligne de l'onglet `ContactsParents`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 duplication de constantes métier, d'entités ou de fonctions de normalisation ne subsiste entre `extract_parent_contacts.py` et `generate_contacts_vcf.py` (100 % de la logique métier est centralisée dans le package `sgdf_contacts`).
- **SC-002**: 100 % des fonctionnalités de lecture d'export SGDF et de génération (`.xlsx` et `.vcf`) fonctionnent aussi bien en mémoire (sans fichier temporaire sur disque) que via des chemins de fichiers sur disque, avec une égalité stricte (100 % de correspondance) des résultats produits.
- **SC-003**: Sur l'export de référence `ExportIndividus.xls`, l'extraction continue d'identifier exactement les 134 parents uniques dédoublonnés (dont les 20 parents ayant le rôle `Parent Animateur Farfadet`) et la génération vCard produit exactement les 134 fiches contacts attendues, que l'on passe par le fichier `ContactsParents.xlsx` ou directement par la liste des `ParentContact` en mémoire.
- **SC-004**: 100 % de la suite de tests automatisés existante et des nouveaux tests unitaires du package s'exécutent avec succès, et le vérificateur de qualité du code rapporte 0 anomalie.

## Assumptions

- Pour préserver une rétrocompatibilité complète avec la suite de tests existante (`tests/test_extract_parent_contacts.py` et `tests/test_generate_contacts_vcf.py`), les scripts `extract_parent_contacts.py` et `generate_contacts_vcf.py` ré-exportent les symboles publics qu'ils exposaient auparavant tout en déléguant leur implémentation au package `sgdf_contacts`.
- La propriété `waha_chat_id` sur `ParentContact` se base sur le numéro `primary_mobile_phone` déjà normalisé au format international (`+336...` ou `+337...`), retire le préfixe `+` initial et ajoute le suffixe `@c.us` attendu par WAHA ; si `primary_mobile_phone` est vide, elle retourne `""`.
- La documentation `README.md` est mise à jour en français pour présenter l'architecture modulaire du package `sgdf_contacts` en complément de l'utilisation des scripts en ligne de commande.
