import re
from pathlib import Path

from spellchecker import SpellChecker


class AutoCorrect:
    def __init__(self, corpus_path=None):
        self.spell = SpellChecker()
        if corpus_path:
            path = Path(corpus_path)
            if path.is_file():
                self.spell.word_frequency.load_text_file(str(path))

    def candidates(self, word):
        word = word.lower()
        if not word:
            return []

        cands = self.spell.candidates(word)
        if not cands:
            return [word]

        return sorted(
            cands,
            key=lambda candidate: (-self.spell.word_usage_frequency(candidate), candidate),
        )[:5]

    def correct_word(self, word):
        if not word or "'" in word or "’" in word:
            return word

        clean_word = word.lower()

        # Let pyspellchecker find the best correction
        best_word = self.spell.correction(clean_word)

        if not best_word:
            return word

        if word.isupper():
            best_word = best_word.upper()
        elif word[0].isupper():
            best_word = best_word.capitalize()

        return best_word

    def correct_sentence(self, sentence):
        if not isinstance(sentence, str):
            raise TypeError("sentence must be a string")

        return re.sub(
            r"[A-Za-z]+(?:['’][A-Za-z]+)*",
            lambda match: self.correct_word(match.group(0)),
            sentence,
        )
