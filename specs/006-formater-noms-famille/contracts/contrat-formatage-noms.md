# Contrat d'Interface : Formatage des Noms de Famille dans `ContactsParents.xlsx` et `ContactParents.vcf`

**Branche** : `006-formater-noms-famille` | **Date** : 2026-10-23 | **Spécification** : [spec.md](../spec.md)

## 1. Contrat des Colonnes `Nom` et `Noms des enfants` dans `ContactsParents.xlsx`

Le schéma à 13 colonnes de l'onglet `ContactsParents` reste identique dans ses intitulés et son ordre, avec les règles de formatage suivantes sur les colonnes portant des noms de famille :

1. **Colonne 1 — `Nom`** :
   - Contient le nom de famille du parent normalisé en minuscules avec la première lettre de chaque mot ou segment (séparé par un espace, un trait d'union `-` ou une apostrophe `'`) en majuscule.
   - Exemples : `Bernard`, `Dupont-Moretti`, `Le Goff`, `D'Artagnan`, `Évrard`.
2. **Colonne 2 — `Prénom`** *(inchangé)* :
   - Contient le prénom du parent normalisé selon la même règle (ex. `Jean-Pierre`, `Élodie`).
3. **Colonne 7 — `Noms des enfants`** :
   - Contient la liste dédoublonnée des enfants rattachés au parent, séparés par `, `, où chaque enfant est formaté sous la forme `Prénom Nom` avec le prénom et le nom de famille tous deux en casse titre.
   - Exemples : `Lucas Bernard, Chloé Bernard`, `Tom Martin`, `Léa Dupont`.
4. **Onglet `ExportIndividus`** *(inchangé)* :
   - Conserve la copie tabulaire brute de `ExportIndividus.xls` sans reformatage de la casse d'origine.

## 2. Contrat des Champs `N`, `FN` et `NOTE` dans `ContactParents.vcf`

Dans chaque bloc `VCARD` 3.0 généré par `generate_contacts_vcf.py` à partir de `ContactsParents.xlsx` :

```vcard
BEGIN:VCARD
VERSION:3.0
N:Dupont;Jean-Pierre;;;
FN:Jean-Pierre Dupont
TEL;TYPE=CELL,VOICE,PREF:+33612345678
ADR;TYPE=HOME:;;12 Rue Des Mouettes;La Rochelle;;17000;
NOTE:Enfants : Lucas Dupont (Farfadets)\, Emma Dupont (Louveteaux-Jeannettes)\nNuméro d'adhérent : 123456789\nRemarques : Parent Animateur Farfadet
CATEGORIES:SGDF,La Rochelle
END:VCARD
```

- **`N`** : `<Nom en casse titre>;<Prénom en casse titre>;;;`
- **`FN`** : `<Prénom en casse titre> <Nom en casse titre>`
- **`NOTE` (rubrique `Enfants`)** : `Enfants : <Prénom Enfant> <Nom Enfant> (<Unité>)\, ...`
