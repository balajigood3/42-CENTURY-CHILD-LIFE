"""Lightweight scientific discovery workflow over supplied research notes."""
from __future__ import annotations
import re
from collections import Counter

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "were", "was",
    "are", "is", "in", "on", "to", "of", "a", "an", "by", "as", "at",
    "it", "be", "we", "our", "their", "these", "those", "can", "may"
}

def tokenize(text):
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text)
            if w.lower() not in STOPWORDS]

def analyze_research(documents, research_question, top_k=10):
    if not isinstance(documents, list) or not documents:
        raise ValueError("Provide at least one research document.")
    if not isinstance(research_question, str) or not research_question.strip():
        raise ValueError("Research question must not be empty.")
    if not isinstance(top_k, int) or not 1 <= top_k <= 50:
        raise ValueError("top_k must be between 1 and 50.")
    cleaned = []
    for i, doc in enumerate(documents):
        if not isinstance(doc, dict) or not isinstance(doc.get("title"), str) or not doc["title"].strip():
            raise ValueError(f"Document {i+1} needs a title.")
        if not isinstance(doc.get("text"), str) or not doc["text"].strip():
            raise ValueError(f"Document {i+1} needs non-empty text.")
        cleaned.append({"title": doc["title"].strip(), "text": doc["text"].strip()})
    question_terms = set(tokenize(research_question))
    corpus = Counter()
    per_doc = []
    for doc in cleaned:
        terms = tokenize(doc["text"])
        corpus.update(terms)
        overlap = sorted(question_terms.intersection(terms))
        per_doc.append({
            "title": doc["title"],
            "word_count": len(terms),
            "question_term_overlap": overlap,
            "overlap_score": len(overlap) / max(1, len(question_terms))
        })
    keywords = [{"term": term, "frequency": count} for term, count in corpus.most_common(top_k)]
    gaps = sorted(question_terms - set(corpus))
    ranked_docs = sorted(per_doc, key=lambda x: (-x["overlap_score"], x["title"].lower()))
    return {
        "research_question": research_question.strip(),
        "document_count": len(cleaned),
        "documents": ranked_docs,
        "frequent_terms": keywords,
        "question_terms_not_found": gaps,
        "candidate_research_gaps": [
            f"The supplied documents do not contain the question term '{term}'. Check additional literature before treating this as a genuine research gap."
            for term in gaps
        ],
        "suggested_next_steps": [
            "Search additional peer-reviewed literature for missing question terms.",
            "Compare study methods, datasets, populations and evaluation metrics.",
            "Check whether findings replicate across independent studies.",
            "Ask a domain expert to validate any proposed research gap."
        ],
        "method": "Keyword frequency and question-term overlap; no semantic literature review or causal inference."
    }

def build_hypothesis_templates(research_question, missing_terms):
    if not isinstance(research_question, str) or not research_question.strip():
        raise ValueError("Research question must not be empty.")
    if not isinstance(missing_terms, list):
        raise ValueError("missing_terms must be a list.")
    topic = research_question.strip()
    return [
        {
            "hypothesis": f"Investigate whether {topic} differs across relevant datasets or conditions.",
            "null_hypothesis": "There is no measurable difference across the selected conditions.",
            "test_design": "Define variables, preregister metrics, select a representative dataset and compare against a baseline.",
            "evidence_needed": list(missing_terms),
            "status": "candidate for expert review; not a scientific finding"
        }
    ]
