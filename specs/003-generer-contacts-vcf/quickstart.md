# Guide de Démarrage et de Validation Rapide (`quickstart.md`)

**Branche** : `003-generer-contacts-vcf` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

Ce guide décrit les étapes permettant de générer le fichier `ContactParents.vcf` à partir de `ContactsParents.xlsx` et de vérifier sa conformité pour l'importation dans Google Contacts.

## 1. Prérequis

- Se placer dans le dossier du projet afin que `direnv` active automatiquement l'environnement éphémère Python 3 (`flake.nix` ou `devbox.json`).
- Disposer du fichier `ContactsParents.xlsx` (contenant l'onglet `ContactsParents`) à la racine du projet. Si ce fichier n'a pas encore été généré, exécuter au préalable :

  ```bash
  python3 extraire_contacts_parents.py
  ```

## 2. Exécution standard du script

Lancer le script sans argument pour lire `ContactsParents.xlsx` (onglet `ContactsParents`) et créer `ContactParents.vcf` :

```bash
python3 generer_contacts_vcf.py
```

**Résultat attendu** :

- Affichage d'un message de confirmation en français sur la sortie standard indiquant le nombre de fiches de parents exportées dans `ContactParents.vcf`.
- Création du fichier `ContactParents.vcf` à la racine du projet.
- Le fichier d'entrée `ContactsParents.xlsx` demeure strictement intact (lecture seule).

## 3. Exécution avec chemins personnalisés

```bash
python3 generer_contacts_vcf.py --entree ContactsParents.xlsx --sortie sorties/ContactParents.vcf
```

## 4. Importation dans Google Contacts

1. Ouvrir [Google Contacts](https://contacts.google.com/).
2. Cliquer sur **Importer** dans le menu latéral gauche.
3. Sélectionner le fichier `ContactParents.vcf` généré.
4. Vérifier que les parents sont importés avec leurs numéros de téléphone, adresse email, adresse postale, la note contenant les enfants et leurs unités (ainsi que le numéro d'adhérent et les remarques éventuelles), et les deux libellés **`SGDF`** et **`La Rochelle`**.

## 5. Validation automatisée (Tests et Qualité)

Exécuter la suite de tests automatisés et le vérificateur de style :

```bash
pytest -v
ruff check .
```

**Critères vérifiés par les tests** :

- Lecture exclusive de l'onglet `ContactsParents` de `ContactsParents.xlsx` en lecture seule (empreinte SHA-256 intacte).
- Génération des 134 fiches `BEGIN:VCARD` / `END:VCARD` correspondant aux 134 parents de l'onglet `ContactsParents`.
- Formatage `N:NOM;Prénom;;;` et `FN:Prénom NOM`.
- Présence des téléphones non vides (`CELL,VOICE,PREF`, `CELL,VOICE`, `HOME,VOICE`), de l'adresse email et de l'adresse physique.
- Structuration de la note (`Enfants : Prénom NOM (Unité), ...`, `Numéro d'adhérent : ...` si présent, `Remarques : ...` si présentes) et absence de lignes vides.
- Présence systématique de `CATEGORIES:SGDF,La Rochelle` sur toutes les fiches.
