# Modèle de Données : Extraction et Regroupement des Contacts des Parents SGDF

**Branche** : `002-extraire-contacts-parents` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Entités Métier

### 1.1. `EnfantRattache` (Jeune Scout)

Représente un enfant ou adolescent (`Fonction.CategorieMembre == "0"`) rattaché à un parent.

| Champ | Type | Règle de construction / Validation |
|-------|------|------------------------------------|
| `prenom` | `str` | Prénom du jeune (`Individu.Prenom`) normalisé en casse titre (première lettre de chaque composant en majuscule). |
| `nom` | `str` | Nom de famille du jeune (`Individu.Nom`) normalisé en MAJUSCULES. |
| `unite_courte` | `str` | Unité normalisée parmi : `Farfadets`, `Louveteaux-Jeannettes`, `Scouts-Guides`, `Pionniers-Caravelles`, `Compagnons`. |
| `statut_inscription` | `str` | Valeur de `Inscriptions.Type` (`Inscrit(e)`, `Pré-inscrit(e)` ou `Invité(e)`). |

- **Règle d'affichage du nom de l'enfant** :
  - Si `enfant.nom == parent.nom` : affiché sous la forme `Prénom` (ex. `Léo`).
  - Si `enfant.nom != parent.nom` : affiché sous la forme `Prénom NOM` (ex. `Léo MARTIN`) afin d'éviter toute ambiguïté pour les familles recomposées ou parents portant des noms distincts.

### 1.2. `ProfilAdulteGroupe` (Inscription Adulte SGDF)

Représente une ligne adulte (`Fonction.CategorieMembre != "0"`) dans `ExportIndividus.xls`.

| Champ | Type | Règle de construction / Validation |
|-------|------|------------------------------------|
| `nom` | `str` | `Individu.Nom` en MAJUSCULES. |
| `prenom` | `str` | `Individu.Prenom` en casse titre. |
| `numero_adherent` | `str` | `Individu.CodeAdherent` (chaîne de chiffres préservée intacte). |
| `roles_et_delegations` | `list[str]` | Fonction adulte accordée selon la civilité (`Fonction.NomFeminin` si `Mme`, sinon `Fonction.NomMasculin`) + `Inscription.Delegations` si non vide. |
| `telephone_portable_1` | `str` | `Individu.TelephonePortable1` (repli éventuel si non renseigné sur la fiche représentant légal). |
| `telephone_portable_2` | `str` | `Individu.TelephonePortable2` (repli éventuel). |
| `telephone_domicile` | `str` | `Individu.TelephoneDomicile` (repli éventuel). |
| `courriel` | `str` | `Individu.CourrielPersonnel` ou `Individu.CourrielDédiéSGDF` (repli éventuel). |
| `adresse_physique` | `str` | Adresse postale assemblée (repli éventuel). |

### 1.3. `ContactParent` (Entité Principale de Sortie)

Représente une ligne unique dédoublonnée dans l'onglet `ContactsParents`.

- **Clé d'unicité et de dédoublonnage** : `(nom, prenom)` où `nom` est en MAJUSCULES et `prenom` en casse titre.
- **Ordre de tri** : Croissant sur `(cle_tri_sans_accent(nom), nom, cle_tri_sans_accent(prenom), prenom)`.

| # | Nom de la colonne (`ContactsParents`) | Attribut Python | Contraintes et règles de fusion |
|---|---------------------------------------|-----------------|---------------------------------|
| 1 | `Nom` | `nom` | Non vide, intégralement en MAJUSCULES. |
| 2 | `Prénom` | `prenom` | Non vide, première lettre de chaque partie en majuscule, reste en minuscules. |
| 3 | `Téléphone portable principal` | `telephone_portable_principal` | Texte (`RepresentantLegalX.TelephonePortable1`), première valeur non vide conservée. |
| 4 | `Téléphone portable secondaire` | `telephone_portable_secondaire` | Texte (`RepresentantLegalX.TelephonePortable2`), première valeur non vide conservée. |
| 5 | `Téléphone fixe (domicile)` | `telephone_fixe` | Texte (`RepresentantLegalX.TelephoneDomicile`), première valeur non vide conservée. |
| 6 | `Adresse email` | `adresse_email` | Texte (`RepresentantLegalX.CourrielPersonnel`, ou à défaut `CourrielDédiéSGDF`), première valeur non vide conservée. |
| 7 | `Noms des enfants` | `noms_enfants` | Liste dédoublonnée (ordre d'apparition préservé) séparée par `, `. |
| 8 | `Unités des enfants` | `unites_enfants` | Liste dédoublonnée des unités courtes séparée par `, `, triée selon la progression d'âge SGDF (`Farfadets` → `Louveteaux-Jeannettes` → `Scouts-Guides` → `Pionniers-Caravelles` → `Compagnons`). |
| 9 | `Adresse physique` | `adresse_physique` | Assemblage propre de `Ligne1`, `Ligne2`, `Ligne3`, `CodePostal Municipalite` (et `Pays` si différent de `FRANCE`), première valeur non vide conservée. |
| 10 | `Numéro d'adhérent` | `numero_adherent` | Texte (`RepresentantLegalX.CodeAdherent`, ou à défaut `Individu.CodeAdherent` de la fiche adulte correspondante). |
| 11 | `Remarques` | `remarques` | Liste dédoublonnée séparée par ` ; ` contenant : (a) le(s) rôle(s) adulte(s) du parent dans le groupe (ex. `Parent Animateur Farfadet`, `Responsable de groupe`), et (b) le statut d'inscription de chaque enfant non encore `Inscrit(e)` (ex. `Enfant Léo : Invité(e)` ou `Enfant Emma : Pré-inscrit(e)`). |

## 2. Flux de Transformation des Données

```text
[ExportIndividus.xls (HTML/XLS - 153 lignes)]
         │
         ├──► Onglet 1 : "ExportIndividus" (copie fidèle des 153 lignes)
         │
         ├──► Extraction des lignes adultes (CategorieMembre != "0", 58 lignes)
         │         └──► Index des profils adultes par (Nom, Prénom)
         │
         └──► Extraction des représentants légaux 1, 2, 3 des jeunes (CategorieMembre == "0", 95 lignes)
                   │
                   ▼
         Dédoublonnage et fusion par (Nom, Prénom) (134 parents uniques)
                   │
                   ▼
         Enrichissement avec l'index des profils adultes (Numéro d'adhérent + Remarques rôles)
                   │
                   ▼
         Tri alphabétique français sur (Nom, Prénom)
                   │
                   ▼
         Onglet 2 : "ContactsParents" dans ContactsParents.xlsx
```
