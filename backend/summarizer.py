"""
summarizer.py – LSA-based text summarization using sumy
"""
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Download NLTK punkt tokenizer data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

LANGUAGE = "english"

SENTENCE_COUNTS = {
    "short":  3,
    "medium": 5,
    "long":   8,
}


def summarize_text(text: str, length: str = "medium") -> dict:
    """
    Summarize the given text using LSA.

    Args:
        text:   The input text to summarize.
        length: One of 'short', 'medium', 'long'.

    Returns:
        A dictionary with 'summary' (string) and 'key_points' (list of strings).
    """
    if not text or not text.strip():
        return {"summary": "No text provided for summarization.", "key_points": []}

    sentence_count = SENTENCE_COUNTS.get(length, 5)

    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    sentences = summarizer(parser.document, sentence_count)
    summary_str = " ".join(str(s) for s in sentences)
    
    # Extract 5 to 8 key points natively
    kp_count = max(5, min(8, sentence_count))
    kp_sentences = summarizer(parser.document, kp_count)
    key_points = [str(s) for s in kp_sentences]

    if not summary_str.strip():
        return {"summary": "Could not generate a summary for the provided text.", "key_points": []}

    return {"summary": summary_str, "key_points": key_points}
