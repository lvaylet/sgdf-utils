<!--
Sync Impact Report
- Version change: 2.0.0 → 2.1.0
- Modified principles: Aucun principe existant renommé
- Added sections / principles:
  - VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)
- Modified sections:
  - Contraintes Techniques et Environnement (ajout de Git et de la CLI GitHub `gh`)
  - Flux de Travail et Assurance Qualité (ajout du flux de branche dédiée, commits, PR via `gh`, approbation manuelle et fusion Squash and Merge par défaut)
  - Governance (vérification du respect du flux par branche et Pull Request)
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

### VI. Flux Git par Branche Dédiée et Pull Request (Squash and Merge)

Tout travail portant sur une fonctionnalité, un correctif ou une évolution DOIT être réalisé dans
une branche Git dédiée créée à partir de la branche principale (`main`). Aucun commit direct sur la
branche principale NE DOIT être effectué. L'agent et les contributeurs SONT AUTORISÉS à enregistrer
des commits sur la branche dédiée, à pousser cette branche vers le dépôt distant et à créer une Pull
Request à l'aide de la CLI GitHub (`gh`). En revanche, l'approbation et la fusion des Pull Requests
DOIVENT demeurer exclusivement manuelles par le responsable du projet : l'agent NE DOIT JAMAIS
approuver ni fusionner lui-même une Pull Request. Les Pull Requests DOIVENT utiliser la méthode de
fusion **Squash and Merge** par défaut.

**Justification** : Garantir une revue humaine systématique avant toute intégration dans `main` tout
en automatisant la préparation des branches et des Pull Requests via `gh`, et conserver un
historique Git propre, atomique et linéaire grâce au *Squash and Merge*.

## Contraintes Techniques et Environnement

- **Prérequis de la machine de développement** : La machine hôte est présumée disposer de `direnv`,
  du gestionnaire de paquets Nix (avec les fonctionnalités expérimentales `nix-command` et `flakes`
  activées) et/ou de Jetify Devbox, ainsi que de `git` et de la CLI GitHub `gh` authentifiée.
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

- **Branches dédiées et Pull Requests (`gh`)** : Chaque fonctionnalité DOIT être développée sur sa
  propre branche dédiée (ex. `NNN-nom-fonctionnalite`). Une fois les vérifications passées, les
  modifications PEUVENT être validées dans un ou plusieurs commits sur cette branche et soumises via
  une Pull Request créée avec `gh pr create`. Le responsable du projet approuve manuellement chaque
  Pull Request et la fusionne selon la méthode **Squash and Merge** par défaut.
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
  la documentation (`README.md`) en français, l'utilisation de l'environnement éphémère Nix/Devbox
  activé par `direnv`, et le respect du travail en branche dédiée avec ouverture de Pull Request via
  `gh` pour approbation manuelle en mode **Squash and Merge**.

**Version**: 2.1.0 | **Ratified**: 2026-10-16 | **Last Amended**: 2026-10-23
