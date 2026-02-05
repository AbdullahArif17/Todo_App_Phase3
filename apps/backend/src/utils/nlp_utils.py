from typing import List, Dict, Tuple, Optional
import re
from collections import Counter
import uuid


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple heuristics.

    Args:
        text: Input text to extract keywords from
        min_length: Minimum length of keywords to consider
        max_keywords: Maximum number of keywords to return

    Returns:
        List of extracted keywords
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())

    # Filter words by length and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'about', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down',
        'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'i', 'me', 'my', 'myself',
        'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your',
        'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
        'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
        'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
        'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing', 'would', 'should', 'could', 'ought', 'i'm', 'you're', 'he's',
        'she's', 'it's', 'we're', 'they're', 'i've', 'you've', 'we've', 'they've', 'i'd', 'you'd',
        'he'd', 'she'd', 'we'd', 'they'd', 'i'll', 'you'll', 'he'll', 'she'll', 'we'll', 'they'll',
        'isn', 'aren', 'wasn', 'weren', 'haven', 'hasn', 'hadn', 'doesn', 'don', 'didn', 'won',
        'wouldn', 'shan', 'shouldn', 'can', 'couldn', 'will', 'not', 'no', 'yes', 'ok'
    }

    filtered_words = [
        word for word in words
        if len(word) >= min_length and word not in stop_words
    ]

    # Count occurrences and return most frequent
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(max_keywords)]


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text (simple pattern-based extraction).

    Args:
        text: Input text to extract entities from

    Returns:
        Dictionary mapping entity types to lists of entities
    """
    entities = {
        'dates': [],
        'times': [],
        'numbers': [],
        'emails': [],
        'urls': [],
        'todos': []  # Based on common todo patterns
    }

    # Extract dates (various formats)
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or MM-DD-YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD
        r'(january|february|march|april|may|june|july|august|september|october|november|december)',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['dates'].extend(matches)

    # Extract times
    time_pattern = r'\d{1,2}:\d{2}\s*(am|pm)?'
    entities['times'] = re.findall(time_pattern, text, re.IGNORECASE)

    # Extract numbers
    number_pattern = r'\b\d+\b'
    entities['numbers'] = re.findall(number_pattern, text)

    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities['emails'] = re.findall(email_pattern, text)

    # Extract URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    entities['urls'] = re.findall(url_pattern, text)

    # Extract potential todo items (phrases after keywords like "add", "create", "remember")
    todo_pattern = r'(add|create|remember|remind me to|todo|task)[\s:]+([^.!?]+)(?=[.!?]|$)'
    todo_matches = re.findall(todo_pattern, text, re.IGNORECASE)
    entities['todos'] = [match[1].strip() for match in todo_matches]

    return entities


def calculate_sentence_importance(sentence: str, position: int, total_sentences: int) -> float:
    """
    Calculate the importance of a sentence for summarization.

    Args:
        sentence: Sentence to evaluate
        position: Position of sentence in text (0-indexed)
        total_sentences: Total number of sentences

    Returns:
        Importance score (higher is more important)
    """
    importance = 0.0

    # Sentences at the beginning and end are often more important
    if position == 0:
        importance += 1.0  # First sentence
    elif position == total_sentences - 1:
        importance += 0.8  # Last sentence

    # Longer sentences might contain more information
    words = sentence.split()
    if len(words) > 5 and len(words) < 20:  # Medium-length sentences are often important
        importance += 0.3

    # Sentences with question marks or exclamation points might be important
    if '?' in sentence or '!' in sentence:
        importance += 0.5

    # Sentences containing important keywords
    important_keywords = [
        'important', 'key', 'critical', 'essential', 'main', 'primary', 'summary',
        'conclusion', 'result', 'findings', 'solution', 'answer', 'decision'
    ]

    sentence_lower = sentence.lower()
    for keyword in important_keywords:
        if keyword in sentence_lower:
            importance += 0.4

    return importance


def generate_sentence_summary(sentences: List[str], num_sentences: int = 3) -> str:
    """
    Generate a summary by selecting the most important sentences.

    Args:
        sentences: List of sentences to summarize
        num_sentences: Number of sentences to include in summary

    Returns:
        Generated summary string
    """
    if len(sentences) <= num_sentences:
        return ' '.join(sentences)

    # Calculate importance for each sentence
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = calculate_sentence_importance(sentence, i, len(sentences))
        sentence_scores.append((sentence, score))

    # Sort by importance and select top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    top_sentences = sentence_scores[:num_sentences]

    # Return sentences in their original order
    result = []
    for sent in sentences:
        if sent in [s[0] for s in top_sentences]:
            result.append(sent)

    return ' '.join(result[:num_sentences])


def extract_conversation_topics(messages: List[str], num_topics: int = 3) -> List[Tuple[str, int]]:
    """
    Extract main topics from a series of conversation messages.

    Args:
        messages: List of message texts
        num_topics: Number of top topics to return

    Returns:
        List of tuples containing (topic, frequency)
    """
    all_text = ' '.join(messages)

    # Extract keywords from all messages
    keywords = extract_keywords(all_text, min_length=3, max_keywords=20)

    # Group related keywords to form topics
    topics = []
    for keyword in keywords:
        # Simple topic formation - in practice, this would use more sophisticated clustering
        topics.append((keyword, 1))  # For now, just return keywords as topics

    return topics[:num_topics]


def classify_message_intent(text: str) -> str:
    """
    Classify the intent of a message based on keywords.

    Args:
        text: Input text to classify

    Returns:
        Classified intent
    """
    text_lower = text.lower()

    # Define intent patterns
    intents = {
        'todo_add': ['add', 'create', 'make', 'new', 'put', 'enter', 'schedule'],
        'todo_remove': ['remove', 'delete', 'cancel', 'clear', 'eliminate'],
        'todo_update': ['update', 'change', 'modify', 'edit', 'fix', 'adjust'],
        'todo_complete': ['complete', 'finish', 'done', 'accomplish', 'achieve'],
        'todo_list': ['list', 'show', 'display', 'view', 'see', 'what'],
        'question': ['what', 'how', 'when', 'where', 'why', 'who', 'which', 'can', 'could', 'would', 'should'],
        'greeting': ['hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening'],
        'affirmation': ['yes', 'ok', 'okay', 'sure', 'absolutely', 'indeed', 'exactly'],
        'negation': ['no', 'not', 'never', 'nothing', 'nowhere', 'neither', 'nor']
    }

    # Count matches for each intent
    intent_scores = {}
    for intent, keywords in intents.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        intent_scores[intent] = score

    # Return the intent with the highest score
    if max(intent_scores.values()) > 0:
        return max(intent_scores, key=intent_scores.get)
    else:
        return 'unknown'


def detect_conversation_sentiment(text: str) -> str:
    """
    Detect the sentiment of text using simple keyword matching.

    Args:
        text: Input text to analyze

    Returns:
        Detected sentiment ('positive', 'negative', 'neutral')
    """
    positive_words = [
        'good', 'great', 'excellent', 'awesome', 'wonderful', 'fantastic', 'brilliant',
        'perfect', 'amazing', 'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied',
        'thank', 'thanks', 'grateful', 'appreciate', 'well done', 'nice', 'cool', 'super'
    ]

    negative_words = [
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'angry',
        'annoyed', 'frustrated', 'sad', 'upset', 'disappointed', 'disgusted', 'mad',
        'sucks', 'stupid', 'dumb', 'wrong', 'problem', 'issue', 'error', 'fail', 'shit'
    ]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'