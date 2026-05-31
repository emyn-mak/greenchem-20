# GreenChem Navigator Backend

FastAPI backend for rule-based green chemistry recommendations. This version does not use invented percentage scores or fabricated confidence values. It uses a local JSON knowledge base with GHS hazard codes, solvent guide colors, boiling points, and compatibility rules.

It also includes a small prototype ML compatibility classifier. The model is trained from curated rule-bootstrap data generated from the local knowledge base. This is useful for a hackathon demo, but it is not experimental proof.

The solvent knowledge base can be expanded with public PubChem metadata using `app/tools/import_pubchem_solvents.py`. PubChem data is used for fields such as CID, molecular formula, molecular weight, and canonical SMILES when available.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Train The Prototype Model

Command line:

```bash
python -m app.tools.import_pubchem_solvents
python -m app.ml.train_model
```

Or use the API after starting the server:

```text
POST http://127.0.0.1:8000/model/train
GET  http://127.0.0.1:8000/model/status
```

## Running Backend

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Frontend

A professional Python-served frontend is included under `app/static/`. It is mounted directly by FastAPI, so no Node, npm, or separate frontend server is required.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Open the application:

```text
http://127.0.0.1:8000/
```

## Example Request

This request includes a known catalyst formula and role, so the backend can screen alternatives.

```json
{
  "formula_text": "20 mL H2O\n10 mL Acetone\n1 mL H2SO4\nTemperature: 90C\nTime: 4h\nPressure: 1 atm\nStirring: 300 rpm\npH: 2\nSolvent: Acetone\nCatalyst: H2SO4\nCatalyst role: acid_catalyst"
}
```

If the catalyst is missing or unknown, the backend returns `status: "Insufficient data"` and proposes no alternatives.

## Example Reality Check

```json
{
  "formula_text": "is this real?"
}
```

Response message:

```text
These are predictions based on literature and chemical rules. Wet lab validation required.
```

## Architecture

- `app/main.py`: FastAPI app, CORS, health check, `/analyze`
- `app/schemas.py`: request and response models
- `app/parser.py`: simple formula/process parser
- `app/knowledge_base.json`: local solvent and catalyst knowledge base
- `app/knowledge.py`: lookup helpers
- `app/compatibility.py`: acid/base and incompatibility checks
- `app/ml/dataset.py`: generates training rows from the local knowledge base
- `app/ml/train_model.py`: trains and saves the RandomForest compatibility model
- `app/ml/model.py`: loads the saved model and predicts compatibility
- `app/recommender.py`: recommendation orchestration
- `app/model_placeholder.py`: compatibility model wrapper that uses the trained model and an optional LLM fallback
- `app/llm.py`: optional OpenAI-compatible LLM compatibility fallback for solvent recommendations

If `OPENAI_API_KEY` is set, the backend can fall back to an LLM when no trained compatibility model artifact is available.

No alternative is laboratory advice. Every response requires human review and wet lab validation.
