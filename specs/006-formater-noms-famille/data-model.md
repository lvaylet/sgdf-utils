# Modèle de Données : Formatage des Noms de Famille en Casse Titre Comme les Prénoms

**Branche** : `006-formater-noms-famille` | **Date** : 2026-10-23 | **Spécification** : [spec.md](./spec.md)

## 1. Règle de Normalisation des Noms de Famille (`normalize_last_name`)

Tout nom de famille extrait de `ExportIndividus.xls` (`Individu.Nom`, `RepresentantLegal1.Nom`, `RepresentantLegal2.Nom`, `RepresentantLegal3.Nom`) suit désormais la même règle que `normalize_first_name` :

1. Suppression des espaces en début/fin et réduction des espaces multiples internes à un seul espace.
2. Conversion de tous les caractères en minuscules.
3. Conversion en majuscule de la première lettre située en début de chaîne ou immédiatement après un espace (` `), un trait d'union (`-`) ou une apostrophe (`'`).

### Exemples de transformation

| Valeur brute dans `ExportIndividus.xls` | Valeur normalisée (`normalize_last_name`) |
| --------------------------------------- | ----------------------------------------- |
| `BERNARD` / `bernard` | `Bernard` |
| `  dupont-moretti ` / `DUPONT-MORETTI` | `Dupont-Moretti` |
| `LE GOFF` / `le   goff` | `Le Goff` |
| `D'ARTAGNAN` / `d'artagnan` | `D'Artagnan` |
| `ÉVRARD` / `évrard` | `Évrard` |
| `""` / `"   "` | `""` |

## 2. Impact sur les Entités du Modèle

### 2.1. `AttachedChild` (`extract_parent_contacts.py`)

| Attribut / Méthode | Type | Format avant | Format après (`006`) |
| ------------------ | ---- | ------------ | -------------------- |
| `first_name` | `str` | Casse titre (`Lucas`, `Chloé`) | Casse titre (`Lucas`, `Chloé`) *(inchangé)* |
| `last_name` | `str` | MAJUSCULES (`BERNARD`) | Casse titre (`Bernard`) |
| `format_full_name()` | `str` | `Prénom NOM` (`Lucas BERNARD`) | `Prénom Nom` (`Lucas Bernard`) |

### 2.2. `AdultGroupProfile` (`extract_parent_contacts.py`)

| Attribut | Type | Format avant | Format après (`006`) |
| -------- | ---- | ------------ | -------------------- |
| `last_name` | `str` | MAJUSCULES (`BERNARD`) | Casse titre (`Bernard`) |
| `first_name` | `str` | Casse titre (`Élodie`) | Casse titre (`Élodie`) *(inchangé)* |
| Clé d'indexation | `tuple[str, str]` | `("BERNARD", "Élodie")` | `("Bernard", "Élodie")` |

### 2.3. `ParentContact` (`extract_parent_contacts.py` → Onglet `ContactsParents`)

| # | Colonne Excel | Attribut / Propriété | Format avant | Format après (`006`) |
| - | ------------- | -------------------- | ------------ | -------------------- |
| 1 | `Nom` | `last_name` | `DUPONT` | `Dupont` |
| 2 | `Prénom` | `first_name` | `Jean-Pierre` | `Jean-Pierre` *(inchangé)* |
| 7 | `Noms des enfants` | `children_names` | `Lucas BERNARD, Chloé BERNARD` | `Lucas Bernard, Chloé Bernard` |

*(Les 10 autres colonnes de l'onglet `ContactsParents` ainsi que l'onglet `ExportIndividus` demeurent inchangés.)*

### 2.4. `ParentContactCard` (`generate_contacts_vcf.py` → `ContactParents.vcf`)

| Propriété vCard 3.0 | Source (`ContactsParents`) | Format avant | Format après (`006`) |
| ------------------- | -------------------------- | ------------ | -------------------- |
| `N` | `last_name`, `first_name` | `N:DUPONT;Jean-Pierre;;;` | `N:Dupont;Jean-Pierre;;;` |
| `FN` | `formatted_full_name` | `FN:Jean-Pierre DUPONT` | `FN:Jean-Pierre Dupont` |
| `NOTE` (ligne Enfants) | `children_names`, `children_units` | `Enfants : Lucas BERNARD (Scouts-Guides), Chloé BERNARD (Farfadets)` | `Enfants : Lucas Bernard (Scouts-Guides), Chloé Bernard (Farfadets)` |
