import os
import json
import difflib
import time
import uuid
import re
from datetime import datetime, timezone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Load all clause dictionaries from /data
DATA_DIR = "data"
STANDARDS = {}
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_PATH = os.path.join(LOG_DIR, "audit_log.json")
GLOSSARY_PATH = os.path.join(os.path.dirname(__file__), "glossary.json")
os.makedirs(LOG_DIR, exist_ok=True)

def _ensure_log_file():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)

def _load_logs():
    _ensure_log_file()
    with open(LOG_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _write_logs(entries):
    with open(LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)

def _record_audit(question, clauses, answer, confidence, latency_ms):
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "clauses": [
            {
                "standard": c["standard"],
                "clause": c["clause"],
                "score": round(c["score"], 3),
            }
            for c in clauses
        ],
        "answer": answer,
        "confidence": confidence,
        "latency_ms": round(latency_ms, 2),
        "flagged": False,
    }
    entries = _load_logs()
    entries.append(entry)
    _write_logs(entries)

for file in os.listdir(DATA_DIR):
    if file.endswith(".json"):
        name = os.path.splitext(file)[0]
        with open(os.path.join(DATA_DIR, file), "r") as f:
            STANDARDS[name] = json.load(f)

if os.path.exists(GLOSSARY_PATH):
    with open(GLOSSARY_PATH, "r") as f:
        GLOSSARY = json.load(f)
else:
    GLOSSARY = {}

def normalize_question(text: str) -> str:
    normalized = text.lower()
    for slang, proper in GLOSSARY.items():
        normalized = normalized.replace(slang, proper)
    return normalized

def find_best_matches(question, standard_data, top_n=3):
    scored = [
        (clause, difflib.SequenceMatcher(None, question.lower(), text.lower()).ratio())
        for clause, text in standard_data.items()
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]

def get_answer(question):
    start = time.perf_counter()
    normalized_question = normalize_question(question)
    explicit_clauses = set(re.findall(r"\b\d+(?:\.\d+)+\b", normalized_question))

    combined_results = []
    for name, data in STANDARDS.items():
        matches = find_best_matches(normalized_question, data)
        for clause, score in matches:
            combined_results.append({
                "standard": name,
                "clause": clause,
                "text": data[clause],
                "score": score
            })

    # Get top results across all standards
    top = sorted(combined_results, key=lambda x: x["score"], reverse=True)[:5]

    elapsed_ms = (time.perf_counter() - start) * 1000
    if not top:
        answer_text = "No relevant clauses found in any standard."
        _record_audit(question, [], answer_text, 0.0, elapsed_ms)
        return {
            "answer": answer_text,
            "confidence": 0.0
        }

    direct_hits = []
    seen = set()
    for clause_id in explicit_clauses:
        for standard_name, clauses in STANDARDS.items():
            if clause_id in clauses:
                key = (standard_name, clause_id)
                if key in seen:
                    continue
                seen.add(key)
                direct_hits.append({
                    "standard": standard_name,
                    "clause": clause_id,
                    "text": clauses[clause_id],
                    "score": 1.0
                })

    context_entries = direct_hits + top
    # Build context for GPT
    context = "\n\n".join([
        f"{t['standard']} Clause {t['clause']}:\n{t['text']}"
        for t in context_entries
    ])

    max_score = top[0]["score"] if top else 0.0

    prompt = (
        "You are SparkAI, an electrical compliance advisor for Australian electricians. "
        "You are an Expert Electrician and have a sound Knowledge of Austalian Standards and Regulations"
        "Ground your answer in the supplied clauses whenever possible, citing the clause number and document. "
        "If the clauses do not cover the entire question, combine any relevant clauses with your broader electrical knowledge "
        "to provide the most accurate guidance available, and clearly distinguish between clause-backed facts and expert interpretation. "
        "Never leave the user unanswered—offer your best professional assessment while reminding them to validate against the latest standard.\n\n"
        f"Reference clauses:\n{context}\n\nQuestion: {question}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer_text = response.choices[0].message.content
    confidence = round(max_score, 3)
    elapsed_ms = (time.perf_counter() - start) * 1000
    _record_audit(question, context_entries, answer_text, confidence, elapsed_ms)
    return {
        "answer": answer_text,
        "confidence": confidence
    }

def get_audit_logs(limit: int = 50):
    entries = _load_logs()
    return list(reversed(entries))[:limit]

def flag_audit_entry(log_id: str, flagged: bool = True):
    entries = _load_logs()
    for entry in entries:
        if entry["id"] == log_id:
            entry["flagged"] = flagged
            _write_logs(entries)
            return entry
    raise KeyError(f"log_id {log_id} not found")
