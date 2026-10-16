# Modèle de Données : Conservation des Parties Brutes de l'Adresse de Bout en Bout

**Branche** : `004-conserver-parties-adresse` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Entités Métier Mises à Jour

### 1.1. `ProfilAdulteGroupe` (`extraire_contacts_parents.py`)

Représente une inscription adulte (`Fonction.CategorieMembre != "0"`) dans `ExportIndividus.xls` servant à enrichir la fiche d'un parent.

| Champ | Type | Règle de construction / Validation |
| ----- | ---- | ---------------------------------- |
| `nom` | `str` | `Individu.Nom` en MAJUSCULES. |
| `prenom` | `str` | `Individu.Prenom` en Casse Titre. |
| `numero_adherent` | `str` | `Individu.CodeAdherent` (texte). |
| `roles_et_delegations` | `list[str]` | Rôles adultes et délégations accordés selon la civilité. |
| `telephone_portable_1` | `str` | `Individu.TelephonePortable1` normalisé au format `+33...`. |
| `telephone_portable_2` | `str` | `Individu.TelephonePortable2` normalisé au format `+33...`. |
| `telephone_domicile` | `str` | `Individu.TelephoneDomicile` normalisé au format `+33...`. |
| `courriel` | `str` | `Individu.CourrielPersonnel` ou `Individu.CourrielDédiéSGDF`. |
| `rue` | `str` | Regroupement des valeurs non vides de `Individu.Adresse.Ligne1`, `Ligne2` et `Ligne3` normalisées en casse titre (minuscules, première lettre de chaque mot en majuscule) et séparées par `, `. |
| `code_postal` | `str` | Valeur nettoyée et normalisée de `Individu.Adresse.CodePostal`. |
| `ville` | `str` | Valeur de `Individu.Adresse.Municipalite` normalisée en casse titre (ex. `La Rochelle`). |

### 1.2. `ContactParent` (`extraire_contacts_parents.py` → Onglet `ContactsParents` à 13 colonnes)

Représente la fiche consolidée et dédoublonnée d'un parent dans l'onglet `ContactsParents` de `ContactsParents.xlsx`.

| # | Nom de la colonne (`ContactsParents`) | Attribut Python | Contraintes et règles de fusion |
| - | ------------------------------------- | --------------- | ------------------------------- |
| 1 | `Nom` | `nom` | MAJUSCULES. |
| 2 | `Prénom` | `prenom` | Casse Titre. |
| 3 | `Téléphone portable principal` | `telephone_portable_principal` | Format international compact (`+33...`), réorganisé depuis fixe/portable 2 si vide. |
| 4 | `Téléphone portable secondaire` | `telephone_portable_secondaire` | Format international compact (`+33...`). |
| 5 | `Téléphone fixe (domicile)` | `telephone_fixe` | Format international compact (`+33...`). |
| 6 | `Adresse email` | `adresse_email` | Première valeur non vide conservée. |
| 7 | `Noms des enfants` | `noms_enfants` | Liste dédoublonnée `Prénom NOM` séparée par `, `. |
| 8 | `Unités des enfants` | `unites_enfants` | Liste des unités courtes dans le même ordre que les enfants. |
| 9 | `Rue` | `rue` | Lignes `Adresse.Ligne1..3` non vides jointes par `, `. Conservé avec `code_postal` et `ville` comme premier bloc d'adresse non vide. |
| 10 | `Code postal` | `code_postal` | Valeur brute nettoyée de `Adresse.CodePostal`. Conservé au sein du premier bloc d'adresse non vide. |
| 11 | `Ville` | `ville` | Valeur brute nettoyée de `Adresse.Municipalite`. Conservé au sein du premier bloc d'adresse non vide. |
| 12 | `Numéro d'adhérent` | `numero_adherent` | Code adhérent SGDF du parent. |
| 13 | `Remarques` | `remarques` | Rôles adultes et statuts d'enfants `Pré-inscrit(e)` / `Invité(e)` séparés par ` ; `. |

### 1.3. `FicheContactParent` (`generer_contacts_vcf.py` → `ContactParents.vcf`)

Représente une ligne lue depuis les 13 colonnes de l'onglet `ContactsParents` et sa projection directe en fiche vCard 3.0.

| # | Colonne source (`ContactsParents`) | Champ Python | Propriété vCard 3.0 cible | Règle d'affectation |
| - | ---------------------------------- | ------------ | ------------------------- | ------------------- |
| 1 | `Nom` | `nom` | `N` (composante 1) et `FN` | Échappé RFC 2426. |
| 2 | `Prénom` | `prenom` | `N` (composante 2) et `FN` | `FN` = `Prénom NOM`. |
| 3 | `Téléphone portable principal` | `telephone_portable_principal` | `TEL;TYPE=CELL,VOICE,PREF` | Inclus si non vide. |
| 4 | `Téléphone portable secondaire` | `telephone_portable_secondaire` | `TEL;TYPE=CELL,VOICE` | Inclus si non vide. |
| 5 | `Téléphone fixe (domicile)` | `telephone_fixe` | `TEL;TYPE=HOME,VOICE` | Inclus si non vide. |
| 6 | `Adresse email` | `adresse_email` | `EMAIL;TYPE=INTERNET,HOME` | Inclus si non vide. |
| 7 | `Noms des enfants` | `noms_enfants` | `NOTE` (`Enfants : ...`) | Associé par position à `unites_enfants`. |
| 8 | `Unités des enfants` | `unites_enfants` | `NOTE` (`Enfants : ...`) | `Prénom NOM (Unité)`. |
| 9 | `Rue` | `rue` | `ADR;TYPE=HOME` (composante 3 `<rue>`) | Affectation directe (échappée RFC 2426) sans découpage. |
| 10 | `Code postal` | `code_postal` | `ADR;TYPE=HOME` (composante 6 `<code_postal>`) | Affectation directe (échappée RFC 2426). |
| 11 | `Ville` | `ville` | `ADR;TYPE=HOME` (composante 4 `<ville>`) | Affectation directe (échappée RFC 2426). |
| 12 | `Numéro d'adhérent` | `numero_adherent` | `NOTE` (`Numéro d'adhérent : ...`) | Inclus si non vide. |
| 13 | `Remarques` | `remarques` | `NOTE` (`Remarques : ...`) | Inclus si non vide. |
| — | *(Constante)* | `etiquettes` | `CATEGORIES:SGDF,La Rochelle` | Systématique sur 100 % des fiches. |

## 2. Flux de Transformation de l'Adresse de Bout en Bout

```text
[ExportIndividus.xls]
  Adresse.Ligne1, Adresse.Ligne2, Adresse.Ligne3  ──►  assembler_rue()  ──►  Colonne "Rue"
  Adresse.CodePostal                              ────────────────────────►  Colonne "Code postal"
  Adresse.Municipalite                            ────────────────────────►  Colonne "Ville"
  Adresse.Pays ("FRANCE")                         ──►  (omis)
                                                                                   │
                                                                                   ▼
                                                       [ContactsParents.xlsx — Onglet "ContactsParents"]
                                                         Colonnes 9, 10, 11 : "Rue", "Code postal", "Ville"
                                                                                   │
                                                                                   ▼
                                                       [ContactParents.vcf — Propriété vCard 3.0 ADR]
                                                         ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;
```
