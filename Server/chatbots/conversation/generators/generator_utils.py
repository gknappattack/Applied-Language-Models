import re
import wikipedia
from typing import List, Union

custom_stop_words = [
    'sure',
    'yes',
    'why not',
    'not',
    'thanks',
    'no thanks',
    'thank you',
    'no thank you',
    'name',
    'my name',
    'your name',
    'who are you',
    'i didn\'t know that',
    'what\'s your name',
    'what\'s my name',
    'what my name is',
    'what your name is',
    'war',
    'ago',
    'gene',
    'yes',
    'no',
    'i have',
    'book',
    'books',
    'you',
    'me',
    'we',
    'them',
    'he',
    'she',
    'it',
    'they',
    'with',
    'for',
    'that',
    'if',
    'maybe',
    'right',
    'wrong',
    'good',
    'bad',
    'up',
    'down',
    'social',
    'movie',
    'book',
    'movies',
    'literature',
    'neither',
    'both',
    'stop',
    'tonight',
    'tomorrow',
    'yesterday',
    'really',
    'anything',
    'nothing',
    'couple',
    'few',
    'some',
    'sometimes',
    'sad',
    'happy',
    'terrible',
    'bored',
    'depressed',
    'angry',
    'depressing',
    'suicide',
    'suicidal',
    'murder',
    'scared',
    'scary',
    'good',
    'bad',
    'interesting',
    'cool',
    'awesome',
    'fine',
    'good',
    'wow',
    'hitler',
    'food',
    'news',
    'politics',
    'book',
    'books',
    'movie',
    'movies'
    'pirate',
    'mein kampf',
    'game',
    'games',
    'videogame',
    'videogames',
    'thanks',
    'no thanks',
    'thank you',
    'video game',
    'video games',
    "don't",
    'know',
    'dunno',
    'sure',
    'okay',
    'OK',
    'ok',
    'fine',
    'to',
    'too',
    '1',
    'one',
    'acting',
    'the acting',
    'the',
    'actor',
    'director',
    'the effects',
    'special effects',
    'special',
    'effects',
    'chat',
    'chatting',
    'talk',
    'talking',
    'uh',
    'um',
    'uhhh',
    'ummm',
    'sport',
    'sports',
    'new',
    'news',
    'celebrities',
    'finance',
]


def get_template_keywords(keywords, response):
    used_keywords = []
    for keyword in keywords:
        if keyword and keyword.lower() in response.lower():
            used_keywords.append(keyword)
    return list(set(used_keywords))


def get_pruned_key_words(input_data):
    # pull ner and handpicked_keywords
    full_ner = input_data.get('ner', [])
    if full_ner:
        ner = [x.get("text", []) for x in full_ner]
    else:
        ner = []
    handpicked_keywords = input_data.get('handpicked_keywords', [])

    # concatenate keywords
    key_words = []
    if handpicked_keywords:
        key_words += handpicked_keywords
    if ner:
        key_words += ner

    # hack to prevent common fails
    key_words = set(key_words)
    stripped_key_words = set()
    for w in key_words:
        if w not in custom_stop_words:
            stripped_key_words.add(w)
    return list(stripped_key_words)


def get_sentences(
        text= str,
        caps="([A-Z])",
        digits="([0-9])",
        prefixes="(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]",
        suffixes="(Inc|Ltd|Jr|Sr|Co)",
        starters="(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)",
        acronyms="([A-Z][.][A-Z][.](?:[A-Z][.])?)",
        websites="[.](com|net|org|io|gov|me|edu)",
):
    """Split text into sentences; taken from: https://stackoverflow.com/a/31505798.
    Returns:
        List[str]: The sentences.
    """
    if not isinstance(text, str):
        raise TypeError("can only get_sentences of a str".format(text))

    text = " " + text + "<stop>"
    text = text.replace("\n", " ")
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    if "Ph.D" in text:
        text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + caps + "[.]", " \\1<prd>", text)

    if '"' in text:
        text = text.replace('."', '".')
    if "\"" in text:
        text = text.replace(".\"", "\".")
    if "!" in text:
        text = text.replace("!\"", "\"!")
    if "?" in text:
        text = text.replace("?\"", "\"?")
    if "..." in text:
        text = text.replace("...", "<prd><prd><prd>")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")

    sentences = []
    for chunk in text.split("<stop>"):
        sentence = chunk.strip()
        if sentence:
            sentences.append(sentence)

    return sentences


def get_wikipedia_summary(query= str, sentences=5):
    """Get a Wikipedia article summary for query.
    Returns:
        List[str]: The sentences of the summary.
    """

    stop_words = ['sports','books','news','literature','movies']

    if query not in stop_words:
        return wikipedia.summary(query, sentences=sentences)
    else:
        return ""


def break_long_response(
        text= Union[str, List[str]],
        response_modifier=lambda x: x + ' Would you like to hear more?',
        more_info_modifier=lambda x: "OK here is some more info for you: " + x,
        sentence_limit=5,
        word_limit=40,
        word_limit_tolerance=5,
):
    if not text:
        return text, ""

    if not isinstance(text, str):
        text = " ".join(text)

    sentences = get_sentences(text)

    word_count = 0
    for i, sentence in enumerate(sentences):
        words_in_sentence = len(sentence.split(" "))
        if i >= sentence_limit and words_in_sentence > word_limit_tolerance:
            break

        new_word_count = words_in_sentence + word_count
        if new_word_count > word_limit + word_limit_tolerance:
            break
        word_count = new_word_count

    break_at = i + 1
    response = " ".join(sentences[:break_at])
    more_info = " ".join(sentences[break_at:])

    if more_info:
        response = response_modifier(response)
        more_info = more_info_modifier(more_info)

    return response, more_info


if __name__ == '__main__':
    doc = ["{}.".format(num) if i > 0 and i % 10 == 0 else str(num) for i, num in enumerate(range(57))]
    print(break_long_response(doc), sep='/n/n')
