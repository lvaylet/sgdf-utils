# Modèle de Données et Correspondance des Identifiants (Phase 1)

## 1. Entités du Script d'Extraction (`extract_parent_contacts.py`)

### 1.1 `AttachedChild` (anciennement `EnfantRattache`)

Représente un jeune scout rattaché à un parent (dataclass immuable `frozen=True`).

| Attribut / Méthode (Anglais) | Ancien nom (Français) | Type | Rôle (commentaires et valeurs métiers en français) |
| ---------------------------- | --------------------- | ---- | -------------------------------------------------- |
| `first_name` | `prenom` | `str` | Prénom de l'enfant en casse titre |
| `last_name` | `nom` | `str` | Nom de famille de l'enfant en MAJUSCULES |
| `short_unit` | `unite_courte` | `str` | Unité courte (`Farfadets`, `Louveteaux-Jeannettes`, etc.) |
| `registration_status` | `statut_inscription` | `str` | Statut d'inscription (`Inscrit(e)`, `Pré-inscrit(e)`, `Invité(e)`) |
| `format_full_name()` | `formater_nom_complet()` | `str` | Retourne `"Prénom NOM"` |

### 1.2 `AdultGroupProfile` (anciennement `ProfilAdulteGroupe`)

Représente l'inscription adulte éventuelle d'un parent dans le groupe SGDF.

| Attribut (Anglais) | Ancien nom (Français) | Type | Rôle |
| ------------------ | --------------------- | ---- | ---- |
| `last_name` | `nom` | `str` | Nom de famille en MAJUSCULES |
| `first_name` | `prenom` | `str` | Prénom en casse titre |
| `member_id` | `numero_adherent` | `str` | Code adhérent SGDF |
| `roles_and_delegations` | `roles_et_delegations` | `list[str]` | Rôles et délégations en français |
| `mobile_phone_1` | `telephone_portable_1` | `str` | Téléphone portable 1 normalisé |
| `mobile_phone_2` | `telephone_portable_2` | `str` | Téléphone portable 2 normalisé |
| `home_phone` | `telephone_domicile` | `str` | Téléphone domicile normalisé |
| `email` | `courriel` | `str` | Courriel personnel ou dédié SGDF |
| `street` | `rue` | `str` | Rue normalisée en casse titre (`Ligne 1..3`) |
| `postal_code` | `code_postal` | `str` | Code postal |
| `city` | `ville` | `str` | Ville normalisée en casse titre |

### 1.3 `ParentContact` (anciennement `ContactParent`)

Représente la fiche consolidée et dédoublonnée d'un parent destinée à l'onglet `ContactsParents`.

| Attribut / Propriété / Méthode (Anglais) | Ancien nom (Français) | Type | Rôle |
| ---------------------------------------- | --------------------- | ---- | ---- |
| `last_name` | `nom` | `str` | Colonne 1 : `Nom` |
| `first_name` | `prenom` | `str` | Colonne 2 : `Prénom` |
| `primary_mobile_phone` | `telephone_portable_principal` | `str` | Colonne 3 : `Téléphone portable principal` |
| `secondary_mobile_phone` | `telephone_portable_secondaire` | `str` | Colonne 4 : `Téléphone portable secondaire` |
| `landline_phone` | `telephone_fixe` | `str` | Colonne 5 : `Téléphone fixe (domicile)` |
| `email_address` | `adresse_email` | `str` | Colonne 6 : `Adresse email` |
| `children` | `enfants` | `list[AttachedChild]` | Liste des enfants rattachés |
| `units` | `unites` | `list[str]` | Liste des unités courtes uniques |
| `street` | `rue` | `str` | Colonne 9 : `Rue` |
| `postal_code` | `code_postal` | `str` | Colonne 10 : `Code postal` |
| `city` | `ville` | `str` | Colonne 11 : `Ville` |
| `member_id` | `numero_adherent` | `str` | Colonne 12 : `Numéro d'adhérent` |
| `notes_list` | `remarques_liste` | `list[str]` | Liste ordonnée des remarques |
| `children_names` (propriété) | `noms_enfants` | `str` | Colonne 7 : `Noms des enfants` |
| `children_units` (propriété) | `unites_enfants` | `str` | Colonne 8 : `Unités des enfants` |
| `notes` (propriété) | `remarques` | `str` | Colonne 13 : `Remarques` |
| `add_child(child)` | `ajouter_enfant(enfant)` | `None` | Ajoute un enfant et son statut éventuel |
| `add_note(note)` | `ajouter_remarque(remarque)` | `None` | Ajoute une remarque sans doublon |
| `merge_contact_info(...)` | `fusionner_coordonnees(...)` | `None` | Fusionne les coordonnées du parent |
| `reorganize_phones()` | `reorganiser_telephones()` | `None` | Promeut un mobile valide vers le portable principal |
| `to_excel_row()` | `vers_ligne_excel()` | `list[str]` | Retourne les 13 valeurs de colonnes dans l'ordre |

---

## 2. Entité du Script de Génération vCard (`generate_contacts_vcf.py`)

### 2.1 `ParentContactCard` (anciennement `FicheContactParent`)

Représente une fiche contact prête à être sérialisée au format vCard 3.0 dans `ContactParents.vcf` (`frozen=True`).

| Attribut / Propriété (Anglais) | Ancien nom (Français) | Type | Rôle |
| ------------------------------ | --------------------- | ---- | ---- |
| `last_name` | `nom` | `str` | Nom de famille (`N:<last_name>;...`) |
| `first_name` | `prenom` | `str` | Prénom (`N:...;<first_name>;...`) |
| `primary_mobile_phone` | `telephone_portable_principal` | `str` | `TEL;TYPE=CELL,VOICE,PREF` |
| `secondary_mobile_phone` | `telephone_portable_secondaire` | `str` | `TEL;TYPE=CELL,VOICE` |
| `landline_phone` | `telephone_fixe` | `str` | `TEL;TYPE=HOME,VOICE` |
| `email_address` | `adresse_email` | `str` | `EMAIL;TYPE=INTERNET,HOME` |
| `children_names` | `noms_enfants` | `str` | Enfants issus de la colonne `Noms des enfants` |
| `children_units` | `unites_enfants` | `str` | Unités issues de la colonne `Unités des enfants` |
| `street` | `rue` | `str` | Sous-champ `<rue>` de `ADR;TYPE=HOME` |
| `postal_code` | `code_postal` | `str` | Sous-champ `<code_postal>` de `ADR;TYPE=HOME` |
| `city` | `ville` | `str` | Sous-champ `<ville>` de `ADR;TYPE=HOME` |
| `member_id` | `numero_adherent` | `str` | Rubrique `Numéro d'adhérent :` de `NOTE` |
| `notes` | `remarques` | `str` | Rubrique `Remarques :` de `NOTE` |
| `categories` | `etiquettes` | `tuple[str, ...]` | `CATEGORIES:SGDF,La Rochelle` |
| `formatted_full_name` (propriété) | `nom_complet_affiche` | `str` | `FN:<Prénom NOM>` |
