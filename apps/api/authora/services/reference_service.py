"""Unified reference service - providers, cache, fallbacks."""

from dataclasses import dataclass

from authora.services.reference_analyzer import analyze_text
from authora.services.reference_cache import cached_lookup, get_dict_cache, get_thesaurus_cache
from authora.services.reference_data import get_simplification_hint, get_vocab_enhancements
from authora.services.reference_providers import (
    DatamusePhraseProvider,
    DatamuseThesaurusProvider,
    FreeDictProvider,
)


@dataclass
class LookupResult:
    word: str
    definition: dict | None
    synonyms: list[str]
    antonyms: list[str]
    phrase_alternatives: list[str]
    simplification_hint: str | None
    vocab_alternatives: list[str]
    source: str  # "cache" | "api" | "local"


_dict_provider = FreeDictProvider()
_thesaurus_provider = DatamuseThesaurusProvider()
_phrase_provider = DatamusePhraseProvider()


async def lookup_word(word: str) -> LookupResult:
    """Unified word lookup with cache and fallbacks."""
    word_clean = word.strip().lower()
    if not word_clean:
        return LookupResult(
            word=word,
            definition=None,
            synonyms=[],
            antonyms=[],
            phrase_alternatives=[],
            simplification_hint=None,
            vocab_alternatives=[],
            source="local",
        )

    # Try cache first
    dict_cache = get_dict_cache()
    thesaurus_cache = get_thesaurus_cache()

    async def fetch_def():
        d = await _dict_provider.lookup(word_clean)
        if d:
            return {"phonetic": d.phonetic, "meanings": d.meanings}
        return None

    async def fetch_synonyms():
        return await _thesaurus_provider.synonyms(word_clean, 15)

    async def fetch_antonyms():
        return await _thesaurus_provider.antonyms(word_clean, 10)

    definition = await cached_lookup(dict_cache, f"def:{word_clean}", fetch_def)
    synonyms = await cached_lookup(thesaurus_cache, f"syn:{word_clean}", fetch_synonyms, [])
    antonyms = await cached_lookup(thesaurus_cache, f"ant:{word_clean}", fetch_antonyms, [])

    # Local data (always available, no fetch)
    simplification_hint = get_simplification_hint(word_clean)
    vocab_alternatives = get_vocab_enhancements(word_clean)

    # Phrase alternatives only if multi-word
    phrase_alternatives = []
    if " " in word_clean:
        try:
            phrase_alternatives = await _phrase_provider.phrase_alternatives(word_clean, 5)
        except Exception:
            pass

    return LookupResult(
        word=word_clean,
        definition=definition,
        synonyms=synonyms or [],
        antonyms=antonyms or [],
        phrase_alternatives=phrase_alternatives,
        simplification_hint=simplification_hint,
        vocab_alternatives=vocab_alternatives or [],
        source="cache" if definition or synonyms else "api",
    )


async def analyze_document(text: str) -> dict:
    """Analyze document for writing hints."""
    return analyze_text(text or "")
