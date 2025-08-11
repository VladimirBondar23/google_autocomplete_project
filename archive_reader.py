"""
This module is responsible for loading the auto-completor archive data
"""
import os
import json
import time
from typing import List

DEFAULT_CACHE_FILE = "sentences_cache.json"


class Sentence:
    """
    A class to represent a single archive sentence
    """
    def __init__(self, content: str, source_path: str, offset: int, score=0):
        self.content = content
        self.source_path = source_path
        self.offset = offset
        self.score = score

    def to_dict(self):
        return {
            "content": self.content,
            "source_path": self.source_path,
            "offset": self.offset,
            "score": self.score
        }

    def __repr__(self):
        source_name = os.path.basename(self.source_path)
        return f'{self.content} ({source_name} {self.offset})'


class Reader:
    """
    A class to read the auto-completor archive data
    """
    def __init__(self, archive_path, cache_filepath=DEFAULT_CACHE_FILE):
        self.archive_path = archive_path
        self.cache_filepath = cache_filepath
        self.sentences = []
        self.read_sentences_with_metadata()

    def read_sentences_with_metadata(self) -> List[Sentence]:
        """
        Read the auto-completor archive data and store it in a python list.
        If data is already written in cache json file, reading straight from it.
        Otherwise, read the raw data from the archive directory.
        :return: A list of Sentence objects containing the whole archive data
        """
        if os.path.exists(self.cache_filepath):
            # read data from cache json file
            with open(self.cache_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sentences = [Sentence(**item) for item in data]
        else:
            # read data from archive directory
            self.sentences = []
            for dirpath, _, filenames in os.walk(self.archive_path):
                for filename in filenames:
                    if filename.endswith(".txt"):
                        filepath = os.path.join(dirpath, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for i, line in enumerate(f, start=1):
                                clean_line = line.strip()
                                if clean_line:
                                    self.sentences.append(Sentence(clean_line, filepath, i))
            # save data to cache json file
            with open(self.cache_filepath, 'w', encoding='utf-8') as f:
                json.dump([s.to_dict() for s in self.sentences], f, ensure_ascii=False, indent=2)
        return self.sentences

    def get_sentences(self) -> List[Sentence]:
        """
        Getter method for the sentence list
        :return: A list of Sentence objects.
        """
        return self.sentences


if __name__ == "__main__":
    # simple data loading example with time measurement
    start = time.time()
    reader = Reader("Archive")
    print(f"Load sentences in {time.time() - start:.2f} seconds.")
    for sentence in reader.sentences[:10]:
        print(sentence)
