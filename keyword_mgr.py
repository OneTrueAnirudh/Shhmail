import os

class KeywordManager:
    def __init__(self, filepath="keywords.txt"):
        self.filepath = filepath
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                pass  # Create the file if it doesn't exist

    def load_keywords(self):
        with open(self.filepath, "r") as f:
            return [line.strip() for line in f.readlines()]

    def save_keywords(self, keywords):
        with open(self.filepath, "w") as f:
            f.write("\n".join(keywords))

    def add_keyword(self, keyword):
        keywords = self.load_keywords()
        if keyword not in keywords:
            keywords.append(keyword)
            self.save_keywords(keywords)

    def remove_keyword(self, keyword):
        keywords = self.load_keywords()
        if keyword in keywords:
            keywords.remove(keyword)
            self.save_keywords(keywords)
