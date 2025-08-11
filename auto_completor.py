"""
Module that search the best completion in the data structure for a specific input
"""
from typing import List, Tuple
import archive_reader
import string
import re

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
        return (f"AutoCompleteData("
                f"score={self.score}, "
                f"match_span={self.match_span}, "
                f"file='{self.source_text}', "
                f"line={self.offset}, "
                f"text='{self.completed_sentence}')")


class AutoCompletor:
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.reader = archive_reader.Reader(archive_path)
        self.sentences = self.reader.get_sentences()

    def search(self, substring: str) -> List[AutoCompleteData]:
        results: List[AutoCompleteData] = []
        for sentence in self.sentences:
            if substring.lower() in sentence.content.lower():
                if is_perfect_match(substring, sentence.content):
                    # Give maximum possible score for perfect match
                    score = len(substring) * 2  # max base score, no penalties
                else:
                    # Normal scoring for substring matches
                    # Use the first occurrence for scoring
                    start = sentence.content.lower().index(substring.lower())
                    end = start + len(substring)
                    score = 0
                    continue
                results.append(AutoCompleteData(
                    completed_sentence=sentence.content,
                    source_text=sentence.source_path,
                    offset=sentence.offset,
                    score=score,
                    matched_substring=substring,
                    match_span=(start, end) if 'start' in locals() else None
                ))
        return results



    def get_best_k_completions(self, prefix: str) -> List[AutoCompleteData]:
        # TODO: sort and return the best 5
        pass



def is_perfect_match(query: str, sentence: str) -> bool:
        """
        Checks if query is a prefix of any word in sentence.
        Case-insensitive, ignores punctuation.
        """
        # Use regex to match words and compare lowercase
        words = re.findall(r"\b\w+", sentence.lower())
        return any(word.startswith(query.lower()) for word in words)

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