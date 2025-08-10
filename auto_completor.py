"""
Module that search the best completion in the data structure for a specific input
"""
from typing import List
from archive_reader import start_reading

data_structure = None


class AutoCompleteData:
    pass


def get_best_completions(prefix: str) -> List[AutoCompleteData]:
    pass


def search(prefix):
    node = data_structure.root
    # Traverse the Trie to the node corresponding to the end of the prefix.
    for char in prefix:
        if char not in node.children:
            return []  # No sentences found with this prefix.
        node = node.children[char]

    # Once at the prefix's end node, collect all sentences from there.
    results = []
    data_structure.collect_all_sentences(node, results)
    return results


def search_substring(substring):
    # This approach is less performant for prefixes than a Trie but is simple and works for any substring.
    results = []
    # The 'in' operator in Python checks for a substring.
    for sentence in all_sentences:
        if substring.lower() in sentence.lower():
            results.append(sentence)
    return results


def init(data_struct):
    global data_structure
    data_structure = data_struct
    pass
