"""
Module that search the best completion in the data structure for a specific input
"""
from typing import List, Tuple
import archive_reader
import string
import re
import os


class AutoCompleteData:
    def __init__(self,
                 completed_sentence: str,
                 source_text: str,
                 offset: int,
                 score: int,
                 matched_substring: str,
                 match_span: Tuple[int, int]):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score
        self.matched_substring = matched_substring
        self.match_span = match_span

    def __repr__(self):
        source_name = os.path.basename(self.source_text)
        return f'{self.completed_sentence} ({source_name} {self.offset})'


class AutoCompletor:
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.reader = archive_reader.Reader(archive_path)
        self.sentences = self.reader.get_sentences()

    def search(self, substring: str) -> List[AutoCompleteData]:
        substring = re.sub(r"\s+", " ", substring).strip()
        substring = re.sub(r",", "", substring).strip()
        results: List[AutoCompleteData] = []
        fuzzy_candidates = {}
        q_lower = substring.lower()
        for sentence in self.sentences:
            text = sentence.content
            tl = text.lower()

            if q_lower in tl:
                # 1) perfect phrase/word match
                if is_perfect_match(substring, text):
                    start = tl.index(q_lower)
                    end = start + len(substring)
                    score = len(substring) * 2
                    results.append(AutoCompleteData(
                        completed_sentence=text,
                        source_text=sentence.source_path,
                        offset=sentence.offset,
                        score=score,
                        matched_substring=substring,
                        match_span=(start, end),
                    ))
                    continue

        if not results and len(results) < 5:
            fuzzy_rx = self.build_regex(substring)
            fuzzy_candidates = set(self.search_sentences(substring))

        return results + list(fuzzy_candidates)

    def build_regex(self, query):
        escaped = re.escape(query)
        patterns = [escaped]  # Perfect match
        # Single character substitution
        for i in range(len(query)):
            pattern = escaped[:i] + '.' + escaped[i + 1:]
            patterns.append(pattern)
        # Single character addition
        for i in range(len(query) + 1):
            pattern = escaped[:i] + '.' + escaped[i:]
            patterns.append(pattern)
        # # Single character deletion (subtraction) - fixed here
        for i in range(len(query)):
            part = query[:i] + query[i + 1:]
            pattern = re.escape(part)
            patterns.append(pattern)
        combined_pattern = '|'.join(patterns)
        return re.compile(combined_pattern)

    def search_sentences(self, query):
        regex = self.build_regex(query)
        return [s for s in self.sentences if regex.search(s.content)]

    def get_text(self, r):
        if hasattr(r, 'content'):
            return r.content.lower()
        elif hasattr(r, 'completed_sentence'):
            return r.completed_sentence.lower()
        else:
            return ""  # fallback if neither attribute

    def get_best_k_completions(self, prefix: str) -> List[AutoCompleteData]:
        hits = self.search(prefix)
        # Rank: higher score first; tie-break by sentence text (case-insensitive)
        hits.sort(key=lambda r: (-r.score, self.get_text(r)))
        return hits[:5]


def is_perfect_match(query: str, sentence: str) -> bool:
    """
    Perfect match == query appears as a phrase of whole words in the sentence.
    Case-insensitive, ignores punctuation and variable spaces between words.
    Examples that will match "my name":
      "My name"
      "my, name"
      "MY   NAME"
      "my - name"
    """
    tokens = re.findall(r"\w+", query.lower())
    if not tokens:
        return False
    # Build a pattern that allows any non-word chars between tokens, and
    # enforces word boundaries at the ends, so we don't match inside larger words.
    pattern = r"\b" + r"\W+".join(map(re.escape, tokens)) + r"\b"
    return re.search(pattern, sentence.lower()) is not None


def calc_score(query: str, match_text: str) -> int:
    """
    Calculates the score between the user query and the matched text,
    following the project definition rules.

    query: the text the user typed
    match_text: the matching substring from the sentence
    """
    # --- 1. Normalize (lowercase, remove punctuation) ---
    table = str.maketrans('', '', string.punctuation)
    q_norm = query.lower().translate(table)
    m_norm = match_text.lower().translate(table)

    # Base score: 2 points per matching letter (including spaces)
    # We'll also track mismatches to apply penalties.
    score = 0
    penalties = 0

    # --- 2. Compare character-by-character ---
    min_len = min(len(q_norm), len(m_norm))
    for i in range(min_len):
        if q_norm[i] == m_norm[i]:
            score += 2
        else:
            # wrong character
            penalties += incorrect_letter_penalty(i)

    # --- 3. If length mismatch, treat as added/missing letters ---
    length_diff = len(q_norm) - len(m_norm)
    if length_diff != 0:
        # only 1 edit is allowed according to the project
        if abs(length_diff) > 1:
            return 0  # invalid match
        # Apply penalty for the position of the missing/added char
        penalties += missing_or_added_penalty(min_len)

    # Apply penalties
    score -= penalties
    return score


def incorrect_letter_penalty(position: int) -> int:
    """Penalty for incorrect letter at given 0-based position."""
    if position == 0:
        return 5
    elif position == 1:
        return 4
    elif position == 2:
        return 3
    elif position == 3:
        return 2
    else:
        return 1


def missing_or_added_penalty(position: int) -> int:
    """Penalty for missing or added letter at given 0-based position."""
    if position == 0:
        return 10
    elif position == 1:
        return 8
    elif position == 2:
        return 6
    elif position == 3:
        return 4
    else:
        return 2
