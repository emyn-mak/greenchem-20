from pathlib import Path
import re
from html import unescape
from urllib.request import Request, urlopen

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.model_placeholder import GreenChemModel
from app.ml.train_model import train_model
from app.pdf_report import build_analysis_pdf
from app.recommender import GreenChemRecommender
from app.schemas import AnalyzeRequest, AnalyzeResponse


app = FastAPI(
    title="GreenChem Navigator Backend",
    version="0.2.0",
    description="Rule-based backend for green chemistry solvent recommendations.",
)

STATIC_DIR = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_recommender(settings: Settings = Depends(get_settings)) -> GreenChemRecommender:
    return GreenChemRecommender()


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/news")
def chemistry_news() -> dict[str, object]:
    return {
        "source": "Chemical & Engineering News / ACS, with curated fallbacks",
        "items": fetch_chemistry_news(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/model/status")
def model_status() -> dict[str, object]:
    model = GreenChemModel()
    model_type = None
    accuracy = None
    training_rows = None
    feature_count = None
    label_source = None
    if model.compatibility_model.is_available:
        model_type = "RandomForestClassifier"
        artifact = model.compatibility_model.artifact or {}
        accuracy = artifact.get("accuracy")
        training_rows = artifact.get("training_rows")
        feature_count = len(artifact.get("feature_columns", []))
        label_source = artifact.get("label_source")
    elif model.llm_model.is_available:
        model_type = "OpenAI-compatible LLM"

    return {
        "available": model.is_available,
        "type": model_type,
        "accuracy": accuracy,
        "accuracy_percent": round(float(accuracy) * 100, 1) if accuracy is not None else None,
        "training_rows": training_rows,
        "feature_count": feature_count,
        "label_source": label_source,
        "message": (
            "Trained compatibility model is available."
            if model.compatibility_model.is_available
            else "LLM fallback is available. Set OPENAI_API_KEY and use a compatible OpenAI endpoint."
            if model.llm_model.is_available
            else "No trained model or LLM fallback found. Run POST /model/train or configure OPENAI_API_KEY."
        ),
    }


@app.post("/model/train")
def train_compatibility_model() -> dict[str, object]:
    return train_model()


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    request: AnalyzeRequest,
    recommender: GreenChemRecommender = Depends(get_recommender),
) -> AnalyzeResponse:
    return recommender.analyze(request.formula_text)


@app.post("/analyze/pdf")
def analyze_pdf(
    request: AnalyzeRequest,
    recommender: GreenChemRecommender = Depends(get_recommender),
) -> StreamingResponse:
    response = recommender.analyze(request.formula_text)
    pdf_bytes = build_analysis_pdf(response, request.formula_text)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="greenchem-analysis-report.pdf"'},
    )


def fetch_chemistry_news() -> list[dict[str, str]]:
    try:
        request = Request(
            "https://cen.acs.org/",
            headers={"User-Agent": "GreenChemNavigator/0.1"},
        )
        with urlopen(request, timeout=8) as response:
            html = response.read().decode("utf-8", errors="ignore")
        return parse_cen_homepage(html)[:6] or fallback_news()
    except Exception:
        return fallback_news()


def parse_cen_homepage(html: str) -> list[dict[str, str]]:
    items = []
    seen = set()
    navigation_labels = {
        "features",
        "perspectives",
        "interviews",
        "acs news",
        "graphics",
        "chempics",
        "magazine",
        "latest news",
        "research",
        "business",
        "careers",
        "policy",
    }
    pattern = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]{24,160})\s*</a>', re.IGNORECASE)
    for href, title in pattern.findall(html):
        title = clean_html_text(title)
        if not title or title in seen:
            continue
        lowered = title.lower()
        if lowered in navigation_labels:
            continue
        if any(skip in lowered for skip in ["subscribe", "log in", "advertise", "privacy", "terms"]):
            continue
        if len(title.split()) < 4:
            continue
        if href.startswith("/"):
            href = f"https://cen.acs.org{href}"
        if not href.startswith("https://cen.acs.org"):
            continue
        seen.add(title)
        items.append(
            {
                "title": title,
                "source": "C&EN",
                "url": href,
                "summary": "Recent chemistry news item. Open the source for full details before using it in a decision.",
            }
        )
    return items if len(items) >= 3 else []


def fallback_news() -> list[dict[str, str]]:
    return [
        {
            "title": "Green chemistry news and sustainability updates",
            "source": "American Chemical Society",
            "url": "https://www.acs.org/green-chemistry-sustainability/what-is-green-chemistry/green-chemistry-news.html",
            "summary": "ACS green chemistry resources, updates, and sustainability-oriented chemistry information.",
        },
        {
            "title": "Chemistry news from Chemical & Engineering News",
            "source": "C&EN",
            "url": "https://cen.acs.org/",
            "summary": "Current chemistry, chemical engineering, safety, policy, materials, and sustainability news.",
        },
        {
            "title": "Royal Society of Chemistry feeds and journal updates",
            "source": "RSC",
            "url": "https://pubs.rsc.org/en/ealerts/rssfeed",
            "summary": "RSC feed directory for chemistry journals and Chemistry World news updates.",
        },
    ]


def clean_html_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()
