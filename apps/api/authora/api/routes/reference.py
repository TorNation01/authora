"""Reference toolkit API - dictionary, thesaurus, analysis."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from authora.api.dependencies import CurrentUser
from authora.services.reference_service import analyze_document, lookup_word

router = APIRouter(prefix="/reference", tags=["reference"])


class AnalyzeRequest(BaseModel):
    text: str = ""


@router.get("/lookup")
async def reference_lookup(
    current_user: CurrentUser,
    word: str = Query(..., min_length=1, max_length=100),
):
    """Look up word: definition, synonyms, antonyms, hints."""
    result = await lookup_word(word)
    return {
        "word": result.word,
        "definition": result.definition,
        "synonyms": result.synonyms,
        "antonyms": result.antonyms,
        "phrase_alternatives": result.phrase_alternatives,
        "simplification_hint": result.simplification_hint,
        "vocab_alternatives": result.vocab_alternatives,
        "source": result.source,
    }


@router.get("/synonyms")
async def get_synonyms(
    current_user: CurrentUser,
    word: str = Query(..., min_length=1, max_length=100),
):
    """Quick synonym lookup for inline menu."""
    result = await lookup_word(word)
    return {"word": result.word, "synonyms": result.synonyms}


@router.get("/antonyms")
async def get_antonyms(
    current_user: CurrentUser,
    word: str = Query(..., min_length=1, max_length=100),
):
    """Quick antonym lookup."""
    result = await lookup_word(word)
    return {"word": result.word, "antonyms": result.antonyms}


@router.post("/analyze")
async def analyze_text_endpoint(
    current_user: CurrentUser,
    data: AnalyzeRequest,
):
    """Analyze text: overused words, repeated phrases, cliches, readability, vocab hints."""
    return await analyze_document(data.text[:100_000])
