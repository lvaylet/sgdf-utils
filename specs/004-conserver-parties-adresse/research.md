# Recherche Technique : Conservation des Parties Brutes de l'Adresse de Bout en Bout

**Branche** : `004-conserver-parties-adresse` | **Date** : 2026-10-16 | **Spécification** : [spec.md](./spec.md)

## 1. Remplacement de l'assemblage d'adresse complète par le triplet `(Rue, Code postal, Ville)` dans `extraire_contacts_parents.py`

- **Decision** :
  - Supprimer la fonction `assembler_adresse_physique(ligne1, ligne2, ligne3, code_postal, municipalite, pays)` qui concaténait l'ensemble de l'adresse postale en une chaîne unique.
  - La remplacer par une fonction légère `assembler_rue(ligne1: str, ligne2: str, ligne3: str) -> str` qui nettoie et joint par `, ` uniquement les lignes de rue non vides (`Adresse.Ligne1`, `Adresse.Ligne2`, `Adresse.Ligne3`).
  - Conserver séparément `code_postal` (`nettoyer_espaces(val(ligne, "...Adresse.CodePostal"))`) et `ville` (`nettoyer_espaces(val(ligne, "...Adresse.Municipalite"))`) sur `ProfilAdulteGroupe` et `ContactParent`.
  - Ignorer le champ `Adresse.Pays` dès l'extraction conformément à la clarification `FR-001`.
- **Rationale** :
  - Dans `ExportIndividus.xls`, le code postal et la municipalité sont déjà isolés dans des colonnes dédiées (`Adresse.CodePostal` et `Adresse.Municipalite`), et `Adresse.Pays` vaut systématiquement `FRANCE` (ou est vide).
  - En conservant `Rue`, `Code postal` et `Ville` dans 3 attributs et 3 colonnes distincts de l'onglet `ContactsParents`, on élimine la perte de structure qui obligeait ensuite `generer_contacts_vcf.py` à deviner par expression régulière où se trouvaient le code postal et la ville.
- **Alternatives considered** :
  - *Exposer 6 colonnes brutes (`Ligne 1`, `Ligne 2`, `Ligne 3`, `Code postal`, `Municipalité`, `Pays`)* : Écarté lors de la clarification `FR-002` au profit des 3 colonnes `Rue`, `Code postal`, `Ville` directement alignées sur les sous-champs utiles du format vCard `ADR`.

## 2. Règle de fusion atomique du bloc d'adresse lors du dédoublonnage des parents

- **Decision** :
  - Dans `ContactParent.fusionner_coordonnees`, traiter le triplet `(rue, code_postal, ville)` comme un bloc atomique : si le parent ne possède encore aucune composante d'adresse renseignée (`not (self.rue or self.code_postal or self.ville)`) et que la nouvelle occurrence fournit au moins une composante non vide (`rue or code_postal or ville`), copier simultanément `rue`, `code_postal` et `ville`.
- **Rationale** :
  - Garantit qu'en cas d'adresse partielle sur une fiche et complète sur une autre, on ne mélange jamais la rue d'une adresse avec le code postal ou la ville d'une autre fiche (`FR-003`).
- **Alternatives considered** :
  - *Fusionner `rue`, `code_postal` et `ville` indépendamment champ par champ* : Rejeté car cela risquerait de créer une adresse incohérente si deux fiches d'une fratrie avaient des adresses partielles différentes.

## 3. Suppression de `decomposer_adresse_postale` et affectation directe dans `generer_contacts_vcf.py`

- **Decision** :
  - Supprimer intégralement la fonction `decomposer_adresse_postale` et son expression régulière `^(\d{4,5})\s+(.+)$` dans `generer_contacts_vcf.py`.
  - Mettre à jour `EN_TETES_CONTACTS_PARENTS` (13 colonnes) et `FicheContactParent` pour porter directement `rue: str = ""`, `code_postal: str = ""` et `ville: str = ""`.
  - Dans `formater_vcard_parent(fiche)` : lorsque `fiche.rue or fiche.code_postal or fiche.ville` est vrai, écrire directement :
    `ADR;TYPE=HOME:;;{echapper_valeur_vcard(fiche.rue)};{echapper_valeur_vcard(fiche.ville)};;{echapper_valeur_vcard(fiche.code_postal)};`
- **Rationale** :
  - Respecte intégralement `FR-006`, `FR-007` et le Principe V de la constitution (Simplicité et Maintenabilité YAGNI).
  - Élimine tout risque de mauvais découpage lorsqu'une rue contient des virgules (ex. `10 Rue du Port, Bâtiment B` ou `12, rue des Mouettes`) ou qu'un code postal a un format atypique (`SC-002`, `SC-003`).
- **Alternatives considered** :
  - *Conserver `decomposer_adresse_postale` en repli pour d'anciens fichiers Excel à 11 colonnes* : Rejeté car `ContactsParents.xlsx` est un fichier intermédiaire généré par `extraire_contacts_parents.py` et validé strictement par `EN_TETES_CONTACTS_PARENTS` (`FR-005`).
