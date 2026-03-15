"""Local reference data - overused words, cliches, simplification hints."""

# Common overused words in writing (curated)
OVERUSED_WORDS = frozenset({
    "very", "really", "just", "actually", "literally", "basically", "actually",
    "quite", "rather", "somewhat", "extremely", "incredibly", "absolutely",
    "definitely", "probably", "maybe", "perhaps", "suddenly", "immediately",
    "quickly", "slowly", "simply", "clearly", "obviously", "honestly",
    "thing", "things", "stuff", "something", "anything", "everything",
    "nice", "good", "bad", "great", "awesome", "amazing", "beautiful",
    "look", "looked", "looking", "see", "saw", "seeing", "think", "thought",
    "feel", "felt", "feeling", "know", "knew", "knowing", "get", "got",
    "went", "go", "going", "come", "came", "coming", "say", "said", "saying",
    "walk", "walked", "walking", "run", "ran", "running", "start", "started",
    "begin", "began", "begun", "end", "ended", "finish", "finished",
    "little", "big", "small", "large", "huge", "tiny", "many", "much",
    "a lot", "lots", "some", "several", "few", "enough",
})

# Common cliches and tired phrases
CLICHES = frozenset({
    "at the end of the day", "at this point in time", "ballpark figure",
    "beat around the bush", "best of both worlds", "bite the bullet",
    "break the ice", "burning the midnight oil", "by the same token",
    "call it a day", "cut to the chase", "easier said than done",
    "fit as a fiddle", "get the ball rolling", "give it 110 percent",
    "go the extra mile", "in the nick of time", "it goes without saying",
    "it's not rocket science", "last but not least", "leave no stone unturned",
    "low-hanging fruit", "move the goalposts", "needless to say",
    "on the same page", "par for the course", "piece of cake",
    "push the envelope", "reinvent the wheel", "think outside the box",
    "tip of the iceberg", "when all is said and done", "win-win situation",
    "at the drop of a hat", "back to the drawing board", "back to square one",
    "blessing in disguise", "cold shoulder", "cry over spilled milk",
    "devil's advocate", "elephant in the room", "every cloud has a silver lining",
    "fish out of water", "green with envy", "head over heels",
    "hit the nail on the head", "in hot water", "let the cat out of the bag",
    "once in a blue moon", "raining cats and dogs", "see eye to eye",
    "spill the beans", "take with a grain of salt", "the ball is in your court",
    "through thick and thin", "under the weather", "up in the air",
})

# Readability: complex words that have simpler alternatives
SIMPLIFICATION_HINTS: dict[str, str] = {
    "utilize": "use", "commence": "start", "terminate": "end",
    "approximately": "about", "subsequently": "then", "consequently": "so",
    "nevertheless": "but", "furthermore": "also", "henceforth": "from now on",
    "notwithstanding": "despite", "in lieu of": "instead of",
    "prior to": "before", "subsequent to": "after", "in regard to": "about",
    "in the event that": "if", "due to the fact that": "because",
    "at the present time": "now", "in close proximity": "near",
    "in order to": "to", "with regard to": "about", "in the near future": "soon",
    "a large number of": "many", "a small number of": "few",
    "in the amount of": "of", "is of the opinion": "believes",
    "make an attempt": "try", "arrive at a conclusion": "conclude",
}

# Vocabulary enhancement: common words with richer alternatives (suggestions)
VOCAB_ENHANCEMENT: dict[str, list[str]] = {
    "said": ["declared", "whispered", "murmured", "exclaimed", "stated", "remarked"],
    "walked": ["strolled", "marched", "trudged", "wandered", "ambled", "strutted"],
    "ran": ["sprinted", "dashed", "bolted", "raced", "hurried", "rushed"],
    "looked": ["gazed", "stared", "glanced", "peered", "glared", "observed"],
    "big": ["immense", "enormous", "vast", "colossal", "massive", "substantial"],
    "small": ["tiny", "petite", "minuscule", "compact", "modest", "diminutive"],
    "good": ["excellent", "superb", "remarkable", "admirable", "splendid"],
    "bad": ["terrible", "dreadful", "awful", "horrible", "deplorable"],
    "happy": ["joyful", "elated", "delighted", "ecstatic", "content", "pleased"],
    "sad": ["melancholy", "sorrowful", "gloomy", "despondent", "mournful"],
    "angry": ["furious", "enraged", "irate", "livid", "incensed"],
    "scared": ["terrified", "frightened", "alarmed", "petrified", "apprehensive"],
    "tired": ["exhausted", "weary", "fatigued", "drained", "spent"],
    "fast": ["rapid", "swift", "quick", "speedy", "brisk", "hasty"],
    "slow": ["sluggish", "leisurely", "gradual", "unhurried", "deliberate"],
}


def get_overused_words() -> frozenset[str]:
    return OVERUSED_WORDS


def get_cliches() -> frozenset[str]:
    return CLICHES


def get_simplification_hint(word: str) -> str | None:
    return SIMPLIFICATION_HINTS.get(word.lower())


def get_vocab_enhancements(word: str) -> list[str]:
    return list(VOCAB_ENHANCEMENT.get(word.lower(), []))
