<!--
Sync Impact Report
- Version change: [CONSTITUTION_VERSION] (template initial) → 1.0.0
- Principes définis (remplacement des emplacements génériques du modèle) :
  - [PRINCIPLE_1_NAME] → I. Usage Intégral du Français (NON-NÉGOCIABLE)
  - [PRINCIPLE_2_NAME] → II. Environnement de Développement Éphémère et Déclaratif
  - [PRINCIPLE_3_NAME] → III. Automatisation Modulaire en Python 3
  - [PRINCIPLE_4_NAME] → IV. Protection des Données Personnelles et Intégrité des Sources
  - [PRINCIPLE_5_NAME] → V. Simplicité et Maintenabilité pour les Bénévoles
- Sections ajoutées :
  - Contraintes Techniques et Environnement
  - Flux de Travail et Assurance Qualité
- Sections supprimées : Aucune
- Modèles dépendants vérifiés (non modifiés conformément au périmètre de la commande) :
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
- Suivi (TODOs différés) : Aucun
-->
# Automatisation SGDF La Rochelle (Contacts Parents) Constitution

## Core Principles

### I. Usage Intégral du Français (NON-NÉGOCIABLE)
La totalité des écrits du projet DOIT être rédigée en langue française. Cette règle s'applique
sans exception à la documentation, aux spécifications, aux messages de validation (commits), aux
commentaires, aux noms de fichiers et de dossiers créés pour le projet, ainsi qu'à l'ensemble des
identifiants dans le code source (noms de modules, de variables, de fonctions, de classes, de
constantes et de paramètres) et aux messages affichés à l'utilisateur. Seuls les mots-clés du
langage Python, les fichiers de configuration imposés par des outils tiers (tels que `.envrc`,
`flake.nix` ou `devbox.json`) et les appels aux bibliothèques externes conservent leur nommage
d'origine.

**Justification** : Garantir une compréhension immédiate, homogène et sans barrière linguistique
pour tous les bénévoles et responsables du groupe scout SGDF de La Rochelle amenés à lire, utiliser
ou maintenir ces scripts.

### II. Environnement de Développement Éphémère et Déclaratif
Le projet DOIT fournir un environnement de développement éphémère, reproductible et isolé du
système hôte, reposant sur le gestionnaire de paquets Nix (avec `flakes` et `nix-command` activés)
et/ou sur Jetify Devbox. Cet environnement DOIT inclure Python 3 ainsi que l'intégralité des
paquets et dépendances nécessaires à l'exécution et à la vérification des scripts. L'activation de
cet environnement DOIT être automatisée par `direnv` via un fichier `.envrc` dès l'entrée dans le
dossier du projet. Aucune installation manuelle globale de paquets Python sur la machine hôte NE
DOIT être requise.

**Justification** : Éliminer les écarts de configuration entre machines et permettre une prise en
main instantanée dès l'ouverture du répertoire de travail, sans polluer le système hôte.

### III. Automatisation Modulaire en Python 3
Chaque tâche manuelle répétitive identifiée au sein du groupe SGDF de La Rochelle DOIT être
automatisée sous forme de script Python 3 clair, autonome et exécutable en ligne de commande (CLI).
Les scripts DOIVENT gérer explicitement les erreurs d'entrée/sortie (fichiers manquants, formats
inattendus, encodages), fournir des messages explicites en français sur la sortie standard ou la
sortie d'erreur, et retourner des codes de sortie standards (zéro en cas de succès, non-zéro en cas
d'échec).

**Justification** : Fiabiliser les opérations administratives récurrentes du groupe scout et réduire
le temps consacré aux manipulations manuelles sujettes aux erreurs humaines.

### IV. Protection des Données Personnelles et Intégrité des Sources
Les scripts manipulent des données personnelles d'adhérents, de jeunes et de parents du groupe
scout (notamment des exports de type `ExportIndividus.xls`). Aucune donnée personnelle nominative
(noms, adresses électroniques, numéros de téléphone, adresses postales) NE DOIT être inscrite en
dur dans le code source ni publiée dans un dépôt distant non sécurisé. Les scripts DOIVENT
traiter les fichiers d'entrée en lecture seule et générer leurs résultats dans des fichiers de
sortie distincts afin de ne jamais altérer ni corrompre les exports originaux.

**Justification** : Respecter la confidentialité des familles du groupe SGDF (conformité RGPD) et
préserver l'intégrité des fichiers d'export issus de l'intranet SGDF.

### V. Simplicité et Maintenabilité pour les Bénévoles
Les solutions implémentées DOIVENT privilégier la simplicité (principe YAGNI), la lisibilité du
code et l'utilisation de la bibliothèque standard Python ou de bibliothèques tierces éprouvées et
strictement nécessaires au traitement des données (comme la lecture de tableurs). Toute abstraction
complexe, architecture sur-dimensionnée ou dépendance superflue DOIT être évitée.

**Justification** : Le renouvellement régulier des équipes de bénévoles au sein d'un groupe scout
impose que le code reste simple à comprendre, à diagnostiquer et à adapter d'une année sur l'autre.

## Contraintes Techniques et Environnement

- **Prérequis de la machine de développement** : La machine hôte est présumée disposer de `direnv`,
  du gestionnaire de paquets Nix (avec les fonctionnalités expérimentales `nix-command` et `flakes`
  activées) et/ou de Jetify Devbox.
- **Exécution et dépendances** : Python 3 et tous les paquets système ou bibliothèques Python
  nécessaires DOIVENT être déclarés dans les fichiers d'environnement (`flake.nix` et/ou
  `devbox.json`) et chargés automatiquement par `direnv` via `.envrc`.
- **Conventions de nommage** : Les fichiers Python (`.py`), la documentation (`.md`), les modules,
  les fonctions, les variables et les arguments CLI DOIVENT utiliser des identifiants en français
  respectant les conventions PEP 8 (`snake_case` en français pour les fichiers, fonctions et
  variables ; `PascalCase` en français pour les classes).

## Flux de Travail et Assurance Qualité

- **Documentation en français** : Chaque script ou fonctionnalité DOIT être accompagné d'instructions
  d'utilisation claires en français expliquant les fichiers d'entrée attendus, les commandes à
  exécuter et les résultats produits.
- **Vérification dans l'environnement éphémère** : Toute exécution, validation ou vérification de
  script DOIT s'effectuer au sein de l'environnement isolé fourni par Nix / Devbox et activé par
  `direnv`.
- **Tests et validation sur données réelles ou anonymisées** : Les traitements DOIVENT être vérifiés
  de bout en bout sur la structure réelle des exports SGDF sans modifier les fichiers sources.

## Governance

Cette constitution prévaut sur toute autre pratique implicite au sein du projet.

- **Procédure d'amendement** : Toute modification de cette constitution DOIT être documentée,
  validée par le responsable du projet et accompagnée d'une mise à jour du numéro de version et de
  la date de dernier amendement.
- **Politique de versionnage** : La constitution suit le versionnage sémantique (`MAJEUR.MINEUR.CORRECTIF`) :
  - **MAJEUR** : Suppression ou redéfinition incompatible d'un principe fondamental ou d'une règle
    de gouvernance.
  - **MINEUR** : Ajout d'un nouveau principe, d'une nouvelle section ou extension substantielle des
    règles existantes.
  - **CORRECTIF** : Clarifications rédactionnelles, corrections typographiques ou précisions sans
    changement sémantique des règles.
- **Revue de conformité** : Toute spécification (`/speckit.specify`), tout plan d'implémentation
  (`/speckit.plan`), toute liste de tâches (`/speckit.tasks`) et toute implémentation
  (`/speckit.implement`) DOIVENT vérifier leur conformité stricte avec les principes de cette
  constitution, en particulier l'usage intégral du français et l'utilisation de l'environnement
  éphémère Nix/Devbox activé par `direnv`.

**Version**: 1.0.0 | **Ratified**: 2026-10-16 | **Last Amended**: 2026-10-16
