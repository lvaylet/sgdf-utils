# Modèle de Données : Génération du Fichier d'Import Google Contacts (`ContactParents.vcf`)

**Branche** : `003-generer-contacts-vcf` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Entités Métier

### 1.1. `LigneContactParent` / `FicheVCardParent`

Représente une ligne lue depuis l'onglet `ContactsParents` du classeur `ContactsParents.xlsx` et sa projection en fiche vCard 3.0 dans `ContactParents.vcf`.

| # | Colonne source (`ContactsParents`) | Champ Python | Propriété vCard 3.0 cible | Règle de validation et de transformation |
|---|------------------------------------|--------------|---------------------------|------------------------------------------|
| 1 | `Nom` | `nom` | `N` (composante 1) et `FN` | Obligatoire (au moins `nom` ou `prenom` non vide). Conservé en MAJUSCULES. |
| 2 | `Prénom` | `prenom` | `N` (composante 2) et `FN` | Conservé en Casse Titre. Nom affiché `FN` = `f"{prenom} {nom}".strip()`. |
| 3 | `Téléphone portable principal` | `telephone_portable_principal` | `TEL;TYPE=CELL,VOICE,PREF` | Inclus uniquement si non vide. |
| 4 | `Téléphone portable secondaire` | `telephone_portable_secondaire` | `TEL;TYPE=CELL,VOICE` | Inclus uniquement si non vide. |
| 5 | `Téléphone fixe (domicile)` | `telephone_fixe` | `TEL;TYPE=HOME,VOICE` | Inclus uniquement si non vide. |
| 6 | `Adresse email` | `adresse_email` | `EMAIL;TYPE=INTERNET,HOME` | Inclus uniquement si non vide. |
| 7 | `Noms des enfants` | `noms_enfants` | `NOTE` (ligne `Enfants : ...`) | Liste séparée par `, ` associée par position à `unites_enfants`. |
| 8 | `Unités des enfants` | `unites_enfants` | `NOTE` (ligne `Enfants : ...`) | Liste séparée par `, ` associée par position à `noms_enfants` sous la forme `Prénom NOM (Unité)`. |
| 9 | `Adresse physique` | `adresse_physique` | `ADR;TYPE=HOME` | Inclus uniquement si non vide. Décomposé en `(rue, ville, code_postal, pays)` si possible, sinon placé dans `<rue>`. |
| 10 | `Numéro d'adhérent` | `numero_adherent` | `NOTE` (ligne `Numéro d'adhérent : ...`) | Inclus dans `NOTE` uniquement si non vide. |
| 11 | `Remarques` | `remarques` | `NOTE` (ligne `Remarques : ...`) | Inclus dans `NOTE` uniquement si non vide. |
| — | *(Constante métier)* | `etiquettes` | `CATEGORIES:SGDF,La Rochelle` | Toujours égal à `("SGDF", "La Rochelle")` pour 100 % des parents (`FR-008`). |

### 1.2. Règle d'assemblage des informations complémentaires (`NOTE`)

Le contenu du champ `NOTE` d'un parent est construit à partir des trois rubriques suivantes, dans cet ordre strict, en omettant toute rubrique vide (`FR-007`) :

1. **Ligne Enfants et Unités** :
   - Découper `noms_enfants` sur `,` → `[e_1, e_2, ...]`
   - Découper `unites_enfants` sur `,` → `[u_1, u_2, ...]`
   - Pour chaque enfant `e_i` :
     - Si `i < len(unites)` et `u_i` non vide : `f"{e_i} ({u_i})"`
     - Sinon si `len(unites) == 1` et `u_0` non vide : `f"{e_i} ({u_0})"`
     - Sinon : `f"{e_i}"`
   - Produire la ligne : `Enfants : < éléments joints par ", " >`
2. **Ligne Numéro d'adhérent** (uniquement si `numero_adherent` est non vide) :
   - `Numéro d'adhérent : <numero_adherent>`
3. **Ligne Remarques** (uniquement si `remarques` est non vide) :
   - `Remarques : <remarques>`

Les lignes retenues sont jointes par un retour à la ligne (`\n`), puis échappées selon la norme vCard 3.0 (`\n` → `\\n`, `,` → `\\,`, `;` → `\\;`).

## 2. Flux de Transformation des Données

```text
[ContactsParents.xlsx — Onglet "ContactsParents" (134 lignes, lecture seule)]
         │
         ▼
Validation de l'existence du fichier, de l'onglet "ContactsParents" et des 11 en-têtes
         │
         ▼
Transformation de chaque ligne en FicheVCardParent :
  - Identité : N:NOM;Prénom;;; et FN:Prénom NOM
  - Téléphones non vides : CELL,PREF / CELL / HOME
  - Courriel non vide : EMAIL;TYPE=INTERNET,HOME
  - Adresse postale non vide : ADR;TYPE=HOME
  - Note structurée : Enfants (+ unités) / Numéro d'adhérent (si présent) / Remarques (si présentes)
  - Étiquettes systématiques : CATEGORIES:SGDF,La Rochelle
         │
         ▼
Sérialisation vCard 3.0 (UTF-8, échappement RFC 2426)
         │
         ▼
[ContactParents.vcf (134 fiches vCard prêtes pour l'import Google Contacts)]
```
