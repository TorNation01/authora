"""Dictionary and thesaurus API - Free Dictionary API."""

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/dictionary", tags=["dictionary"])

FREE_DICT_URL = "https://api.dictionaryapi.dev/api/v2/entries"


async def _fetch_word(word: str):
    """Fetch word data from Free Dictionary API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{FREE_DICT_URL}/en/{word}")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Word not found")
    resp.raise_for_status()
    return resp.json()


@router.get("/lookup")
async def lookup(word: str = Query(..., min_length=1)):
    """Look up word definition (Free Dictionary API - no key required)."""
    return await _fetch_word(word)


@router.get("/thesaurus")
async def thesaurus(word: str = Query(..., min_length=1)):
    """Get synonyms - uses same API (meanings include synonyms in some entries)."""
    data = await _fetch_word(word)
    synonyms = []
    for entry in data:
        for meaning in entry.get("meanings", []):
            for defn in meaning.get("definitions", []):
                synonyms.extend(defn.get("synonyms", []))
    return {"word": word, "synonyms": list(dict.fromkeys(synonyms))[:50]}
