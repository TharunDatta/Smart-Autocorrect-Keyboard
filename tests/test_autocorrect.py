import tempfile
import unittest
from pathlib import Path

from autocorrect import AutoCorrect


class AutoCorrectTests(unittest.TestCase):
    def test_preserves_punctuation_and_case(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.txt"
            corpus.write_text("hello world\nhello project\n", encoding="utf-8")
            corrector = AutoCorrect(corpus)

            self.assertEqual(corrector.correct_sentence("Teh, WORLD!"), "The, WORLD!")

    def test_preserves_contractions(self):
        corrector = AutoCorrect()

        self.assertEqual(corrector.correct_sentence("I don't know."), "I don't know.")

    def test_rejects_non_string_input(self):
        corrector = AutoCorrect()

        with self.assertRaisesRegex(TypeError, "string"):
            corrector.correct_sentence(None)


if __name__ == "__main__":
    unittest.main()
