import os
import re
from bs4 import BeautifulSoup
import pymorphy3
import nltk
from nltk.corpus import stopwords


class TextProcessor:
    def __init__(self, html_dir='./pages', tokens_dir='./tokens', lemmas_dir='./lemmas'):
        self.html_dir = html_dir
        self.tokens_dir = tokens_dir
        self.lemmas_dir = lemmas_dir
        self.morph = pymorphy3.MorphAnalyzer()

        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('russian'))

        os.makedirs(self.tokens_dir, exist_ok=True)
        os.makedirs(self.lemmas_dir, exist_ok=True)

    def extract_text(self, file_path):
        """Извлекает текст из HTML файла."""
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            return soup.get_text(separator=' ')

    def set_tokens(self, text):
        """Токенизирует текст, исключая стоп-слова и приводя слова к нижнему регистру."""
        tokens = re.findall(r'\b[а-яА-ЯёЁ]+\b', text.lower())
        return {token for token in tokens if token not in self.stop_words}

    def set_lemmas(self, tokens):
        """Лемматизирует токены и сохраняет все формы слов."""
        lemmas = {}
        for token in tokens:
            lemma = self.morph.parse(token)[0].normal_form
            lemmas.setdefault(lemma, set()).add(token)
        return lemmas

    def save_tokens(self, file_name, tokens):
        """Сохраняет токены в файл."""
        token_file_path = os.path.join(self.tokens_dir, f'tokens_{os.path.splitext(file_name)[0]}.txt')
        with open(token_file_path, 'w', encoding='utf-8') as token_file:
            token_file.write('\n'.join(sorted(tokens)))

    def save_lemmas(self, file_name, lemmas):
        """Сохраняет леммы и их формы в файл."""
        lemma_file_path = os.path.join(self.lemmas_dir, f'lemmas_{os.path.splitext(file_name)[0]}.txt')
        with open(lemma_file_path, 'w', encoding='utf-8') as lemma_file:
            for lemma, forms in sorted(lemmas.items()):
                lemma_file.write(f'{lemma}: {" ".join(sorted(forms))}\n')

    def process_file(self, file_name):
        """Обрабатывает HTML файл: токенизирует и лемматизирует текст."""
        file_path = os.path.join(self.html_dir, file_name)
        text = self.extract_text(file_path)
        tokens = self.set_tokens(text)
        lemmas = self.set_lemmas(tokens)

        self.save_tokens(file_name, tokens)
        self.save_lemmas(file_name, lemmas)

    def process_all_files(self):
        """Обрабатывает все HTML файлы в заданной директории."""
        html_files = [f for f in os.listdir(self.html_dir)]
        for file_name in html_files:
            self.process_file(file_name)
        print('Обработка завершена!')


if __name__ == '__main__':
    processor = TextProcessor()
    processor.process_all_files()
