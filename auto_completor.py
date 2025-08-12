"""
Module that search the best completion in the data structure for a specific input
"""
from typing import List, Tuple
import archive_reader
import string
import re
import os


class AutoCompleteData:
    """Container for a single autocomplete candidate.

           Args:
               completed_sentence: Full sentence to present as the completion.
               source_text: Path to the source file the sentence came from.
               offset: Byte/char offset of the sentence within the source.
               score: Ranking score for this candidate (higher is better).
               matched_substring: The original user query (normalized string used for matching).
               match_span: (start, end) indices in `completed_sentence` of the matched region.
           """
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
        """Return a compact, human-readable representation for debugging."""
        source_name = os.path.basename(self.source_text)
        return f'{self.completed_sentence} ({source_name} {self.offset})'


class AutoCompletor:
    def __init__(self, archive_path):
        """Initialize the autocomplete engine with an archive.

                Args:
                    archive_path: Path to an archive that `archive_reader.Reader` can open.
                """
        self.archive_path = archive_path
        self.reader = archive_reader.Reader(archive_path)
        self.sentences = self.reader.get_sentences()

    def search(self, substring: str) -> List[AutoCompleteData]:
        """Find exact and fuzzy matches for a query across all sentences.

               The search proceeds in two phases:
                 1) Exact phrase/word match (case-insensitive, punctuation/spacing tolerant).
                 2) If fewer than 5 results were found, run a fuzzy search allowing a single
                    edit (insertion, deletion, or substitution) guided by a regex built by
                    `build_regex()`, then score candidates with `calc_score()`.

               Duplicates are avoided with a set keyed by full sentence text.

               Args:
                   substring: User input to match against sentences.

               Returns:
                   A list of `AutoCompleteData` objects (unsorted).
               """
        substring = re.sub(r"\s+", " ", substring).strip()
        substring = re.sub(r",", "", substring).strip()
        results: List[AutoCompleteData] = []
        set_of_seen = set()
        q_lower = substring.lower()
        for sentence in self.sentences:
            text = sentence.content
            tl = text.lower()

            if q_lower in tl:
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
                    set_of_seen.add(text)
                    continue

        if not results or len(results) < 5:
            fuzzy_rx = self.build_regex(substring)
            fuzzy_candidates = self.search_sentences(substring)

            for s in fuzzy_candidates:
                m = fuzzy_rx.search(s.content)
                if not m:
                    continue
                start, end = m.span()
                matched_text = s.content[start:end]
                if s.content in set_of_seen:
                    continue
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
        """Construct a regex that matches one-edit-away variants of `query`.

                The union covers:
                    - Insertion: any single extra character at any position.
                    - Substitution: any single character replaced.
                    - Deletion: any single character removed.
                    - Exact match: the query itself.

                Word boundaries (\\b) are used so the match aligns to whole tokens.

                Args:
                    query: The string to build a one-edit regex for.

                Returns:
                    A compiled, case-insensitive `re.Pattern`.
                """
        q = query
        parts = []

        for i in range(len(q) + 1):
            left = re.escape(q[:i])
            right = re.escape(q[i:])
            parts.append(f"{left}.{right}")

        for i in range(len(q)):
            left = re.escape(q[:i])
            right = re.escape(q[i + 1:])
            parts.append(f"{left}.{right}")

        for i in range(len(q)):
            left = re.escape(q[:i])
            right = re.escape(q[i + 1:])
            parts.append(f"{left}{right}")

        parts.append(re.escape(q))

        union = "|".join(parts)
        return re.compile(rf"\b(?:{union})\b", re.IGNORECASE)

    def search_sentences(self, query):
        """Return sentence records that match the fuzzy regex for `query`.

                Args:
                    query: The input string to search for.

                Returns:
                    A list of sentence objects from `self.sentences` whose `content`
                    matches the pattern produced by `build_regex(query)`.
                """
        regex = self.build_regex(query)
        return [s for s in self.sentences if regex.search(s.content)]

    def get_text(self, r):
        """Normalize a result object to lowercase text for sorting.

                Accepts either:
                  - a sentence record with `.content`, or
                  - an `AutoCompleteData` with `.completed_sentence`.

                Args:
                    r: Result-like object.

                Returns:
                    Lowercase string suitable as a secondary sort key; empty string if missing.
                """
        if hasattr(r, 'content'):
            return r.content.lower()
        elif hasattr(r, 'completed_sentence'):
            return r.completed_sentence.lower()
        else:
            return ""

    def get_best_k_completions(self, prefix: str) -> List[AutoCompleteData]:
        """Get up to 5 best completions for `prefix`, sorted by score then text.

                Sorting:
                    1) Primary: descending `score`
                    2) Secondary: alphabetical order of normalized text

                Args:
                    prefix: User's current input.

                Returns:
                    Top five `AutoCompleteData` items after sorting.
                """
        hits = self.search(prefix)
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
    pattern = r"\b" + r"\W+".join(map(re.escape, tokens)) + r"\b"
    return re.search(pattern, sentence.lower()) is not None


def calc_score(query: str, match_text: str) -> int:
    """
        Spec-accurate scoring with exactly one edit allowed:
          - Base = 2 * number of matching characters (spaces count, punctuation ignored)
          - If lengths equal -> ONE substitution (apply incorrect-letter penalty at that index)
          - If lengths differ by 1 -> ONE insertion/deletion (apply missing/added penalty at skip index)
          - Never stack penalties

        Normalization steps:
          - Lowercase both strings
          - Remove punctuation
          - Collapse multiple spaces to a single space

        Args:
            query: Original user query string.
            match_text: The substring from a sentence that matched fuzzily.

        Returns:
            Integer score (>= 0). Returns 0 if more than one edit would be required.
        """
    table = str.maketrans('', '', string.punctuation)

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.lower().translate(table)).strip()

    q = norm(query)
    m = norm(match_text)

    if abs(len(q) - len(m)) > 1:
        return 0

    if q == m:
        return 2 * len(q)

    if len(q) == len(m):
        diffs = [i for i, (a, b) in enumerate(zip(q, m)) if a != b]
        if len(diffs) != 1:
            return 0
        i = diffs[0]
        base = 2 * (len(m))
        pen = incorrect_letter_penalty(i)
        return base - pen

    if len(q) > len(m):
        l, s = q, m
    else:
        l, s = m, q

    k = None
    i = j = 0
    while i < len(l) and j < len(s):
        if l[i] == s[j]:
            i += 1
            j += 1
        else:
            if k is not None:
                return 0
            k = i
            i += 1
    if k is None:
        k = len(l) - 1

    base = 2 * len(m)
    pen = missing_or_added_penalty(k)
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
