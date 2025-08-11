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

        if not results:
            fuzzy_rx = self.build_regex(substring)
            fuzzy_candidates = self.search_sentences(substring)  # list of Sentence

            for s in fuzzy_candidates:
                m = fuzzy_rx.search(s.content)
                if not m:
                    continue
                start, end = m.span()  # end is exclusive; don't +1
                matched_text = s.content[start:end]
                score = calc_score(substring, matched_text)

                results.append(AutoCompleteData(
                    completed_sentence=s.content,
                    source_text=s.source_path,
                    offset=s.offset,
                    score=score,
                    matched_substring=substring,
                    match_span=(start, end),
                ))

        return results

    def build_regex(self, query):
        q = query
        parts = []

        # addition in TEXT (user missed one char) – prefer these first
        for i in range(len(q) + 1):
            left = re.escape(q[:i])
            right = re.escape(q[i:])
            parts.append(f"{left}.{right}")  # e.g., .nam, n.am, na.m, nam.

        # substitution (same length)
        for i in range(len(q)):
            left = re.escape(q[:i])
            right = re.escape(q[i + 1:])
            parts.append(f"{left}.{right}")  # e.g., n.m

        # deletion in TEXT (text shorter by 1)
        for i in range(len(q)):
            left = re.escape(q[:i])
            right = re.escape(q[i + 1:])
            parts.append(f"{left}{right}")  # e.g., nm

        # exact last
        parts.append(re.escape(q))

        union = "|".join(parts)
        return re.compile(rf"\b(?:{union})\b", re.IGNORECASE)

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
    Spec-accurate scoring with exactly one edit allowed:
      - Base = 2 * number of matching characters (spaces count, punctuation ignored)
      - If lengths equal -> ONE substitution (apply incorrect-letter penalty at that index)
      - If lengths differ by 1 -> ONE insertion/deletion (apply missing/added penalty at skip index)
      - Never stack penalties
    """


    # Normalize: lowercase, drop punctuation, collapse spaces
    table = str.maketrans('', '', string.punctuation)
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.lower().translate(table)).strip()

    q = norm(query)
    m = norm(match_text)

    # More than one edit away
    if abs(len(q) - len(m)) > 1:
        return 0

    # Exact
    if q == m:
        return 2 * len(q)

    # Same length -> single substitution
    if len(q) == len(m):
        diffs = [i for i, (a, b) in enumerate(zip(q, m)) if a != b]
        if len(diffs) != 1:
            return 0
        i = diffs[0]
        base = 2 * (len(m) )             # all but the wrong char match
        pen  = incorrect_letter_penalty(i)
        return base - pen

    # Length differs by 1 -> single insertion/deletion
    # Let L be the longer, S the shorter (skip one char in L to match S)
    if len(q) > len(m):
        L, S = q, m            # user typed extra char (delete from query)
    else:
        L, S = m, q            # text has extra char (insert in text)

    k = None
    i = j = 0
    while i < len(L) and j < len(S):
        if L[i] == S[j]:
            i += 1; j += 1
        else:
            if k is not None:
                return 0       # would need >1 edit
            k = i              # skip L[i]
            i += 1
    if k is None:
        # extra char is the last one in L
        k = len(L) - 1

    base = 2 * len(m)                  # all chars of the shorter string match
    pen  = missing_or_added_penalty(k) # position of the skipped char in L
    return base - pen



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
