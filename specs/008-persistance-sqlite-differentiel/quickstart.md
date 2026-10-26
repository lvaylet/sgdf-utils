# Quickstart Validation Guide: Persistance SQLite (`SQLModel`) et Calcul de Différentiel

**Feature**: `008-persistance-sqlite-differentiel` | **Date**: 2026-10-26

## Prérequis

1. Disposer de l'environnement éphémère Nix (`flake.nix`) ou Devbox (`devbox.json`) activé via `direnv`.
2. Vérifier que `sqlmodel` et `sqlalchemy` sont disponibles dans l'environnement :

```bash
nix develop --command python3 -c "import sqlmodel, sqlalchemy; print(sqlmodel.__version__, sqlalchemy.__version__)"
```

## Scénario 1 : Initialisation d'une base SQLite, import idempotent et calcul de différentiel

Exécuter un import sur une base SQLite temporaire à partir de `ExportIndividus.xls` (ou de données de test) et vérifier l'idempotence lors d'un second import :

```bash
nix develop --command python3 -c "
import tempfile
from pathlib import Path
from sgdf_contacts.persistence import create_db_engine, init_db, ParentContactRepository

with tempfile.TemporaryDirectory() as tmp:
    engine = create_db_engine(Path(tmp) / 'contacts.db')
    init_db(engine)
    repo = ParentContactRepository(engine)

    export_file = Path('ExportIndividus.xls')
    if export_file.is_file():
        report1 = repo.import_individuals_xls(export_file)
        print('Import 1 :', len(report1.created), len(report1.updated), len(report1.unchanged), len(report1.deactivated))
        report2 = repo.import_individuals_xls(export_file)
        print('Import 2 :', len(report2.created), len(report2.updated), len(report2.unchanged), len(report2.deactivated))
        assert len(report2.created) == 0 and len(report2.updated) == 0
"
```

**Résultat attendu** :
- Premier import sur `ExportIndividus.xls` : `134 created`, `0 updated`, `0 unchanged`, `0 deactivated`.
- Second import immédiat du même fichier : `0 created`, `0 updated`, `134 unchanged`, `0 deactivated`.

## Scénario 2 : Régénération directe de `ContactParents.vcf` et `ContactsParents.xlsx` depuis SQLite

Sans relire `ExportIndividus.xls`, régénérer les deux fichiers d'export directement depuis la base SQLite :

```bash
nix develop --command pytest tests/test_persistence.py
```

## Scénario 3 : Suite complète de tests et contrôle de qualité du code

Lancer l'ensemble des tests automatisés et le vérificateur `ruff` dans l'environnement éphémère :

```bash
nix develop --command pytest
nix develop --command ruff check .
```

**Résultat attendu** :
- `100%` des tests (`test_environment.py`, `test_extract_parent_contacts.py`, `test_generate_contacts_vcf.py`, `test_sgdf_contacts_package.py`, `test_persistence.py`) réussissent.
- `ruff check .` retourne `All checks passed!`.
