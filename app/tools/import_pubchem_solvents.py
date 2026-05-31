import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


KB_PATH = Path(__file__).resolve().parents[1] / "knowledge_base.json"
PUBCHEM_PROPERTY_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
PUBCHEM_CID_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
PUBCHEM_VIEW_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"


EXTRA_SOLVENTS = [
    {"name": "1,4-Dioxane", "aliases": ["dioxane"], "boiling_point_c": 101.1, "chem21_color": "red", "known_incompatibilities": ["peroxide_former", "strong_oxidizer"]},
    {"name": "Diethyl ether", "aliases": ["ether", "et2o"], "boiling_point_c": 34.6, "chem21_color": "red", "known_incompatibilities": ["peroxide_former", "strong_oxidizer"]},
    {"name": "Diisopropyl ether", "aliases": ["diisopropyl ether", "dipe"], "boiling_point_c": 68.5, "chem21_color": "red", "known_incompatibilities": ["peroxide_former", "strong_oxidizer"]},
    {"name": "Methyl acetate", "aliases": ["meoac"], "boiling_point_c": 56.9, "chem21_color": "green", "known_incompatibilities": ["strong_acid_hydrolysis", "strong_base_hydrolysis"]},
    {"name": "Isopropyl acetate", "aliases": ["iproac"], "boiling_point_c": 88.6, "chem21_color": "green", "known_incompatibilities": ["strong_acid_hydrolysis", "strong_base_hydrolysis"]},
    {"name": "Butyl acetate", "aliases": ["n-butyl acetate"], "boiling_point_c": 126.1, "chem21_color": "green", "known_incompatibilities": ["strong_acid_hydrolysis", "strong_base_hydrolysis"]},
    {"name": "Acetic acid", "aliases": ["glacial acetic acid"], "boiling_point_c": 118.1, "chem21_color": "yellow", "known_incompatibilities": ["strong_base"]},
    {"name": "Formic acid", "aliases": [], "boiling_point_c": 100.8, "chem21_color": "yellow", "known_incompatibilities": ["strong_base", "strong_oxidizer"]},
    {"name": "Methyl ethyl ketone", "aliases": ["mek", "2-butanone"], "boiling_point_c": 79.6, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Methyl isobutyl ketone", "aliases": ["mibk"], "boiling_point_c": 116.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Cyclohexanone", "aliases": [], "boiling_point_c": 155.6, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Cyclohexane", "aliases": [], "boiling_point_c": 80.7, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Methylcyclohexane", "aliases": [], "boiling_point_c": 100.9, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Isooctane", "aliases": ["2,2,4-trimethylpentane"], "boiling_point_c": 99.2, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Pentane", "aliases": ["n-pentane"], "boiling_point_c": 36.1, "chem21_color": "red", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Dimethyl sulfone", "aliases": ["msm"], "boiling_point_c": 238.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Sulfolane", "aliases": [], "boiling_point_c": 285.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Dimethylacetamide", "aliases": ["dmac", "n,n-dimethylacetamide"], "boiling_point_c": 165.0, "chem21_color": "red", "known_incompatibilities": ["strong_acid", "strong_base"]},
    {"name": "1,3-Dimethyl-2-imidazolidinone", "aliases": ["dmi"], "boiling_point_c": 225.0, "chem21_color": "red", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "1,3-Dimethyl-3,4,5,6-tetrahydro-2-pyrimidinone", "aliases": ["dmpu"], "boiling_point_c": 246.0, "chem21_color": "red", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Pyridine", "aliases": [], "boiling_point_c": 115.2, "chem21_color": "red", "known_incompatibilities": ["strong_acid", "strong_oxidizer"]},
    {"name": "Morpholine", "aliases": [], "boiling_point_c": 128.0, "chem21_color": "red", "known_incompatibilities": ["strong_acid", "strong_oxidizer"]},
    {"name": "Anisole", "aliases": ["methoxybenzene"], "boiling_point_c": 154.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Benzyl alcohol", "aliases": [], "boiling_point_c": 205.3, "chem21_color": "yellow", "known_incompatibilities": ["strong_acid_heat_dehydration", "strong_oxidizer"]},
    {"name": "Ethyl lactate", "aliases": [], "boiling_point_c": 154.0, "chem21_color": "green", "known_incompatibilities": ["strong_acid_hydrolysis", "strong_base_hydrolysis"]},
    {"name": "Limonene", "aliases": ["d-limonene"], "boiling_point_c": 176.0, "chem21_color": "green", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Glycerol", "aliases": ["glycerine"], "boiling_point_c": 290.0, "chem21_color": "green", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Polyethylene glycol 400", "aliases": ["peg 400"], "boiling_point_c": 250.0, "chem21_color": "green", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Tert-butanol", "aliases": ["tert-butyl alcohol", "t-butanol"], "boiling_point_c": 82.2, "chem21_color": "yellow", "known_incompatibilities": ["strong_acid_heat_dehydration", "strong_oxidizer"]},
    {"name": "Acetophenone", "aliases": [], "boiling_point_c": 202.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Benzotrifluoride", "aliases": ["btf"], "boiling_point_c": 102.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Trifluorotoluene", "aliases": ["benzotrifluoride"], "boiling_point_c": 102.0, "chem21_color": "yellow", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Carbon tetrachloride", "aliases": ["tetrachloromethane"], "boiling_point_c": 76.7, "chem21_color": "red", "known_incompatibilities": ["strong_base", "alkali_metals"]},
    {"name": "Tetrachloroethylene", "aliases": ["perchloroethylene"], "boiling_point_c": 121.1, "chem21_color": "red", "known_incompatibilities": ["strong_base", "strong_oxidizer"]},
    {"name": "1,2-Dichloroethane", "aliases": ["ethylene dichloride"], "boiling_point_c": 83.5, "chem21_color": "red", "known_incompatibilities": ["strong_base", "strong_oxidizer"]},
    {"name": "Nitromethane", "aliases": [], "boiling_point_c": 101.2, "chem21_color": "red", "known_incompatibilities": ["strong_base", "strong_oxidizer"]},
    {"name": "Nitrobenzene", "aliases": [], "boiling_point_c": 210.9, "chem21_color": "red", "known_incompatibilities": ["strong_base", "strong_oxidizer"]},
    {"name": "Carbon disulfide", "aliases": [], "boiling_point_c": 46.3, "chem21_color": "red", "known_incompatibilities": ["strong_oxidizer"]},
    {"name": "Diethyl carbonate", "aliases": ["dec"], "boiling_point_c": 126.0, "chem21_color": "green", "known_incompatibilities": ["strong_base_transesterification", "strong_acid_hydrolysis"]},
    {"name": "Dipropyl carbonate", "aliases": [], "boiling_point_c": 167.0, "chem21_color": "green", "known_incompatibilities": ["strong_base_transesterification", "strong_acid_hydrolysis"]}
]


def fetch_json(url: str, timeout: int = 8) -> dict[str, Any] | None:
    request = urllib.request.Request(url, headers={"User-Agent": "GreenChemNavigatorHackathon/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def pubchem_name_path(name: str) -> str:
    return urllib.parse.quote(name, safe="")


def fetch_pubchem_metadata(name: str) -> dict[str, Any]:
    encoded = pubchem_name_path(name)
    properties = fetch_json(PUBCHEM_PROPERTY_URL.format(name=encoded)) or {}

    property_row = (
        properties.get("PropertyTable", {})
        .get("Properties", [{}])[0]
    )
    cid = property_row.get("CID")

    return {
        "cid": cid,
        "formula": property_row.get("MolecularFormula"),
        "canonical_smiles": property_row.get("CanonicalSMILES"),
        "molecular_weight": property_row.get("MolecularWeight"),
        "ghs_codes": [],
    }


def fetch_pubchem_ghs_codes(cid: int) -> list[str]:
    view = fetch_json(PUBCHEM_VIEW_URL.format(cid=cid)) or {}
    text = json.dumps(view)
    return sorted(set(re.findall(r"\bH\d{3}[A-Za-z]?\b", text)))


def merge_solvents() -> dict[str, int]:
    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    existing = {item["name"].lower(): item for item in kb["solvents"]}
    added = 0
    updated = 0
    fetched = 0

    for solvent in EXTRA_SOLVENTS:
        metadata = fetch_pubchem_metadata(solvent["name"])
        if metadata.get("cid"):
            fetched += 1

        record = {
            "name": solvent["name"],
            "formula": metadata.get("formula"),
            "aliases": solvent.get("aliases", []),
            "ghs_codes": metadata.get("ghs_codes", []),
            "boiling_point_c": solvent["boiling_point_c"],
            "chem21_color": solvent["chem21_color"],
            "known_incompatibilities": solvent.get("known_incompatibilities", []),
            "pubchem_cid": metadata.get("cid"),
            "canonical_smiles": metadata.get("canonical_smiles"),
            "molecular_weight": metadata.get("molecular_weight"),
            "data_sources": [
                "PubChem PUG REST/PUG View for formula, CID, SMILES, molecular weight, and hazard-code text when available",
                "Curated solvent guide category and boiling point seed list for hackathon prototype",
            ],
            "guide_notes": [
                "Imported as public-data-backed prototype solvent entry; verify before production use."
            ],
        }

        key = solvent["name"].lower()
        if key in existing:
            existing[key].update({k: v for k, v in record.items() if v not in (None, [], "")})
            updated += 1
        else:
            kb["solvents"].append(record)
            added += 1

    KB_PATH.write_text(json.dumps(kb, indent=2) + "\n", encoding="utf-8")
    return {
        "added": added,
        "updated": updated,
        "pubchem_records_fetched": fetched,
        "total_solvents": len(kb["solvents"]),
    }


if __name__ == "__main__":
    print(json.dumps(merge_solvents(), indent=2))
