"""
Module that search the best completion in the data structure for a specific input
"""
import archive_reader


class AutoCompletor:
    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.reader = archive_reader.Reader(archive_path)
        self.sentences = self.reader.get_sentences()

    def search(self, substring):
        results = []
        # TODO: add 2 more searches: 1 - single char missing, 2 - single char added
        for sentence in self.sentences:
            if substring in sentence.content:
                results.append(sentence)
        return results
