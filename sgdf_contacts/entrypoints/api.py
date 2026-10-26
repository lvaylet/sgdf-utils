"""Point d'entrée HTTP REST (`FastAPI`) exposant les contacts parents SGDF pour n8n et WAHA."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import uvicorn
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from sgdf_contacts.domain import (
    AttachedChild,
    ContactExtractionError,
    ParentContact,
    VcfGenerationError,
    is_valid_mobile_phone,
)
from sgdf_contacts.persistence import (
    FieldChange,
    ImportDiffReport,
    ParentContactRepository,
    ParentRecord,
    ParentUpdateDiff,
    create_db_engine,
)

DEFAULT_DATABASE_URL = "sqlite:///sgdf_contacts.db"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

api_key_header_scheme = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Clé d'API requise lorsque la variable d'environnement `SGDF_API_KEY` est définie.",
)


@dataclass(frozen=True)
class ApiSettings:
    """Configuration de l'API HTTP chargée depuis les variables d'environnement `SGDF_*`."""

    database_url: str = DEFAULT_DATABASE_URL
    api_key: str | None = None
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT

    @classmethod
    def from_env(
        cls,
        *,
        database_url: str | Path | None = None,
        api_key: str | None = None,
    ) -> ApiSettings:
        """Construit la configuration à partir des arguments explicites ou des variables d'environnement."""
        resolved_db = (
            str(database_url)
            if database_url is not None
            else os.environ.get("SGDF_DATABASE_URL", DEFAULT_DATABASE_URL).strip()
            or DEFAULT_DATABASE_URL
        )
        raw_api_key = (
            api_key
            if api_key is not None
            else os.environ.get("SGDF_API_KEY")
        )
        resolved_api_key = (
            raw_api_key.strip()
            if raw_api_key is not None and raw_api_key.strip()
            else None
        )
        resolved_host = (
            os.environ.get("SGDF_HOST", DEFAULT_HOST).strip() or DEFAULT_HOST
        )
        raw_port = os.environ.get("SGDF_PORT", str(DEFAULT_PORT)).strip()
        try:
            resolved_port = int(raw_port)
        except ValueError:
            resolved_port = DEFAULT_PORT

        return cls(
            database_url=resolved_db,
            api_key=resolved_api_key,
            host=resolved_host,
            port=resolved_port,
        )


class HealthResponse(BaseModel):
    """Réponse de vérification de l'état de santé du service et de la base SQLite."""

    status: str = Field(default="ok", description="État du service HTTP.")
    database: str = Field(default="ok", description="État de la connexion SQLite.")


class ChildResponse(BaseModel):
    """Représentation d'un enfant rattaché à un parent."""

    first_name: str
    last_name: str
    full_name: str
    short_unit: str
    registration_status: str

    @classmethod
    def from_domain(cls, child: AttachedChild) -> ChildResponse:
        """Construit un `ChildResponse` depuis une entité `AttachedChild` du domaine."""
        return cls(
            first_name=child.first_name,
            last_name=child.last_name,
            full_name=child.format_full_name(),
            short_unit=child.short_unit,
            registration_status=child.registration_status,
        )


class ParentResponse(BaseModel):
    """Représentation complète d'une fiche parent persistée en base."""

    id: int
    member_id: str
    last_name: str
    first_name: str
    full_name: str
    primary_mobile_phone: str
    secondary_mobile_phone: str
    landline_phone: str
    email_address: str
    street: str
    postal_code: str
    city: str
    notes: str
    has_whatsapp: bool | None
    is_active: bool
    first_seen_at: datetime
    updated_at: datetime
    units: list[str]
    children: list[ChildResponse]

    @classmethod
    def from_record(
        cls,
        record: ParentRecord,
        ordered_children: list[AttachedChild],
    ) -> ParentResponse:
        """Construit un `ParentResponse` à partir d'un `ParentRecord` et de ses enfants ordonnés."""
        assert record.id is not None
        domain_parent = record.to_domain(ordered_children)
        return cls(
            id=record.id,
            member_id=record.member_id,
            last_name=record.last_name,
            first_name=record.first_name,
            full_name=format_parent_full_name(record.first_name, record.last_name),
            primary_mobile_phone=record.primary_mobile_phone,
            secondary_mobile_phone=record.secondary_mobile_phone,
            landline_phone=record.landline_phone,
            email_address=record.email_address,
            street=record.street,
            postal_code=record.postal_code,
            city=record.city,
            notes=record.notes,
            has_whatsapp=record.has_whatsapp,
            is_active=record.is_active,
            first_seen_at=record.first_seen_at,
            updated_at=record.updated_at,
            units=domain_parent.units,
            children=[
                ChildResponse.from_domain(child) for child in ordered_children
            ],
        )


class ParentSummaryResponse(BaseModel):
    """Représentation synthétique d'un parent dans le rapport de différentiel d'import."""

    member_id: str
    last_name: str
    first_name: str
    full_name: str
    primary_mobile_phone: str
    secondary_mobile_phone: str
    landline_phone: str
    email_address: str
    street: str
    postal_code: str
    city: str
    notes: str
    units: list[str]
    children: list[ChildResponse]

    @classmethod
    def from_domain(cls, parent: ParentContact) -> ParentSummaryResponse:
        """Construit un `ParentSummaryResponse` depuis une entité `ParentContact` du domaine."""
        return cls(
            member_id=parent.member_id,
            last_name=parent.last_name,
            first_name=parent.first_name,
            full_name=format_parent_full_name(parent.first_name, parent.last_name),
            primary_mobile_phone=parent.primary_mobile_phone,
            secondary_mobile_phone=parent.secondary_mobile_phone,
            landline_phone=parent.landline_phone,
            email_address=parent.email_address,
            street=parent.street,
            postal_code=parent.postal_code,
            city=parent.city,
            notes=parent.notes,
            units=list(parent.units),
            children=[
                ChildResponse.from_domain(child) for child in parent.children
            ],
        )


class FieldChangeResponse(BaseModel):
    """Détail de la modification d'un champ entre l'état précédent et le nouvel import."""

    old_value: Any
    new_value: Any

    @classmethod
    def from_domain(cls, change: FieldChange) -> FieldChangeResponse:
        """Convertit un `FieldChange` (y compris les listes d'`AttachedChild`) en structure sérialisable JSON."""
        return cls(
            old_value=cls._serialize_value(change.old_value),
            new_value=cls._serialize_value(change.new_value),
        )

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, AttachedChild):
            return ChildResponse.from_domain(value).model_dump()
        if isinstance(value, (list, tuple)):
            return [FieldChangeResponse._serialize_value(item) for item in value]
        return value


class ParentUpdateDiffResponse(BaseModel):
    """Représente un parent mis à jour lors d'un import avec le détail de ses champs modifiés."""

    parent: ParentSummaryResponse
    changes: dict[str, FieldChangeResponse]

    @classmethod
    def from_domain(cls, item: ParentUpdateDiff) -> ParentUpdateDiffResponse:
        """Convertit un `ParentUpdateDiff` du dépôt en `ParentUpdateDiffResponse`."""
        return cls(
            parent=ParentSummaryResponse.from_domain(item.parent),
            changes={
                field_name: FieldChangeResponse.from_domain(field_change)
                for field_name, field_change in item.changes.items()
            },
        )


class ImportDiffDetailsResponse(BaseModel):
    """Détail complet des listes de parents créés, mis à jour, inchangés et désactivés."""

    created: list[ParentSummaryResponse]
    updated: list[ParentUpdateDiffResponse]
    unchanged: list[ParentSummaryResponse]
    deactivated: list[ParentSummaryResponse]


class ImportReportResponse(BaseModel):
    """Rapport JSON retourné à l'issue d'un import `POST /api/v1/imports/intranet`."""

    total_parents: int
    created: int
    updated: int
    unchanged: int
    deactivated: int
    changes: ImportDiffDetailsResponse

    @classmethod
    def from_report(cls, report: ImportDiffReport) -> ImportReportResponse:
        """Construit la réponse JSON complète à partir d'un `ImportDiffReport`."""
        created_count = len(report.created)
        updated_count = len(report.updated)
        unchanged_count = len(report.unchanged)
        deactivated_count = len(report.deactivated)
        return cls(
            total_parents=created_count + updated_count + unchanged_count,
            created=created_count,
            updated=updated_count,
            unchanged=unchanged_count,
            deactivated=deactivated_count,
            changes=ImportDiffDetailsResponse(
                created=[
                    ParentSummaryResponse.from_domain(p) for p in report.created
                ],
                updated=[
                    ParentUpdateDiffResponse.from_domain(u)
                    for u in report.updated
                ],
                unchanged=[
                    ParentSummaryResponse.from_domain(p)
                    for p in report.unchanged
                ],
                deactivated=[
                    ParentSummaryResponse.from_domain(p)
                    for p in report.deactivated
                ],
            ),
        )


class WhatsAppRecipientResponse(BaseModel):
    """Destinataire WhatsApp d'une unité scoute formaté pour WAHA et n8n."""

    parent_id: int
    first_name: str
    last_name: str
    full_name: str
    phone_e164: str
    waha_chat_id: str
    has_whatsapp: bool | None
    children: list[ChildResponse]


class ParentPatchRequest(BaseModel):
    """Corps de requête JSON pour la mise à jour partielle des métadonnées d'un parent."""

    has_whatsapp: bool | None = Field(
        default=None,
        description="Indicateur de présence du parent sur WhatsApp (`true`, `false` ou `null`).",
    )


def format_parent_full_name(first_name: str, last_name: str) -> str:
    """Formate le nom complet d'un parent sous la forme 'Prénom Nom'."""
    return " ".join(part for part in (first_name, last_name) if part)


def format_waha_chat_id(phone_e164: str) -> str:
    """Convertit un numéro mobile E.164 (`+33687966975`) en identifiant WAHA (`33687966975@c.us`)."""
    digits = phone_e164.strip().lstrip("+")
    return f"{digits}@c.us"


def select_valid_mobile_phone(record: ParentRecord) -> str | None:
    """Sélectionne le premier numéro mobile valide d'un parent (principal puis secondaire)."""
    if is_valid_mobile_phone(record.primary_mobile_phone):
        return record.primary_mobile_phone
    if is_valid_mobile_phone(record.secondary_mobile_phone):
        return record.secondary_mobile_phone
    return None


def get_repository(request: Request) -> ParentContactRepository:
    """Fournit l'instance de `ParentContactRepository` associée à l'application ou à `SGDF_DATABASE_URL`."""
    configured_db_url: str | None = getattr(
        request.app.state, "explicit_database_url", None
    )
    env_db_url = (
        os.environ.get("SGDF_DATABASE_URL", DEFAULT_DATABASE_URL).strip()
        or DEFAULT_DATABASE_URL
    )
    target_db_url = (
        configured_db_url if configured_db_url is not None else env_db_url
    )

    cached_url: str | None = getattr(request.app.state, "cached_database_url", None)
    cached_repo: ParentContactRepository | None = getattr(
        request.app.state, "repository", None
    )
    if cached_repo is not None and cached_url == target_db_url:
        return cached_repo

    engine = create_db_engine(target_db_url)
    repo = ParentContactRepository(engine)
    request.app.state.cached_database_url = target_db_url
    request.app.state.repository = repo
    return repo


RepositoryDep = Annotated[ParentContactRepository, Depends(get_repository)]


def verify_api_key(
    request: Request,
    header_api_key: Annotated[str | None, Depends(api_key_header_scheme)] = None,
) -> None:
    """Vérifie l'en-tête `X-API-Key` lorsque `SGDF_API_KEY` est définie."""
    explicit_api_key: str | None = getattr(
        request.app.state, "explicit_api_key", None
    )
    raw_expected_key = (
        explicit_api_key
        if explicit_api_key is not None
        else os.environ.get("SGDF_API_KEY")
    )
    expected_key = (
        raw_expected_key.strip()
        if raw_expected_key is not None and raw_expected_key.strip()
        else None
    )

    if expected_key is None:
        return

    if header_api_key is None or not header_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé d'API manquante dans l'en-tête X-API-Key.",
        )

    if not secrets.compare_digest(header_api_key.strip(), expected_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé d'API invalide.",
        )


def create_app(
    database_url: str | Path | None = None,
    api_key: str | None = None,
) -> FastAPI:
    """Crée et configure l'application FastAPI exposant les contacts parents SGDF."""
    application = FastAPI(
        title="SGDF La Rochelle - API Contacts Parents",
        description=(
            "API HTTP REST d'import, de consultation et d'export des contacts parents "
            "du groupe scout SGDF de La Rochelle pour n8n et WAHA."
        ),
        version="1.0.0",
    )

    application.state.explicit_database_url = (
        str(database_url) if database_url is not None else None
    )
    application.state.explicit_api_key = api_key
    application.state.cached_database_url = None
    application.state.repository = None

    if database_url is not None:
        initial_url = str(database_url)
        engine = create_db_engine(initial_url)
        application.state.cached_database_url = initial_url
        application.state.repository = ParentContactRepository(engine)

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["Supervision"],
        summary="Vérifie l'état du service et de la connexion SQLite",
    )
    def health_check(
        repository: RepositoryDep,
    ) -> HealthResponse:
        """Vérifie que le serveur répond et que la base de données SQLite est joignable."""
        try:
            is_healthy = repository.check_health()
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Erreur de connexion à la base de données SQLite : {error}",
            ) from error

        if not is_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="La base de données SQLite n'a pas répondu à la vérification d'état.",
            )
        return HealthResponse(status="ok", database="ok")

    v1_router = APIRouter(
        prefix="/api/v1",
        dependencies=[Depends(verify_api_key)],
    )

    @v1_router.post(
        "/imports/intranet",
        response_model=ImportReportResponse,
        tags=["Imports"],
        summary="Importe un fichier ExportIndividus.xls et calcule le différentiel",
    )
    async def import_intranet_export(
        file: Annotated[
            UploadFile,
            File(description="Fichier ExportIndividus.xls issu de l'intranet SGDF."),
        ],
        repository: RepositoryDep,
    ) -> ImportReportResponse:
        """Reçoit un export `ExportIndividus.xls` en multipart, synchronise la base et retourne le différentiel."""
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le fichier téléversé est vide.",
            )

        try:
            diff_report = repository.import_individuals_xls(raw_bytes)
        except (ContactExtractionError, VcfGenerationError) as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Impossible d'analyser le fichier d'export SGDF : {error}",
            ) from error

        return ImportReportResponse.from_report(diff_report)

    @v1_router.get(
        "/parents",
        response_model=list[ParentResponse],
        tags=["Parents"],
        summary="Liste paginée et filtrée des parents",
    )
    def list_parents(
        repository: RepositoryDep,
        unit: Annotated[
            str | None,
            Query(
                description="Filtre par unité scoute (code court comme LJ ou nom comme LOUVETEAUX-JEANNETTES)."
            ),
        ] = None,
        has_mobile: Annotated[
            bool | None,
            Query(
                description="Filtre selon la présence d'un numéro de téléphone mobile valide."
            ),
        ] = None,
        registration_status: Annotated[
            str | None,
            Query(
                description="Filtre selon le statut d'inscription d'au moins un enfant."
            ),
        ] = None,
        active_only: Annotated[
            bool,
            Query(description="Retourne uniquement les parents actifs si vrai."),
        ] = True,
        limit: Annotated[
            int | None,
            Query(ge=1, description="Nombre maximal de parents à retourner."),
        ] = None,
        offset: Annotated[
            int,
            Query(ge=0, description="Indice de départ pour la pagination."),
        ] = 0,
    ) -> list[ParentResponse]:
        """Retourne la liste des parents filtrée et triée par ordre alphabétique français."""
        records_with_children = repository.list_parent_records(
            short_unit=unit,
            registration_status=registration_status,
            has_valid_mobile=has_mobile,
            include_inactive=not active_only,
        )
        sliced = (
            records_with_children[offset : offset + limit]
            if limit is not None
            else records_with_children[offset:]
        )
        return [
            ParentResponse.from_record(record, children)
            for record, children in sliced
        ]

    @v1_router.get(
        "/units/{unit_name}/whatsapp-recipients",
        response_model=list[WhatsAppRecipientResponse],
        tags=["WhatsApp / WAHA"],
        summary="Retourne les destinataires WhatsApp d'une unité formatés pour WAHA",
    )
    def list_unit_whatsapp_recipients(
        unit_name: str,
        repository: RepositoryDep,
    ) -> list[WhatsAppRecipientResponse]:
        """Retourne les parents actifs d'une unité disposant d'un mobile valide avec leur `waha_chat_id`."""
        records_with_children = repository.list_parent_records(
            short_unit=unit_name,
            has_valid_mobile=True,
            include_inactive=False,
        )
        recipients: list[WhatsAppRecipientResponse] = []
        for record, children in records_with_children:
            if record.id is None:
                continue
            mobile_e164 = select_valid_mobile_phone(record)
            if not mobile_e164:
                continue
            recipients.append(
                WhatsAppRecipientResponse(
                    parent_id=record.id,
                    first_name=record.first_name,
                    last_name=record.last_name,
                    full_name=format_parent_full_name(
                        record.first_name, record.last_name
                    ),
                    phone_e164=mobile_e164,
                    waha_chat_id=format_waha_chat_id(mobile_e164),
                    has_whatsapp=record.has_whatsapp,
                    children=[
                        ChildResponse.from_domain(child) for child in children
                    ],
                )
            )
        return recipients

    @v1_router.get(
        "/parents/by-phone/{phone}",
        response_model=ParentResponse,
        tags=["Parents", "WhatsApp / WAHA"],
        summary="Recherche un parent par numéro de téléphone ou identifiant WAHA",
    )
    def find_parent_by_phone(
        phone: str,
        repository: RepositoryDep,
        active_only: Annotated[
            bool,
            Query(
                description="Recherche uniquement parmi les parents actifs si vrai."
            ),
        ] = True,
    ) -> ParentResponse:
        """Recherche un parent à partir d'un numéro `+336...`, `06...`, `336...` ou `336...@c.us`."""
        found = repository.find_record_by_phone(
            phone,
            include_inactive=not active_only,
        )
        if found is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun parent trouvé pour le numéro ou l'identifiant '{phone}'.",
            )
        record, children = found
        return ParentResponse.from_record(record, children)

    @v1_router.patch(
        "/parents/{parent_id}",
        response_model=ParentResponse,
        tags=["Parents"],
        summary="Met à jour partiellement les métadonnées d'intégration d'un parent",
    )
    def patch_parent(
        parent_id: int,
        payload: ParentPatchRequest,
        repository: RepositoryDep,
    ) -> ParentResponse:
        """Met à jour les métadonnées d'intégration (ex. `has_whatsapp`) d'un parent."""
        if "has_whatsapp" in payload.model_fields_set:
            updated = repository.update_parent_metadata(
                parent_id,
                has_whatsapp=payload.has_whatsapp,
            )
        else:
            updated = repository.get_parent_record_by_id(parent_id)

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aucun parent trouvé avec l'identifiant {parent_id}.",
            )
        record, children = updated
        return ParentResponse.from_record(record, children)

    @v1_router.get(
        "/exports/vcf",
        tags=["Exports"],
        summary="Télécharge à la volée le fichier ContactParents.vcf",
    )
    def download_vcf_export(
        repository: RepositoryDep,
        unit: Annotated[str | None, Query()] = None,
        has_mobile: Annotated[bool | None, Query()] = None,
        registration_status: Annotated[str | None, Query()] = None,
        active_only: Annotated[bool, Query()] = True,
    ) -> Response:
        """Génère et retourne le fichier `ContactParents.vcf` depuis la base SQLite."""
        vcf_content = repository.export_vcf(
            short_unit=unit,
            registration_status=registration_status,
            has_valid_mobile=has_mobile,
            include_inactive=not active_only,
        )
        return Response(
            content=vcf_content.encode("utf-8"),
            media_type="text/vcard; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="ContactParents.vcf"'
            },
        )

    @v1_router.get(
        "/exports/xlsx",
        tags=["Exports"],
        summary="Télécharge à la volée le classeur ContactsParents.xlsx",
    )
    def download_xlsx_export(
        repository: RepositoryDep,
        unit: Annotated[str | None, Query()] = None,
        has_mobile: Annotated[bool | None, Query()] = None,
        registration_status: Annotated[str | None, Query()] = None,
        active_only: Annotated[bool, Query()] = True,
    ) -> Response:
        """Génère et retourne le classeur `ContactsParents.xlsx` depuis la base SQLite."""
        xlsx_bytes = repository.export_excel(
            short_unit=unit,
            registration_status=registration_status,
            has_valid_mobile=has_mobile,
            include_inactive=not active_only,
        )
        return Response(
            content=xlsx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="ContactsParents.xlsx"'
            },
        )

    application.include_router(v1_router)
    return application


app = create_app()


def run_server() -> None:
    """Lance le serveur HTTP Uvicorn en utilisant la configuration issue de l'environnement."""
    settings = ApiSettings.from_env()
    uvicorn.run(
        "sgdf_contacts.entrypoints.api:app",
        host=settings.host,
        port=settings.port,
    )


if __name__ == "__main__":
    run_server()
