# Recherche Technique : Extraction et Regroupement des Contacts des Parents SGDF

**Branche** : `002-extraire-contacts-parents` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Analyse et lecture du fichier `ExportIndividus.xls`

- **Decision** : Analyser `ExportIndividus.xls` à l'aide de `BeautifulSoup` avec le parseur `lxml` en extrayant directement les lignes `<tr>` et cellules `<th>`/`<td>` sous forme de chaînes de caractères (`get_text(strip=True)`).
- **Rationale** : L'export `ExportIndividus.xls` généré par l'intranet SGDF est un document HTML contenant un tableau de 154 lignes (1 ligne d'en-tête de 97 colonnes et 153 lignes de membres). L'extraction directe via `BeautifulSoup(..., "lxml")` garantit que toutes les valeurs textuelles (notamment les numéros de téléphone commençant par `0` comme `06...` ou `05...` et les codes postaux ou numéros d'adhérent) sont lues en tant que texte pur, sans conversion numérique implicite qui supprimerait les zéros de tête.
- **Alternatives considered** :
  - *`pandas.read_html` sans typage explicite* : Convertit par défaut les colonnes de numéros de téléphone et de codes adhérents en entiers ou flottants (`612345678.0`), faisant perdre le `0` initial indispensable pour Google Contacts et WhatsApp.

## 2. Identification des jeunes et enrichissement par les fiches adultes

- **Decision** :
  1. Identifier les **jeunes scouts** par le critère `Fonction.CategorieMembre == "0"` (qui regroupe les codes `170` Farfadets, `110` Louveteaux/Jeannettes, `120` Scouts/Guides, `130` Pionniers/Caravelles et `140` Compagnons, soit 95 jeunes au total : 74 `Inscrit(e)`, 18 `Invité(e)` et 3 `Pré-inscrit(e)`).
  2. Identifier les **inscriptions adultes** par `Fonction.CategorieMembre != "0"` (58 lignes) et indexer leurs informations par clé `(Nom normalisé, Prénom normalisé)` afin d'enrichir automatiquement les fiches des parents correspondants (32 parents concernés dans l'export, dont les 18 Parents Animateurs Farfadets) avec :
     - leur `Individu.CodeAdherent` (si `RepresentantLegalX.CodeAdherent` n'est pas déjà renseigné),
     - leur fonction adulte accordée selon la civilité (`Fonction.NomFeminin` si `IndividuCivilite.NomCourt == "Mme"`, sinon `Fonction.NomMasculin`), normalisée de façon lisible (ex. `Parent Animateur Farfadet`), ainsi que toute délégation éventuelle (`Inscription.Delegations`).
- **Rationale** : Dans l'export SGDF, lorsqu'un parent a un rôle dans le groupe (ex. `271 - PARENT ANIMATEUR FARFADET`), cette fonction n'apparaît pas dans les colonnes `RepresentantLegal1.*` de la ligne de l'enfant, mais sur une ligne séparée où le parent est lui-même `Individu` adulte. Le croisement par `(Nom, Prénom)` permet de renseigner automatiquement les 32 parents bénévoles sans saisie manuelle (`SC-003`).
- **Alternatives considered** :
  - *Lire uniquement les colonnes `RepresentantLegal1..3`* : Rejeté car cela laisserait la colonne `Remarques` vide pour les Parents Animateurs Farfadets et les responsables de groupe.

## 3. Normalisation des noms, prénoms, unités et tri alphabétique français

- **Decision** :
  - **Nom du parent** : Nettoyage des espaces superflus et conversion en majuscules (`str.upper()`).
  - **Prénom du parent** : Mise en minuscules avec majuscule initiale sur chaque composant séparé par un espace, un tiret `-` ou une apostrophe `'` (ex. `jean-pierre` → `Jean-Pierre`, `marie claire` → `Marie Claire`).
  - **Unités courtes** : Correspondance déterministe depuis `Structure.Nom` ou `Fonction.Code` vers les 5 libellés courts validés lors de la clarification :
    - `170` / `FARFADET` → `Farfadets`
    - `110` / `LOUVETEAUX` → `Louveteaux-Jeannettes`
    - `120` / `SCOUTS GUIDES` → `Scouts-Guides`
    - `130` / `PIONNIERS` → `Pionniers-Caravelles`
    - `140` / `COMPAGNONS` → `Compagnons`
  - **Tri alphabétique** : Tri primaire sur `Nom` puis secondaire sur `Prénom` en utilisant une clé de tri normalisée sans accents (`unicodedata.normalize("NFD", ...)` filtrant les marques diacritiques `Mn`) suivie de la chaîne originale en départage.
- **Rationale** : En Python, le tri Unicode brut place `É` (code 201) après `Z` (code 90). L'utilisation d'une clé de tri désaccentuée garantit l'ordre alphabétique français attendu (`ÉLODIE` trié avec `E`, `Ç` avec `C`) indépendamment des paramètres régionaux (`locale`) installés sur le système hôte.
- **Alternatives considered** :
  - *`locale.strxfrm` avec `fr_FR.UTF-8`* : Rejeté car dans un environnement Nix éphémère minimal, la locale `fr_FR.UTF-8` peut ne pas être générée par défaut, ce qui provoquerait une erreur `locale.Error`.

## 4. Génération du classeur Excel `ContactsParents.xlsx` multi-onglets

- **Decision** : Utiliser `openpyxl` pour générer le classeur `ContactsParents.xlsx` contenant :
  1. Un premier onglet `ExportIndividus` reproduisant fidèlement l'en-tête et les 153 lignes de `ExportIndividus.xls` au format texte.
  2. Un second onglet `ContactsParents` contenant les 11 colonnes demandées, avec formatage explicite de toutes les cellules en texte (`@`) pour préserver les zéros initiaux des numéros de téléphone et codes adhérents, figeage de la ligne d'en-tête et ajustement automatique de la largeur des colonnes.
- **Rationale** : Répond exactement à la clarification `FR-007` tout en produisant un fichier `.xlsx` propre et immédiatement lisible dans LibreOffice Calc, Microsoft Excel ou Google Sheets.
- **Alternatives considered** :
  - *Écriture CSV seule* : Rejeté car ne permet pas d'avoir un onglet nommé `ContactsParents` aux côtés de l'onglet `ExportIndividus`.
