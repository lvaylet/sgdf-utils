# Contrat d'Interface CLI et Structure du Classeur de Sortie

**Branche** : `002-extraire-contacts-parents` | **Date** : 2026-10-16 | **Spécification** : [spec.md](../spec.md)

## 1. Interface en Ligne de Commande (CLI)

### Commande d'exécution

```bash
python3 extraire_contacts_parents.py [--entree CHEMIN_ENTREE] [--sortie CHEMIN_SORTIE]
```

### Arguments CLI (intégralement en français)

| Argument | Raccourci | Défaut | Description |
|----------|-----------|--------|-------------|
| `--entree` | `-e` | `ExportIndividus.xls` | Chemin du fichier d'export SGDF en entrée (ouvert strictement en lecture seule). |
| `--sortie` | `-s` | `ContactsParents.xlsx` | Chemin du classeur Excel `.xlsx` généré en sortie. |
| `--help` | `-h` | — | Affiche l'aide en français et quitte avec le code `0`. |

### Codes de sortie

| Code | Signification | Condition |
|------|---------------|-----------|
| `0` | Succès | Extraction terminée, classeur `ContactsParents.xlsx` généré et résumé affiché en français sur `stdout`. |
| `1` | Erreur d'entrée/sortie ou de format | Fichier d'entrée introuvable, illisible ou structure de colonnes invalide (message explicite en français sur `stderr`). |

## 2. Contrat du Classeur Excel Généré (`ContactsParents.xlsx`)

### Onglets obligatoires

1. **`ExportIndividus`** : Contient les 97 colonnes d'origine et l'intégralité des lignes de `ExportIndividus.xls` sans perte.
2. **`ContactsParents`** : Contient exactement les 11 colonnes suivantes dans cet ordre :

| Indice (1-based) | En-tête exact de la colonne | Format Excel | Exemple de valeur |
|------------------|-----------------------------|--------------|-------------------|
| 1 | `Nom` | Texte (`@`) | `DUPONT` |
| 2 | `Prénom` | Texte (`@`) | `Jean-Pierre` |
| 3 | `Téléphone portable principal` | Texte (`@`) | `0612345678` |
| 4 | `Téléphone portable secondaire` | Texte (`@`) | `0698765432` |
| 5 | `Téléphone fixe (domicile)` | Texte (`@`) | `0546123456` |
| 6 | `Adresse email` | Texte (`@`) | `jean-pierre.dupont@example.fr` |
| 7 | `Noms des enfants` | Texte (`@`) | `Lucas, Emma` |
| 8 | `Unités des enfants` | Texte (`@`) | `Farfadets, Louveteaux-Jeannettes` |
| 9 | `Adresse physique` | Texte (`@`) | `12 Rue des Mouettes, 17000 LA ROCHELLE` |
| 10 | `Numéro d'adhérent` | Texte (`@`) | `123456789` |
| 11 | `Remarques` | Texte (`@`) | `Parent Animateur Farfadet ; Enfant Lucas : Invité(e)` |
