<!--
Sync Impact Report
- Version change: 1.0.0 → 2.0.0
- Modified principles:
  - I. Usage Intégral du Français (NON-NÉGOCIABLE) → I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)
- Modified sections:
  - Contraintes Techniques et Environnement (identifiants de code en anglais selon PEP 8, commentaires et README.md en français)
  - Flux de Travail et Assurance Qualité (référence à README.md pour la documentation en français)
  - Governance (mise à jour de la revue de conformité sur la répartition anglais/français)
- Added sections: Aucune
- Removed sections: Aucune
- Follow-up TODOs: Aucun
-->
# Automatisation SGDF La Rochelle (Contacts Parents) Constitution

## Core Principles

### I. Code en Anglais et Documentation en Français (NON-NÉGOCIABLE)

L'intégralité du code source du projet DOIT être rédigée en langue anglaise. Cette règle s'applique
sans exception à tous les identifiants du code : noms de variables, de fonctions, de méthodes, de
classes, de constantes, de paramètres et de modules Python. En revanche, le reste de la base de code
et des écrits du projet DOIT rester rédigé en français : cela inclut les commentaires dans le code
(ainsi que les docstrings), la documentation (dont le fichier principal nommé `README.md`), les
spécifications, les messages de validation (commits) et les messages affichés à l'utilisateur.

**Justification** : Aligner le code source sur les standards universels de l'écosystème Python tout
en garantissant une compréhension immédiate, homogène et sans barrière linguistique des explications,
commentaires et documentations pour tous les bénévoles et responsables du groupe scout SGDF de
La Rochelle.

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
- **Conventions de nommage et de langue** : Les identifiants dans le code Python (modules, fichiers
  `.py`, fonctions, méthodes, variables, constantes, paramètres et classes) DOIVENT être rédigés en
  anglais et respecter les conventions PEP 8 (`snake_case` en anglais pour les fichiers, fonctions
  et variables ; `PascalCase` en anglais pour les classes ; `UPPER_SNAKE_CASE` en anglais pour les
  constantes). Les commentaires dans le code et la documentation DOIVENT être rédigés en français,
  et le fichier principal de documentation à la racine du dépôt DOIT être nommé `README.md`.

## Flux de Travail et Assurance Qualité

- **Documentation en français** : Le fichier `README.md` et toute documentation associée DOIVENT
  fournir des instructions d'utilisation claires en français expliquant les fichiers d'entrée
  attendus, les commandes à exécuter et les résultats produits.
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
  constitution, en particulier la rédaction du code en anglais, le maintien des commentaires et de
  la documentation (`README.md`) en français, et l'utilisation de l'environnement éphémère
  Nix/Devbox activé par `direnv`.

**Version**: 2.0.0 | **Ratified**: 2026-10-16 | **Last Amended**: 2026-10-16
