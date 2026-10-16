# Contrat d'Interface : Schéma à 13 Colonnes (`ContactsParents`) et Propriété `ADR` (`ContactParents.vcf`)

**Branche** : `004-conserver-parties-adresse` | **Date** : 2026-10-16 | **Spécification** : [spec.md](../spec.md)

## 1. Contrat de l'Onglet `ContactsParents` dans `ContactsParents.xlsx`

L'onglet `ContactsParents` généré par `extraire_contacts_parents.py` et lu par `generer_contacts_vcf.py` DOIT comporter exactement les **13 en-têtes de colonnes** suivants dans cet ordre :

```python
EN_TETES_CONTACTS_PARENTS: tuple[str, ...] = (
    "Nom",
    "Prénom",
    "Téléphone portable principal",
    "Téléphone portable secondaire",
    "Téléphone fixe (domicile)",
    "Adresse email",
    "Noms des enfants",
    "Unités des enfants",
    "Rue",
    "Code postal",
    "Ville",
    "Numéro d'adhérent",
    "Remarques",
)
```

### Règles sur les colonnes d'adresse (`Rue`, `Code postal`, `Ville`)

1. **`Rue`** (colonne 9) : Contient les valeurs non vides de `Adresse.Ligne1`, `Adresse.Ligne2` et `Adresse.Ligne3` normalisées en casse titre (minuscules, sauf la première lettre de chaque mot) et jointes par `, ` (ex. `10 Rue Du Port, Bâtiment B`).
2. **`Code postal`** (colonne 10) : Contient la valeur nettoyée de `Adresse.CodePostal` au format texte (`@`) afin de préserver tout zéro initial éventuel.
3. **`Ville`** (colonne 11) : Contient la valeur de `Adresse.Municipalite` normalisée en casse titre (minuscules, sauf la première lettre de chaque mot, ex. `La Rochelle`).
4. **Absence de colonne `Pays`** : Le champ `Adresse.Pays` est omis dès l'extraction.

## 2. Contrat de Génération de la Propriété `ADR` dans `ContactParents.vcf`

- Lorsque ` bool(rue or code_postal or ville) ` est vrai :

  ```vcard
  ADR;TYPE=HOME:;;<rue_echappee>;<ville_echappee>;;<code_postal_echappe>;
  ```

  où `<rue_echappee>`, `<ville_echappee>` et `<code_postal_echappe>` sont obtenus en appliquant `echapper_valeur_vcard()` directement aux valeurs des colonnes `Rue`, `Ville` et `Code postal`, sans aucun découpage préalable.
- Lorsque `rue`, `code_postal` et `ville` sont tous trois vides :
  - Aucune ligne `ADR` n'est émise dans le bloc `VCARD`.

### Exemple avec plusieurs lignes de rue

Si dans `ContactsParents.xlsx` :

- `Rue` = `10 Rue du Port, Bâtiment B`
- `Code postal` = `17000`
- `Ville` = `LA ROCHELLE`

Alors dans `ContactParents.vcf` :

```vcard
ADR;TYPE=HOME:;;10 Rue du Port\, Bâtiment B;LA ROCHELLE;;17000;
```
