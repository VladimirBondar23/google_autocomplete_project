"""
Module that reads text files from archive

TODOS:
 * Create a class Sentence that represent a sentence in the archive
 * Each sentence has the following:
 *  - content
 *  - source path
 *  - offset (which line in the file)
"""
import os

all_sentences = []


# Trie Node Class
class TrieNode:
    def __init__(self):
        # A dictionary to hold child nodes, mapping a character to a TrieNode instance.
        self.children = {}
        # A flag to mark the end of a valid word or sentence.
        self.is_end_of_word = False
        # A list to store the full sentences that end at this node.
        self.sentences = []


# Trie class
class Trie:
    def __init__(self):
        self.root = TrieNode()

    # Inserts a sentence into the Trie.
    def insert(self, sentence):
        node = self.root
        # Iterate through each character of the sentence.
        for char in sentence:
            # If the character is not already a child, create a new TrieNode.
            if char not in node.children:
                node.children[char] = TrieNode()
            # Move to the child node.
            node = node.children[char]

        # Mark the end of the sentence.
        node.is_end_of_word = True
        node.sentences.append(sentence)

    def collect_all_sentences(self, node, results):
        if node.is_end_of_word:
            # Add all sentences stored at this node.
            results.extend(node.sentences)

        # Recursively call for all child nodes.
        for char in node.children:
            self._collect_all_sentences(node.children[char], results)

    def print_trie_structure(self):
        print("\n--- Trie Structure ---")
        self._print_trie_node(self.root, "", 0)
        print("----------------------\n")

    # A recursive helper method to print nodes.
    def _print_trie_node(self, node, prefix, level):
        # Print the current node's information with indentation.
        indent = "  " * level
        node_info = f"{indent}-->'{prefix}' (end of word: {node.is_end_of_word})"
        if node.sentences:
            node_info += f" -> Sentences: {node.sentences}"
        print(node_info)

        # Recursively call this function for each child node.
        for char, child_node in sorted(node.children.items()):
            new_prefix = prefix + char
            self._print_trie_node(child_node, new_prefix, level + 1)


def read_sentences_from_files(directory):
    sentences = []
    # Use os.walk to traverse the directory tree.
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            # Check for text files.
            if filename.endswith(".txt"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Clean up the sentence before adding it.
                        clean_line = line.strip()
                        if clean_line:
                            sentences.append(clean_line)
    return sentences


def start_reading(directory):
    print(f"Reading sentences from files in '{directory}'...")
    all_sentences = read_sentences_from_files(directory)

    # Initialize the Trie and insert all sentences for prefix searching.
    data_structure = Trie()
    for sentence in all_sentences:
        data_structure.insert(sentence)

    return data_structure


if __name__ == "__main__":
    archive_path = 'mockArchive'
    start_reading(archive_path)
