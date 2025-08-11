"""
Module that reads text files from archive
"""
import os
import time

class Sentence:
    def __init__(self, content: str, source_path: str, offset: int):
        self.content = content
        self.source_path = source_path
        self.offset = offset
        self.score = 0

    def __repr__(self):
        return f"Sentence(content={self.content!r}, file={self.source_path!r}, line={self.offset})"


class Reader:
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.sentences = []
        self.read_sentences_with_metadata()

    def read_sentences_with_metadata(self):
        # TODO: read only on first run, write to json file and read from it later
        self.sentences = []
        # Collect tuples of (sentence, source_file_path, line_number)
        for dirpath, _, filenames in os.walk(self.archive_path):
            for filename in filenames:
                if filename.endswith(".txt"):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, start=1):
                            clean_line = line.strip()
                            if clean_line:
                                self.sentences.append(Sentence(clean_line, filepath, i))
        return self.sentences

    def get_sentences(self):
        return self.sentences


if __name__ == "__main__":
    reader = Reader("Archive")
    start = time.time()
    reader.read_sentences_with_metadata()
    print(f"Load sentences in {time.time() - start:.2f} seconds.")

    substring = input("Enter substring: ")
    start = time.time()
    results = reader.search(substring)
    print(f"found {len(results)} results in {time.time() - start:.2f} seconds.")
    for sentence in results[:10]:
        print(sentence)