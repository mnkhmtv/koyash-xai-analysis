def detect_tone(text: str) -> str:
    if not text:
        return "neutral"

    text = text.lower()

    positive_words = [
        "recommend",
        "great",
        "effective",
        "good",
        "best",
        "suitable",
    ]

    negative_words = [
        "avoid",
        "not recommended",
        "bad",
        "irritating",
        "harmful",
    ]

    pos_score = sum(word in text for word in positive_words)
    neg_score = sum(word in text for word in negative_words)

    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    else:
        return "neutral"