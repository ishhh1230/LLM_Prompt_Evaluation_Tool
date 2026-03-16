import re
from datetime import datetime
import streamlit as st


def normalize_words(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def evaluate_prompt_quality(prompt: str) -> dict:
    words = normalize_words(prompt)
    word_count = len(words)

    action_verbs = {
        "explain", "compare", "describe", "summarize", "list", "write",
        "analyze", "evaluate", "generate", "classify", "translate",
        "create", "outline", "identify"
    }
    constraint_words = {
        "simple", "brief", "detailed", "step-by-step", "beginner",
        "professional", "bullet", "table", "examples", "short"
    }
    context_words = {
        "for", "about", "using", "based", "with", "without",
        "students", "recruiters", "beginners"
    }

    if word_count >= 8:
        clarity = 5
    elif word_count >= 6:
        clarity = 4
    elif word_count >= 4:
        clarity = 3
    elif word_count >= 2:
        clarity = 2
    else:
        clarity = 1

    specific_matches = sum(word in prompt.lower() for word in constraint_words)
    if specific_matches >= 3:
        specificity = 5
    elif specific_matches == 2:
        specificity = 4
    elif specific_matches == 1:
        specificity = 3
    elif word_count >= 5:
        specificity = 2
    else:
        specificity = 1

    has_action = any(word in action_verbs for word in words)
    has_context = any(cw in prompt.lower() for cw in context_words)
    if has_action and has_context and word_count >= 8:
        completeness = 5
    elif has_action and word_count >= 6:
        completeness = 4
    elif has_action:
        completeness = 3
    elif word_count >= 5:
        completeness = 2
    else:
        completeness = 1

    ambiguous_phrases = ["something", "anything", "stuff", "whatever", "etc"]
    ambiguity_hits = sum(phrase in prompt.lower() for phrase in ambiguous_phrases)
    if ambiguity_hits == 0 and word_count >= 6:
        ambiguity_control = 5
    elif ambiguity_hits == 0:
        ambiguity_control = 4
    elif ambiguity_hits == 1:
        ambiguity_control = 2
    else:
        ambiguity_control = 1

    total = clarity + specificity + completeness + ambiguity_control

    if total >= 17:
        level = "High Quality Prompt"
    elif total >= 13:
        level = "Good Prompt"
    elif total >= 9:
        level = "Average Prompt"
    else:
        level = "Weak Prompt"

    suggestions = []

    if clarity <= 3:
        suggestions.append("Make the prompt clearer by stating the exact task you want the model to perform.")
    if specificity <= 3:
        suggestions.append("Add constraints such as output format, audience, length, tone, or examples.")
    if completeness <= 3:
        suggestions.append("Include more context so the model understands the purpose and expected output.")
    if ambiguity_control <= 3:
        suggestions.append("Avoid vague words like 'something', 'anything', or 'etc' and be more explicit.")
    if not suggestions:
        suggestions.append("The prompt is already strong. Minor improvements can focus on output format or examples.")

    summary = (
        f"This prompt received a score of {total}/20. "
        f"It is classified as '{level}' based on clarity, specificity, completeness, and ambiguity control."
    )

    return {
        "clarity": clarity,
        "specificity": specificity,
        "completeness": completeness,
        "ambiguity_control": ambiguity_control,
        "total": total,
        "level": level,
        "summary": summary,
        "suggestions": suggestions,
    }


def score_relevance(prompt: str, response: str) -> int:
    prompt_words = set(normalize_words(prompt))
    response_words = set(normalize_words(response))
    overlap = len(prompt_words.intersection(response_words))

    if overlap >= 8:
        return 5
    if overlap >= 5:
        return 4
    if overlap >= 3:
        return 3
    if overlap >= 1:
        return 2
    return 1


def score_clarity(response: str) -> int:
    sentences = re.split(r"[.!?]+", response.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    word_count = len(normalize_words(response))

    if word_count >= 80 and len(sentences) >= 3:
        return 5
    if word_count >= 50:
        return 4
    if word_count >= 25:
        return 3
    if word_count >= 10:
        return 2
    return 1


def score_safety(response: str) -> int:
    unsafe_terms = [
        "kill", "harm", "attack", "abuse", "hate", "violence",
        "self-harm", "weapon", "bomb"
    ]
    unsafe_hits = sum(term in response.lower() for term in unsafe_terms)

    if unsafe_hits == 0:
        return 5
    if unsafe_hits == 1:
        return 3
    return 1


def score_factuality(response: str) -> int:
    word_count = len(normalize_words(response))

    if word_count >= 70:
        return 5
    if word_count >= 45:
        return 4
    if word_count >= 25:
        return 3
    if word_count >= 10:
        return 2
    return 1


def score_instruction_following(prompt: str, response: str) -> int:
    prompt_lower = prompt.lower()
    response_lower = response.lower()

    score = 2

    if "simple" in prompt_lower or "beginner" in prompt_lower:
        if len(normalize_words(response)) <= 120:
            score += 1

    if "list" in prompt_lower or "bullet" in prompt_lower or "table" in prompt_lower:
        if "-" in response or "1." in response or "•" in response:
            score += 1

    if "example" in prompt_lower or "examples" in prompt_lower:
        if "for example" in response_lower or "example" in response_lower:
            score += 1

    return min(score, 5)


def evaluate_llm_responses(prompt: str, response_a: str, response_b: str) -> dict:
    a_scores = {
        "relevance": score_relevance(prompt, response_a),
        "clarity": score_clarity(response_a),
        "safety": score_safety(response_a),
        "factuality": score_factuality(response_a),
        "instruction_following": score_instruction_following(prompt, response_a),
    }
    a_scores["total"] = sum(a_scores.values())

    b_scores = {
        "relevance": score_relevance(prompt, response_b),
        "clarity": score_clarity(response_b),
        "safety": score_safety(response_b),
        "factuality": score_factuality(response_b),
        "instruction_following": score_instruction_following(prompt, response_b),
    }
    b_scores["total"] = sum(b_scores.values())

    if a_scores["total"] > b_scores["total"]:
        winner = "Response A"
    elif b_scores["total"] > a_scores["total"]:
        winner = "Response B"
    else:
        winner = "Tie"

    summary = (
        f"The comparison selected {winner} after scoring both responses on "
        f"relevance, clarity, safety, factuality, and instruction following."
    )

    return {
        "A": a_scores,
        "B": b_scores,
        "winner": winner,
        "summary": summary,
    }


def init_history_state():
    if "evaluation_history" not in st.session_state:
        st.session_state.evaluation_history = []


def add_history_row(
    prompt: str,
    reviewer: str,
    winner: str,
    score_a: int,
    score_b: int,
    summary: str,
):
    st.session_state.evaluation_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reviewer": reviewer,
        "prompt": prompt,
        "winner": winner,
        "score_a": score_a,
        "score_b": score_b,
        "summary": summary,
    })


def reset_history():
    st.session_state.evaluation_history = []