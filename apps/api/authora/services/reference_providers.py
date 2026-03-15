"""Reference toolkit providers - dictionary, thesaurus, local data."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

FREE_DICT_URL = "https://api.dictionaryapi.dev/api/v2/entries"
DATAMUSE_URL = "https://api.datamuse.com"


@dataclass
class WordDefinition:
    word: str
    phonetic: str | None
    meanings: list[dict[str, Any]]


@dataclass
class ThesaurusResult:
    word: str
    synonyms: list[str]
    antonyms: list[str]
    related: list[str]


class DictionaryProvider(ABC):
    """Abstract dictionary provider."""

    @abstractmethod
    async def lookup(self, word: str) -> WordDefinition | None:
        """Look up word definition."""
        ...


class ThesaurusProvider(ABC):
    """Abstract thesaurus provider."""

    @abstractmethod
    async def synonyms(self, word: str, limit: int = 20) -> list[str]:
        """Get synonyms."""
        ...

    @abstractmethod
    async def antonyms(self, word: str, limit: int = 20) -> list[str]:
        """Get antonyms."""
        ...


class FreeDictProvider(DictionaryProvider):
    """Free Dictionary API - no key required."""

    async def lookup(self, word: str) -> WordDefinition | None:
        word = word.strip().lower()
        if not word:
            return None
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{FREE_DICT_URL}/en/{word}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        entry = data[0]
        phonetic = entry.get("phonetic") or (entry.get("phonetics") or [{}])[0].get("text")
        meanings = []
        for m in entry.get("meanings", []):
            meanings.append({
                "partOfSpeech": m.get("partOfSpeech"),
                "definitions": [
                    {"definition": d.get("definition"), "example": d.get("example")}
                    for d in m.get("definitions", [])[:5]
                ],
            })
        return WordDefinition(word=entry.get("word", word), phonetic=phonetic, meanings=meanings)


class DatamuseThesaurusProvider(ThesaurusProvider):
    """Datamuse API - synonyms (ml), antonyms (rel_ant)."""

    async def synonyms(self, word: str, limit: int = 20) -> list[str]:
        word = word.strip().lower()
        if not word:
            return []
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DATAMUSE_URL}/words", params={"ml": word, "max": limit})
        resp.raise_for_status()
        data = resp.json()
        return [w["word"] for w in data if "word" in w][:limit]

    async def antonyms(self, word: str, limit: int = 20) -> list[str]:
        word = word.strip().lower()
        if not word:
            return []
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DATAMUSE_URL}/words", params={"rel_ant": word, "max": limit})
        resp.raise_for_status()
        data = resp.json()
        return [w["word"] for w in data if "word" in w][:limit]

    async def related(self, word: str, limit: int = 20) -> list[str]:
        """Related words (triggers)."""
        word = word.strip().lower()
        if not word:
            return []
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DATAMUSE_URL}/words", params={"rel_trg": word, "max": limit})
        resp.raise_for_status()
        data = resp.json()
        return [w["word"] for w in data if "word" in w][:limit]


class DatamusePhraseProvider:
    """Datamuse for phrase alternatives (means like)."""

    async def phrase_alternatives(self, phrase: str, limit: int = 10) -> list[str]:
        """Get alternative phrases with similar meaning."""
        phrase = phrase.strip()
        if not phrase or len(phrase) < 3:
            return []
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{DATAMUSE_URL}/words", params={"ml": phrase, "max": limit})
        resp.raise_for_status()
        data = resp.json()
        return [w["word"] for w in data if "word" in w and w["word"] != phrase][:limit]
