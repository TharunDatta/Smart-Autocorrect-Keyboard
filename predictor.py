import re
from collections import Counter, defaultdict
from pathlib import Path


class NGramPredictor:

    def __init__(self, corpus_path):
        self.unigrams = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()

        self.bigram_context = defaultdict(Counter)
        self.trigram_context = defaultdict(Counter)

        self.train(corpus_path)

    def tokenize(self, text):
        return re.findall(r"[a-zA-Z']+", text.lower())

    def train(self, corpus_path):

        with Path(corpus_path).open("r", encoding="utf-8") as file:
            text = file.read()

        sentences = re.split(r"[.!?]+", text)

        for sentence in sentences:

            tokens = self.tokenize(sentence)

            if not tokens:
                continue

            for word in tokens:
                self.unigrams[word] += 1

            for i in range(len(tokens) - 1):

                pair = (tokens[i], tokens[i + 1])

                self.bigrams[pair] += 1

                self.bigram_context[tokens[i]][tokens[i + 1]] += 1

            for i in range(len(tokens) - 2):

                triple = (
                    tokens[i],
                    tokens[i + 1],
                    tokens[i + 2]
                )

                self.trigrams[triple] += 1

                context = (
                    tokens[i],
                    tokens[i + 1]
                )

                self.trigram_context[context][tokens[i + 2]] += 1

    def predict(self, text, number_of_suggestions=5):

        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if number_of_suggestions < 1:
            return []

        tokens = self.tokenize(text)

        if not tokens:
            return self.most_common_words(number_of_suggestions)

        suggestions = Counter()

        # Trigram prediction
        if len(tokens) >= 2:

            context = (
                tokens[-2],
                tokens[-1]
            )

            for word, count in self.trigram_context[context].items():
                suggestions[word] += count * 3

        # Bigram prediction
        last_word = tokens[-1]

        for word, count in self.bigram_context[last_word].items():
            suggestions[word] += count * 2

        # If no contextual prediction exists,
        # use common words.
        if not suggestions:
            return self.most_common_words(number_of_suggestions)

        # Add a small unigram score
        for word in list(suggestions.keys()):
            suggestions[word] += self.unigrams[word] * 0.05

        result = [
            word
            for word, _ in suggestions.most_common(number_of_suggestions)
        ]

        return result

    def most_common_words(self, number_of_suggestions=5):

        return [
            word
            for word, _ in self.unigrams.most_common(number_of_suggestions)
        ]
