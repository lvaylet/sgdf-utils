# Recherche Technique : Génération du Fichier d'Import Google Contacts (`ContactParents.vcf`)

**Branche** : `003-generer-contacts-vcf` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Lecture en lecture seule du classeur `ContactsParents.xlsx`

- **Decision** : Lire exclusivement l'onglet `ContactsParents` du classeur `ContactsParents.xlsx` via `openpyxl.load_workbook(..., read_only=True, data_only=True)` en vérifiant l'existence préalable du fichier, la présence de l'onglet `ContactsParents` et la conformité des 11 en-têtes de colonnes.
- **Rationale** :
  - Respecte la clarification `FR-001` (exiger l'existence préalable de `ContactsParents.xlsx` et lire uniquement son onglet `ContactsParents`).
  - Permet de prendre en compte d'éventuels ajustements manuels effectués par un bénévole directement dans `ContactsParents.xlsx` avant l'export vers Google Contacts.
  - Utilise `openpyxl` déjà présent dans l'environnement éphémère Nix/Devbox (`flake.nix` et `devbox.json`), sans aucune dépendance externe supplémentaire (Principes II et V de la constitution).
- **Alternatives considered** :
  - *Relire directement `ExportIndividus.xls`* : Rejeté lors de la clarification `FR-001` afin de découpler clairement l'étape d'extraction/consolidation Excel (`extraire_contacts_parents.py`) de l'étape de génération vCard (`generer_contacts_vcf.py`).

## 2. Choix du format vCard 3.0 (RFC 2426) pour Google Contacts

- **Decision** : Générer un fichier `ContactParents.vcf` conforme à la spécification **vCard 3.0 (RFC 2426)** encodé en **UTF-8** à l'aide de la bibliothèque standard Python (sans bibliothèque tierce additionnelle).
- **Rationale** :
  - Google Contacts utilise nativement vCard 3.0 pour l'importation et l'exportation de carnets d'adresses.
  - En vCard 3.0, l'encodage UTF-8 est pris en charge nativement sans nécessiter l'encodage `QUOTED-PRINTABLE` de vCard 2.1 (souvent source d'erreurs de décodage d'accents français).
  - La propriété `CATEGORIES:SGDF,La Rochelle` (valeurs séparées par une virgule non échappée selon la RFC 2426 §3.6.1) est interprétée par Google Contacts pour attribuer automatiquement les deux libellés distincts `"SGDF"` et `"La Rochelle"` à chaque contact importé (`FR-008`, `SC-004`).
  - La génération directe en Python pur est triviale (~50 lignes), déterministe, facile à tester unitairement et respecte le principe YAGNI (Principe V de la constitution).
- **Alternatives considered** :
  - *vCard 2.1* : Rejeté car nécessite `CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE` sur chaque champ accentué, ce qui nuit à la lisibilité et à la maintenabilité.
  - *Ajout d'une dépendance externe (`vobject`)* : Rejeté car non présente dans `flake.nix` / `devbox.json` et inutilement complexe pour sérialiser 8 propriétés vCard standards.

## 3. Mapping des champs `ContactsParents` vers les propriétés vCard 3.0

- **Decision** :
  - **Identité (`N` et `FN`)** :
    - `N:<Nom>;<Prénom>;;;` (ex. `N:DUPONT;Jean-Pierre;;;`)
    - `FN:<Prénom> <Nom>` (ex. `FN:Jean-Pierre DUPONT`, conformément à la clarification `FR-003`).
  - **Numéros de téléphone (`TEL`)** :
    - Si `Téléphone portable principal` non vide : `TEL;TYPE=CELL,VOICE,PREF:<numéro>`
    - Si `Téléphone portable secondaire` non vide : `TEL;TYPE=CELL,VOICE:<numéro>`
    - Si `Téléphone fixe (domicile)` non vide : `TEL;TYPE=HOME,VOICE:<numéro>`
  - **Adresse courriel (`EMAIL`)** :
    - Si `Adresse email` non vide : `EMAIL;TYPE=INTERNET,HOME:<email>`
  - **Adresse physique (`ADR`)** :
    - Si `Adresse physique` non vide : extraction structurée `(rue, code_postal, ville, pays)` à partir du format produit par `assembler_adresse_physique` (`<lignes rue>, <CP> <VILLE>[, <PAYS>]`) vers `ADR;TYPE=HOME:;;<rue>;<ville>;;<code_postal>;<pays>`, avec repli en mettant l'adresse complète dans le champ `<rue>` si le format est libre.
  - **Informations complémentaires (`NOTE`)** :
    - Assemblage dans l'ordre validé lors de la clarification `FR-007` (séparé par `\n` échappé en `\\n` dans la ligne `NOTE:` vCard 3.0) :
      1. `Enfants : <Prénom1 NOM1 (Unité1), Prénom2 NOM2 (Unité2), ...>` (si au moins un enfant est renseigné)
      2. `Numéro d'adhérent : <numéro>` (uniquement si non vide)
      3. `Remarques : <remarques>` (uniquement si non vide)
  - **Étiquettes (`CATEGORIES`)** :
    - `CATEGORIES:SGDF,La Rochelle` sur 100 % des fiches.
- **Rationale** : Garantit que Google Contacts reconnaît le type exact de chaque numéro de téléphone (Mobile préféré, Mobile secondaire, Domicile), affiche l'adresse postale de façon structurée, présente les informations complémentaires sur des lignes distinctes dans le champ Note et applique les deux étiquettes `"SGDF"` et `"La Rochelle"`.
- **Alternatives considered** :
  - *Concaténer toutes les notes sur une seule ligne* : Rejeté lors de la clarification `FR-007` au profit d'une ligne par rubrique non vide.

## 4. Règles d'échappement vCard 3.0 et protection RGPD

- **Decision** :
  - Échapper dans les valeurs textuelles vCard (`N`, `FN`, `ADR`, `NOTE`) les caractères réservés selon la RFC 2426 : `\` → `\\`, `;` → `\;`, `,` → `\,` et saut de ligne → `\n`.
  - Ajouter `*.vcf` et `ContactParents.vcf` dans `.gitignore` pour empêcher toute publication accidentelle de données personnelles des familles sur Git (`FR-010`, Principe IV).
- **Rationale** : En vCard 3.0, une virgule ou un point-virgule non échappé dans `NOTE` ou `ADR` est interprété comme un séparateur de valeurs ou de composantes, ce qui tronquerait la liste des enfants ou les remarques séparées par `;` lors de l'import dans Google Contacts.
