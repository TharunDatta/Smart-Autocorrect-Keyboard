const editor = document.querySelector("#textInput");
const suggestions = document.querySelector("#suggestions");
const message = document.querySelector("#editorMessage");
const correctionText = document.querySelector("#correctionText");
const undoButton = document.querySelector("#undoButton");
const autoToggle = document.querySelector("#autoToggle");
let predictionTimer;
let predictionVersion = 0;
let correctionVersion = 0;
let undoState = null;

function setMessage(text, kind = "") {
  message.textContent = text;
  message.className = "editor-message" + (kind ? " " + kind : "");
}

function updateCounts() {
  const value = editor.value;
  const words = value.trim() ? value.trim().split(/\s+/).length : 0;
  document.querySelector("#wordCount").textContent = words + (words === 1 ? " word" : " words");
  document.querySelector("#charCount").textContent = value.length + (value.length === 1 ? " character" : " characters");
}

function setUndo(before, cursor) {
  undoState = { before, cursor };
  undoButton.disabled = false;
}

function showCorrection(before, after) {
  const a = before.match(/[A-Za-z']+/g) || [];
  const b = after.match(/[A-Za-z']+/g) || [];
  let index = 0;
  while (index < a.length && a[index] === b[index]) index++;
  correctionText.textContent = index < a.length && index < b.length
    ? a[index] + "  →  " + b[index]
    : "Text corrected. Use Undo if that was not intended.";
}

async function correctText(quiet = false) {
  const before = editor.value;
  const cursor = editor.selectionStart;
  const requestVersion = ++correctionVersion;
  if (!before.trim()) {
    if (!quiet) setMessage("Write something first, then try correction.");
    return;
  }
  if (!quiet) setMessage("Checking your text…");
  try {
    const response = await fetch("/autocorrect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: before, cursor }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Correction failed");
    if (requestVersion !== correctionVersion || editor.value !== before) return;
    if (data.corrected !== before) {
      setUndo(before, cursor);
      editor.value = data.corrected;
      const nextCursor = Number.isInteger(data.cursor) ? data.cursor : cursor;
      editor.setSelectionRange(nextCursor, nextCursor);
      showCorrection(before, data.corrected);
      setMessage("Correction applied. Undo if you prefer your original wording.", "success");
      updateCounts();
      schedulePrediction();
    } else if (!quiet) {
      setMessage("No spelling changes suggested.", "success");
    }
  } catch (error) {
    setMessage(error.message || "Unable to correct text.", "error");
  }
}

function renderSuggestions(words) {
  suggestions.replaceChildren();
  if (!words.length) {
    const empty = document.createElement("div");
    empty.className = "empty-suggestions";
    empty.textContent = "No suggestions for this context yet.";
    suggestions.append(empty);
    return;
  }
  words.forEach((word) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "suggestion";
    button.textContent = word;
    button.addEventListener("click", () => insertSuggestion(word));
    suggestions.append(button);
  });
}

async function predictWords() {
  const text = editor.value;
  const cursor = editor.selectionStart;
  const version = ++predictionVersion;
  if (!text.trim()) {
    document.querySelector("#suggestionContext").textContent = "· START TYPING";
    renderSuggestions([]);
    return;
  }
  document.querySelector("#suggestionContext").textContent = "· FROM YOUR CONTEXT";
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text.slice(0, cursor) }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prediction failed");
    if (version !== predictionVersion || editor.value !== text || editor.selectionStart !== cursor) return;
    renderSuggestions(data.suggestions || []);
  } catch (error) {
    if (version === predictionVersion) renderSuggestions([]);
    setMessage(error.message || "Suggestions are unavailable.", "error");
  }
}

function schedulePrediction() {
  clearTimeout(predictionTimer);
  predictionVersion++;
  predictionTimer = setTimeout(predictWords, 220);
}

function insertSuggestion(word) {
  const start = editor.selectionStart;
  const end = editor.selectionEnd;
  const before = editor.value.slice(0, start);
  const after = editor.value.slice(end);
  const prefix = before && !/\s$/.test(before) ? " " : "";
  const suffix = after && !/^\s/.test(after) ? " " : " ";
  const insertion = prefix + word + suffix;
  editor.value = before + insertion + after;
  const position = before.length + insertion.length;
  editor.focus();
  editor.setSelectionRange(position, position);
  correctionVersion++;
  updateCounts();
  schedulePrediction();
  setMessage('Added "' + word + '" to your text.', "success");
}

editor.addEventListener("input", (event) => {
  correctionVersion++;
  updateCounts();
  schedulePrediction();
  if (!event.isComposing && autoToggle.checked && typeof event.data === "string" && /[\s.!?,;:]/.test(event.data)) {
    correctText(true);
  }
});
editor.addEventListener("click", schedulePrediction);
editor.addEventListener("keyup", (event) => {
  if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) schedulePrediction();
});
document.querySelector("#correctButton").addEventListener("click", () => correctText());
document.querySelector("#clearButton").addEventListener("click", () => {
  editor.value = "";
  correctionVersion++;
  predictionVersion++;
  undoState = null;
  undoButton.disabled = true;
  correctionText.textContent = "Nothing to correct yet. Keep writing!";
  setMessage("Editor cleared. Start a new sentence.");
  updateCounts();
  renderSuggestions([]);
  document.querySelector("#suggestionContext").textContent = "· START TYPING";
  editor.focus();
});
undoButton.addEventListener("click", () => {
  if (!undoState) return;
  editor.value = undoState.before;
  editor.focus();
  editor.setSelectionRange(undoState.cursor, undoState.cursor);
  undoState = null;
  undoButton.disabled = true;
  correctionVersion++;
  correctionText.textContent = "Last correction undone.";
  setMessage("Restored your original text.", "success");
  updateCounts();
  schedulePrediction();
});
document.querySelectorAll("[data-example]").forEach((button) => {
  button.addEventListener("click", () => {
    editor.value = button.dataset.example;
    editor.focus();
    editor.setSelectionRange(editor.value.length, editor.value.length);
    correctionVersion++;
    updateCounts();
    schedulePrediction();
    setMessage("Sample loaded. Click Correct text or continue typing.");
  });
});
fetch("/api/overview")
  .then((response) => response.ok ? response.json() : Promise.reject(new Error("Overview unavailable")))
  .then((data) => {
    document.querySelector("#statWords").textContent = Number(data.corpus_words).toLocaleString();
    document.querySelector("#statUnique").textContent = Number(data.unique_words).toLocaleString();
    document.querySelector("#statTopFive").textContent = Math.round(data.evaluation.top_5_accuracy * 100) + "%";
    document.querySelector("#evaluationNote").textContent = data.evaluation.note + " Based on " + data.evaluation.held_out_sentences + " held-out sentences.";
  })
  .catch(() => {
    document.querySelector("#evaluationNote").textContent = "Model statistics are temporarily unavailable.";
  });
updateCounts();
