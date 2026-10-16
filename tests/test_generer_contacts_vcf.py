"""Tests unitaires et d'intégration pour `generer_contacts_vcf.py`.

Vérifie :
1. L'échappement vCard 3.0 (RFC 2426) et la décomposition des adresses postales.
2. L'exportation complète des coordonnées des parents (`N`, `FN` au format `Prénom NOM`,
   téléphones `CELL,VOICE,PREF`, `CELL,VOICE`, `HOME,VOICE`, `EMAIL` et `ADR`).
3. La structuration du champ `NOTE` (`Enfants : Prénom NOM (Unité), ...`,
   `Numéro d'adhérent : ...` s'il existe, `Remarques : ...` si elles existent).
4. La présence systématique des étiquettes `"SGDF"` et `"La Rochelle"`
   (`CATEGORIES:SGDF,La Rochelle`) sur 100 % des fiches.
5. La gestion explicite des erreurs (fichier absent, onglet absent, colonnes invalides)
   et la lecture seule stricte de `ContactsParents.xlsx` (empreinte SHA-256 intacte).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

RACINE_PROJET = Path(__file__).resolve().parent.parent
if str(RACINE_PROJET) not in sys.path:
    sys.path.insert(0, str(RACINE_PROJET))

from generer_contacts_vcf import (
    EN_TETES_CONTACTS_PARENTS,
    NOM_ONGLET_PARENTS,
    ErreurGenerationVcf,
    FicheContactParent,
    construire_note_parent,
    decomposer_adresse_postale,
    echapper_valeur_vcard,
    executer_generation_vcf,
    formater_enfants_et_unites,
    formater_vcard_parent,
    lire_contacts_parents_excel,
    principale,
)


def ecrire_classeur_parents_synthetique(
    chemin: Path,
    lignes_parents: list[list[str]],
    *,
    nom_onglet: str = NOM_ONGLET_PARENTS,
    en_tetes: tuple[str, ...] = EN_TETES_CONTACTS_PARENTS,
) -> None:
    """Crée un classeur Excel `.xlsx` de test contenant l'onglet `ContactsParents`."""
    classeur = Workbook()
    feuille = classeur.active
    feuille.title = nom_onglet
    feuille.append(list(en_tetes))
    for ligne in lignes_parents:
        feuille.append(ligne)
    classeur.save(chemin)


def test_echappement_vcard_et_decomposition_adresse() -> None:
    """Vérifie l'échappement RFC 2426 et la décomposition d'adresses postales."""
    assert (
        echapper_valeur_vcard("Ligne 1, suite ; détail\nLigne 2")
        == r"Ligne 1\, suite \; détail\nLigne 2"
    )
    assert echapper_valeur_vcard(r"Chemin\Test") == r"Chemin\\Test"

    assert decomposer_adresse_postale("12 Rue des Mouettes, 17000 LA ROCHELLE") == (
        "12 Rue des Mouettes",
        "LA ROCHELLE",
        "17000",
        "",
    )
    assert decomposer_adresse_postale(
        "10 Rue du Port, Bâtiment B, 17000 LA ROCHELLE"
    ) == (
        "10 Rue du Port, Bâtiment B",
        "LA ROCHELLE",
        "17000",
        "",
    )
    assert decomposer_adresse_postale(
        "5 Place Royale, 1000 BRUXELLES, BELGIQUE"
    ) == (
        "5 Place Royale",
        "BRUXELLES",
        "1000",
        "BELGIQUE",
    )
    assert decomposer_adresse_postale("Adresse libre sans code postal") == (
        "Adresse libre sans code postal",
        "",
        "",
        "",
    )
    assert decomposer_adresse_postale("") == ("", "", "", "")


def test_formatage_enfants_unites_et_construction_note() -> None:
    """Vérifie l'association enfants/unités et l'omission des rubriques vides dans `NOTE`."""
    assert (
        formater_enfants_et_unites(
            "Lucas BERNARD, Chloé BERNARD",
            "Louveteaux-Jeannettes, Farfadets",
        )
        == "Lucas BERNARD (Louveteaux-Jeannettes), Chloé BERNARD (Farfadets)"
    )
    assert (
        formater_enfants_et_unites("Léo DUPONT, Emma DUPONT", "Scouts-Guides")
        == "Léo DUPONT (Scouts-Guides), Emma DUPONT (Scouts-Guides)"
    )
    assert formater_enfants_et_unites("", "") == ""

    # Cas 1 : Parent avec enfants, numéro d'adhérent et remarques
    fiche_complete = FicheContactParent(
        nom="BERNARD",
        prenom="Élodie",
        noms_enfants="Lucas BERNARD, Chloé BERNARD",
        unites_enfants="Scouts-Guides, Farfadets",
        numero_adherent="987654321",
        remarques="Parent Animateur Farfadet ; Enfant Lucas : Invité(e)",
    )
    note_complete = construire_note_parent(fiche_complete)
    assert note_complete == (
        "Enfants : Lucas BERNARD (Scouts-Guides), Chloé BERNARD (Farfadets)\n"
        "Numéro d'adhérent : 987654321\n"
        "Remarques : Parent Animateur Farfadet ; Enfant Lucas : Invité(e)"
    )

    # Cas 2 : Parent sans numéro d'adhérent ni remarques -> seule la ligne Enfants est présente
    fiche_simple = FicheContactParent(
        nom="MARTIN",
        prenom="Paul",
        noms_enfants="Tom MARTIN",
        unites_enfants="Pionniers-Caravelles",
    )
    note_simple = construire_note_parent(fiche_simple)
    assert note_simple == "Enfants : Tom MARTIN (Pionniers-Caravelles)"
    assert "Numéro d'adhérent" not in note_simple
    assert "Remarques" not in note_simple


def test_serialisation_vcard_parent_complet_et_partiel() -> None:
    """Vérifie la génération d'une entrée `VCARD` 3.0 complète et partielle."""
    fiche_complete = FicheContactParent(
        nom="DUPONT",
        prenom="Jean-Pierre",
        telephone_portable_principal="+33612345678",
        telephone_portable_secondaire="+33698765432",
        telephone_fixe="+33546123456",
        adresse_email="jean-pierre.dupont@example.fr",
        noms_enfants="Lucas DUPONT, Emma DUPONT",
        unites_enfants="Farfadets, Louveteaux-Jeannettes",
        adresse_physique="12 Rue des Mouettes, 17000 LA ROCHELLE",
        numero_adherent="123456789",
        remarques="Parent Animateur Farfadet",
    )
    vcard = formater_vcard_parent(fiche_complete)
    lignes = vcard.split("\r\n")

    assert lignes[0] == "BEGIN:VCARD"
    assert lignes[1] == "VERSION:3.0"
    assert "N:DUPONT;Jean-Pierre;;;" in lignes
    assert "FN:Jean-Pierre DUPONT" in lignes
    assert "TEL;TYPE=CELL,VOICE,PREF:+33612345678" in lignes
    assert "TEL;TYPE=CELL,VOICE:+33698765432" in lignes
    assert "TEL;TYPE=HOME,VOICE:+33546123456" in lignes
    assert "EMAIL;TYPE=INTERNET,HOME:jean-pierre.dupont@example.fr" in lignes
    assert "ADR;TYPE=HOME:;;12 Rue des Mouettes;LA ROCHELLE;;17000;" in lignes
    assert (
        r"NOTE:Enfants : Lucas DUPONT (Farfadets)\, Emma DUPONT (Louveteaux-Jeannettes)"
        r"\nNuméro d'adhérent : 123456789\nRemarques : Parent Animateur Farfadet"
        in lignes
    )
    assert "CATEGORIES:SGDF,La Rochelle" in lignes
    assert lignes[-1] == "END:VCARD"

    # Fiche avec coordonnées partielles : pas de portable secondaire, fixe, email ni adresse
    fiche_partielle = FicheContactParent(
        nom="DURAND",
        prenom="Marie",
        telephone_portable_principal="+33600112233",
        noms_enfants="Léo DURAND",
        unites_enfants="Compagnons",
    )
    vcard_partielle = formater_vcard_parent(fiche_partielle)
    assert "FN:Marie DURAND" in vcard_partielle
    assert "TEL;TYPE=CELL,VOICE,PREF:+33600112233" in vcard_partielle
    assert "TEL;TYPE=CELL,VOICE:" not in vcard_partielle
    assert "TEL;TYPE=HOME,VOICE:" not in vcard_partielle
    assert "EMAIL" not in vcard_partielle
    assert "ADR" not in vcard_partielle
    assert "NOTE:Enfants : Léo DURAND (Compagnons)" in vcard_partielle
    assert "CATEGORIES:SGDF,La Rochelle" in vcard_partielle


def test_erreurs_lecture_fichier_et_onglet(tmp_path: Path) -> None:
    """Vérifie la levée d'erreurs explicites en français lorsque l'entrée est invalide."""
    chemin_inexistant = tmp_path / "Absent.xlsx"
    with pytest.raises(ErreurGenerationVcf, match="introuvable"):
        lire_contacts_parents_excel(chemin_inexistant)

    code_retour = principale(
        ["--entree", str(chemin_inexistant), "--sortie", str(tmp_path / "out.vcf")]
    )
    assert code_retour == 1

    # Classeur sans l'onglet ContactsParents
    chemin_sans_onglet = tmp_path / "SansOnglet.xlsx"
    ecrire_classeur_parents_synthetique(
        chemin_sans_onglet,
        [],
        nom_onglet="AutreOnglet",
    )
    with pytest.raises(ErreurGenerationVcf, match="absent"):
        lire_contacts_parents_excel(chemin_sans_onglet)

    # Classeur avec en-têtes invalides
    chemin_mauvais_entetes = tmp_path / "MauvaisEntetes.xlsx"
    ecrire_classeur_parents_synthetique(
        chemin_mauvais_entetes,
        [],
        en_tetes=("Colonne1", "Colonne2"),
    )
    with pytest.raises(ErreurGenerationVcf, match="En-têtes invalides"):
        lire_contacts_parents_excel(chemin_mauvais_entetes)


def test_generation_fichier_vcf_via_cli(tmp_path: Path) -> None:
    """Vérifie la génération de `ContactParents.vcf` de bout en bout via la CLI."""
    chemin_entree = tmp_path / "ContactsParents.xlsx"
    chemin_sortie = tmp_path / "ContactParents.vcf"

    ecrire_classeur_parents_synthetique(
        chemin_entree,
        [
            [
                "BERNARD",
                "Élodie",
                "+33601020304",
                "",
                "+33546001122",
                "elodie.bernard@example.fr",
                "Lucas BERNARD, Chloé BERNARD",
                "Scouts-Guides, Farfadets",
                "5 Avenue Coligny, 17000 LA ROCHELLE",
                "987654321",
                "Parent Animateur Farfadet ; Enfant Lucas : Invité(e)",
            ],
            [
                "MARTIN",
                "Paul",
                "+33699887766",
                "",
                "",
                "",
                "Tom MARTIN",
                "Pionniers-Caravelles",
                "",
                "",
                "",
            ],
        ],
    )

    code_retour = principale(
        ["--entree", str(chemin_entree), "--sortie", str(chemin_sortie)]
    )
    assert code_retour == 0
    assert chemin_sortie.is_file()

    contenu = chemin_sortie.read_text(encoding="utf-8")
    assert contenu.count("BEGIN:VCARD") == 2
    assert contenu.count("END:VCARD") == 2
    assert contenu.count("CATEGORIES:SGDF,La Rochelle") == 2
    assert "FN:Élodie BERNARD" in contenu
    assert "FN:Paul MARTIN" in contenu


def test_integration_contacts_parents_xlsx_reel(tmp_path: Path) -> None:
    """Vérifie la génération de `ContactParents.vcf` depuis `ContactsParents.xlsx` réel."""
    chemin_entree = RACINE_PROJET / "ContactsParents.xlsx"
    if not chemin_entree.is_file():
        return

    empreinte_avant = hashlib.sha256(chemin_entree.read_bytes()).hexdigest()
    chemin_sortie = tmp_path / "ContactParents.vcf"

    fiches = executer_generation_vcf(
        chemin_entree=chemin_entree,
        chemin_sortie=chemin_sortie,
    )

    empreinte_apres = hashlib.sha256(chemin_entree.read_bytes()).hexdigest()
    assert (
        empreinte_avant == empreinte_apres
    ), "`ContactsParents.xlsx` ne doit subir aucune modification."

    # 1. 134 parents uniques exportés
    assert len(fiches) == 134

    contenu = chemin_sortie.read_text(encoding="utf-8")
    assert contenu.count("BEGIN:VCARD") == 134
    assert contenu.count("END:VCARD") == 134
    assert contenu.count("VERSION:3.0") == 134
    assert contenu.count("CATEGORIES:SGDF,La Rochelle") == 134
    assert contenu.count("NOTE:Enfants : ") == 134

    # 2. Vérifier la cohérence des champs sur chaque fiche
    for fiche in fiches:
        assert fiche.nom == fiche.nom.upper()
        assert fiche.nom_complet_affiche == f"{fiche.prenom} {fiche.nom}"
        assert fiche.etiquettes == ("SGDF", "La Rochelle")
        assert fiche.noms_enfants != ""
        assert fiche.unites_enfants != ""
