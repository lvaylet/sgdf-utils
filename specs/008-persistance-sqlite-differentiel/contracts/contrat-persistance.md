# Contrat d'Interface : Persistance SQLite (`sgdf_contacts.persistence`)

**Feature**: `008-persistance-sqlite-differentiel` | **Date**: 2026-10-26

## 1. Module `sgdf_contacts.persistence.models`

Expose les modèles SQLModel et la configuration du moteur SQLite/SQLAlchemy :

```python
def create_db_engine(
    database_url: str | Path = "sqlite:///sgdf_contacts.db",
    *,
    echo: bool = False,
) -> Engine:
    """Crée un moteur SQLAlchemy/SQLModel et active automatiquement `PRAGMA journal_mode=WAL;`
    et `PRAGMA foreign_keys=ON;` sur chaque connexion SQLite."""

def init_db(engine: Engine) -> None:
    """Crée les tables `parents`, `children` et `parent_child_links` si elles n'existent pas."""
```

Entités exposées :
- `ParentRecord` (`__tablename__ = "parents"`)
- `ChildRecord` (`__tablename__ = "children"`)
- `ParentChildLink` (`__tablename__ = "parent_child_links"`)

## 2. Module `sgdf_contacts.persistence.repository`

Expose les structures de rapport de différentiel et le dépôt `ParentContactRepository` :

```python
@dataclass(frozen=True)
class FieldChange:
    """Détail d'un champ modifié sur une fiche parent lors d'un import."""
    old_value: Any
    new_value: Any

@dataclass(frozen=True)
class ParentUpdateDiff:
    """Parent mis à jour avec le dictionnaire des champs modifiés."""
    parent: ParentContact
    changes: dict[str, FieldChange]

@dataclass
class ImportDiffReport:
    """Rapport de différentiel produit par une synchronisation transactionnelle."""
    created: list[ParentContact]
    updated: list[ParentUpdateDiff]
    unchanged: list[ParentContact]
    deactivated: list[ParentContact]
```

### Classe `ParentContactRepository`

```python
class ParentContactRepository:
    def __init__(self, engine: Engine) -> None: ...

    def sync_parents(self, parents: Sequence[ParentContact]) -> ImportDiffReport:
        """Synchronise de façon transactionnelle une liste de `ParentContact` en base et retourne
        le rapport de différentiel (`created`, `updated`, `unchanged`, `deactivated`)."""

    def import_individuals_xls(self, source: Path | bytes | BinaryIO) -> ImportDiffReport:
        """Extrait les parents d'un export `ExportIndividus.xls` (chemin ou flux mémoire) et
        les synchronise en base en retournant le `ImportDiffReport`."""

    def list_active_parents(self) -> list[ParentContact]:
        """Retourne tous les parents actifs (`is_active=True`) triés selon l'ordre alphabétique français."""

    def filter_parents(
        self,
        *,
        short_unit: str | None = None,
        registration_status: str | None = None,
        has_valid_mobile: bool | None = None,
        include_inactive: bool = False,
    ) -> list[ParentContact]:
        """Filtre les parents selon l'unité d'enfant, le statut d'inscription d'enfant et/ou
        la présence d'un numéro de téléphone portable valide."""

    def find_by_phone(
        self,
        phone: str,
        *,
        include_inactive: bool = False,
    ) -> ParentContact | None:
        """Recherche un parent par numéro de téléphone (`primary_mobile_phone`,
        `secondary_mobile_phone` ou `landline_phone`), normalisé automatiquement."""

    def set_whatsapp_status(
        self,
        last_name: str,
        first_name: str,
        has_whatsapp: bool | None,
    ) -> bool:
        """Met à jour la métadonnée externe `has_whatsapp` d'un parent identifié par `(last_name, first_name)`."""

    def export_vcf(
        self,
        output_path: Path | None = None,
        *,
        categories: tuple[str, ...] = DEFAULT_CATEGORIES,
    ) -> str:
        """Régénère `ContactParents.vcf` (sur disque et/ou en mémoire) directement depuis les parents actifs de la base."""

    def export_excel(
        self,
        output_path: Path | BinaryIO | None = None,
        *,
        source_headers: list[str] | None = None,
        source_rows: list[list[str]] | None = None,
    ) -> bytes:
        """Régénère `ContactsParents.xlsx` (sur disque et/ou en mémoire) directement depuis les parents actifs de la base."""
```

## 3. Ré-exports dans `sgdf_contacts` et `sgdf_contacts.persistence`

Tous les symboles ci-dessus (`ParentRecord`, `ChildRecord`, `ParentChildLink`, `FieldChange`, `ParentUpdateDiff`, `ImportDiffReport`, `ParentContactRepository`, `create_db_engine`, `init_db`) sont exposés dans `sgdf_contacts.persistence` ainsi qu'à la racine du package `sgdf_contacts`.
