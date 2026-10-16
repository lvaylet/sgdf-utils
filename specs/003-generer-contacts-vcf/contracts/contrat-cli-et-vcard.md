# Contrat d'Interface CLI et Format du Fichier `ContactParents.vcf`

**Branche** : `003-generer-contacts-vcf` | **Date** : 2026-10-16 | **Spécification** : [spec.md](../spec.md)

## 1. Interface en Ligne de Commande (CLI)

### Commande d'exécution

```bash
python3 generer_contacts_vcf.py [--entree CHEMIN_ENTREE] [--sortie CHEMIN_SORTIE]
```

### Arguments CLI (intégralement en français)

| Argument | Raccourci | Défaut | Description |
| ---------- | ----------- | -------- | ------------- |
| `--entree` | `-e` | `ContactsParents.xlsx` | Chemin du classeur Excel contenant l'onglet `ContactsParents` (ouvert strictement en lecture seule). |
| `--sortie` | `-s` | `ContactParents.vcf` | Chemin du fichier vCard `.vcf` généré en sortie pour Google Contacts. |
| `--help` | `-h` | — | Affiche l'aide en français et quitte avec le code `0`. |

### Codes de sortie

| Code | Signification | Condition |
| ---- | ------------- | --------- |
| `0` | Succès | Lecture de l'onglet `ContactsParents` terminée, fichier `ContactParents.vcf` généré et résumé affiché en français sur `stdout`. |
| `1` | Erreur d'entrée/sortie ou de validation | Fichier `ContactsParents.xlsx` introuvable, illisible, onglet `ContactsParents` absent ou en-têtes des 11 colonnes invalides (message explicite en français sur `stderr`). |

## 2. Contrat du Fichier vCard Généré (`ContactParents.vcf`)

- **Norme** : vCard 3.0 (RFC 2426)
- **Encodage** : UTF-8 (sans BOM)
- **Fin de ligne** : `\r\n` (CRLF standard RFC 2426)

### Structure type d'une fiche contact dans `ContactParents.vcf`

```vcard
BEGIN:VCARD
VERSION:3.0
N:DUPONT;Jean-Pierre;;;
FN:Jean-Pierre DUPONT
TEL;TYPE=CELL,VOICE,PREF:+33612345678
TEL;TYPE=CELL,VOICE:+33698765432
TEL;TYPE=HOME,VOICE:+33546123456
EMAIL;TYPE=INTERNET,HOME:jean-pierre.dupont@example.fr
ADR;TYPE=HOME:;;12 Rue des Mouettes;LA ROCHELLE;;17000;
NOTE:Enfants : Lucas DUPONT (Farfadets)\, Emma DUPONT (Louveteaux-Jeannettes)\nNuméro d'adhérent : 123456789\nRemarques : Parent Animateur Farfadet \; Enfant Lucas : Invité(e)
CATEGORIES:SGDF,La Rochelle
END:VCARD
```

### Garanties d'invariants sur chaque fiche `VCARD`

1. Délimitée par `BEGIN:VCARD` et `END:VCARD` avec `VERSION:3.0`.
2. Contient toujours `N:`, `FN:` (`Prénom NOM`), `NOTE:` et `CATEGORIES:SGDF,La Rochelle`.
3. N'inclut `TEL`, `EMAIL` et `ADR` que lorsque la coordonnée correspondante est renseignée dans `ContactsParents.xlsx`.
4. Dans `NOTE:`, n'inclut `Numéro d'adhérent : ...` et `Remarques : ...` que lorsque ces colonnes sont non vides pour ce parent.
