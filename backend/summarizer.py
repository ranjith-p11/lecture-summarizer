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


def summarize_text(text: str, length: str = "medium") -> str:
    """
    Summarize the given text using LSA.

    Args:
        text:   The input text to summarize.
        length: One of 'short', 'medium', 'long'.

    Returns:
        A string containing the summary sentences joined with spaces.
    """
    if not text or not text.strip():
        return "No text provided for summarization."

    sentence_count = SENTENCE_COUNTS.get(length, 5)

    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    sentences = summarizer(parser.document, sentence_count)
    summary = " ".join(str(s) for s in sentences)

    return summary if summary.strip() else "Could not generate a summary for the provided text."
