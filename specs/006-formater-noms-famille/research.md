# Recherche Technique : Formatage des Noms de Famille en Casse Titre Comme les Prénoms

**Branche** : `006-formater-noms-famille` | **Date** : 2026-10-23 | **Spécification** : [spec.md](./spec.md)

## 1. Alignement de `normalize_last_name` sur `normalize_first_name`

- **Decision** :
  - Modifier `normalize_last_name(raw_last_name: str) -> str` dans `extract_parent_contacts.py` pour appliquer exactement la même transformation que `normalize_first_name(raw_first_name: str) -> str` :
    1. Nettoyage des espaces superflus via `clean_whitespace(raw_last_name)` et passage en minuscules (`.lower()`).
    2. Mise en majuscule du premier caractère suivant le début de chaîne, un espace, un trait d'union (`-`) ou une apostrophe (`'`) via l'expression régulière `r"(^|[\s\-'])([^\s\-'])"`.
- **Rationale** :
  - Garantit une cohérence à 100 % entre le formatage des noms de famille et celui des prénoms (« comme les prénoms », `FR-001`).
  - Gère nativement les noms simples (`BERNARD` → `Bernard`), les noms composés avec trait d'union (`DUPONT-MORETTI` → `Dupont-Moretti`), les noms à plusieurs mots ou particules séparés par des espaces (`LE GOFF` → `Le Goff`, `DE LA FONTAINE` → `De La Fontaine`), les noms avec apostrophe (`D'ARTAGNAN` → `D'Artagnan`) et les caractères accentués français (`ÉVRARD` → `Évrard`).
- **Alternatives considered** :
  - *Utiliser `str.title()` de la bibliothèque standard* : Écarté bien que proche en Python 3, car l'expression régulière `r"(^|[\s\-'])([^\s\-'])"` déjà utilisée par `normalize_first_name` contrôle explicitement et uniquement les délimiteurs attendus (début de chaîne, espace, `-`, `'`) et garantit un comportement strictement identique à `normalize_first_name`.

## 2. Propagation automatique aux enfants, au dédoublonnage, à l'enrichissement adulte et au tri

- **Decision** :
  - Conserver les appels existants à `normalize_last_name` dans `build_adult_profiles_index` (ligne 494) et `extract_and_group_parents` (ligne 584 pour `AttachedChild.last_name` et ligne 593 pour `parent_last_name`).
  - Conserver `parent_sort_key(contact)` tel quel (`strip_accents(contact.last_name).upper()` en clé primaire, puis `contact.last_name`, puis le prénom).
- **Rationale** :
  - Comme `build_adult_profiles_index` et `extract_and_group_parents` normalisent tous deux les noms via `normalize_last_name`, la clé de regroupement et de rapprochement `(last_name, first_name)` reste strictement cohérente entre les fiches jeunes (`RepresentantLegal1..3`) et les fiches adultes (`Individu.Nom` / `Individu.Prenom`).
  - `AttachedChild.format_full_name()` assemble `self.first_name` et `self.last_name` : dès lors que `AttachedChild.last_name` est normalisé par `normalize_last_name`, la colonne `Noms des enfants` produit automatiquement `Prénom Nom` (ex. `Lucas Bernard, Chloé Bernard`), qui est ensuite repris tel quel par `generate_contacts_vcf.py` dans `NOTE:Enfants : Lucas Bernard (Scouts-Guides), ...`.
- **Alternatives considered** :
  - *Re-normaliser les noms dans `generate_contacts_vcf.py`* : Inutile (principe YAGNI), car `generate_contacts_vcf.py` lit directement les colonnes `Nom`, `Prénom` et `Noms des enfants` déjà normalisées dans l'onglet `ContactsParents` de `ContactsParents.xlsx`.

## 3. Mise à jour des tests d'intégration sur les fichiers réels

- **Decision** :
  - Mettre à jour les assertions dans `tests/test_extract_parent_contacts.py` et `tests/test_generate_contacts_vcf.py` pour vérifier que `contact.last_name == normalize_last_name(contact.last_name)` (et `contact.last_name != contact.last_name.upper()` pour les noms de plus d'un caractère) au lieu de `contact.last_name == contact.last_name.upper()`.
  - Lors de la phase d'implémentation, régénérer `ContactsParents.xlsx` (et `ContactParents.vcf`) si présents localement afin que le test d'intégration `test_real_contacts_parents_xlsx_integration` vérifie le classeur à jour.
- **Rationale** :
  - Assure que 100 % des tests unitaires et d'intégration sur données synthétiques et réelles valident la nouvelle règle de casse titre (`SC-001` à `SC-004`).
- **Alternatives considered** :
  - *Aucune*.
