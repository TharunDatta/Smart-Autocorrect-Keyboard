# Typewise: Smart Autocorrect Keyboard

A responsive local text editor for dictionary-based spelling correction and corpus-trained next-word suggestions.

## Run the interface

Use Python 3.10+ from this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**. Type a sentence, then add a space or punctuation to trigger live correction. You can turn automatic correction off, use **Correct text** manually, undo the latest correction, clear the editor, or tap a suggested word. Three sample prompts are included.

The interface displays corpus size and a held-out next-word diagnostic from the included data. The top-5 score is **not** a general keyboard benchmark.

## Verify

```bash
python -m unittest discover -s tests -v
python evaluate.py
```

The tests cover punctuation, capitalization, contractions, API validation, cursor positioning, page loading, prediction, and the overview data.

## Implementation

- `autocorrect.py` uses `pyspellchecker` and the included corpus, preserving punctuation and basic case.
- `predictor.py` builds unigram, bigram and trigram counts from `data/corpus.txt`; trigram context receives the highest weight, then bigram context, with a common-word fallback.
- `app.py` offers `/autocorrect`, `/predict`, and `/api/overview`. Requests are size-limited and validated. The correction endpoint can return an adjusted cursor position.
- `static/script.js` discards stale responses so an older request cannot overwrite newer text.
- `templates/index.html` and `static/style.css` provide the responsive editor interface.

## Scope

This is an educational English-language web prototype, not a mobile or system-wide keyboard. The corpus is small and oriented toward student/project phrases. Suggested words are guesses; correction can occasionally change a word the writer intended, which is why the interface includes an undo control.
