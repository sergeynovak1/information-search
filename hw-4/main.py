import os
import math
from collections import Counter


class FileManager:
    """
    Класс для работы с файловой системой:
    чтение токенов и лемм, получение списка файлов.
    """

    def read_tokens(self, path):
        """
        Читает токены из файла и приводит их к нижнему регистру.

        :param path: Путь к файлу с токенами
        :return: Список токенов
        """
        with open(path, 'r', encoding='utf-8') as file:
            return [word.strip().lower() for word in file.read().split() if word.strip()]

    def read_lemmas(self, path):
        """
        Читает леммы из файла и создает отображение форма → лемма.

        :param path: Путь к файлу с леммами
        :return: Словарь форм: лемма
        """
        form_to_lemma = {}
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(':')
                try:
                    base = parts[0].strip()
                    variations = parts[1].strip().split()
                    for form in variations:
                        form_to_lemma[form] = base
                except:
                    pass
        return form_to_lemma

    def get_files(self, directory_path):
        """
        Возвращает список файлов в каталоге, отсортированных по числовому значению в имени файла.

        :param directory_path: Путь к каталогу
        :return: Отсортированный список путей к файлам
        """
        def extract_number(file_name):
            try:
                return int(''.join(filter(str.isdigit, file_name)))
            except ValueError:
                return float('inf')

        return sorted(
            [
                os.path.join(directory_path, file_name)
                for file_name in os.listdir(directory_path)
            ],
            key=lambda file_path: extract_number(os.path.basename(file_path))
        )


class TextProcessor:
    """
    Класс для вычислений TF и IDF.
    """

    def compute_tf(self, tokens):
        """
        Вычисляет TF (term frequency) для документа.

        :param tokens: Список токенов
        :return: Словарь {терм: TF}
        """
        total_terms = len(tokens)
        frequency = Counter(tokens)
        return {term: frequency[term] / total_terms if total_terms else 0 for term in tokens}

    def compute_idf(self, vocab, document_lists):
        """
        Вычисляет IDF (inverse document frequency) для терминов в коллекции документов.

        :param vocab: Список всех терминов
        :param document_lists: Список списков токенов (документы)
        :return: Словарь {терм: IDF}
        """
        total_documents = len(document_lists)
        idf_scores = {}
        for term in vocab:
            docs_with_term = sum(1 for document in document_lists if term in document)
            idf_scores[term] = math.log((total_documents + 1) / (docs_with_term + 1)) + 1
        return idf_scores


class TFIDFProcessor:
    """
    Класс для основной обработки TF-IDF по токенам и леммам.
    """

    def __init__(self):
        """
        Инициализация путей, создание папок и компонентов.
        """
        self.tokens_dir = './hw-2/tokens'
        self.lemmas_dir = './hw-2/lemmas'
        self.output_terms_dir = './hw-4/tf_idf_tokens'
        self.output_lemmas_dir = './hw-4/tf_idf_lemmas'
        os.makedirs(self.output_terms_dir, exist_ok=True)
        os.makedirs(self.output_lemmas_dir, exist_ok=True)
        self.file_manager = FileManager()
        self.text_analyzer = TextProcessor()

    def save_tfidf(self, output_path, tf_data, idf_data):
        """
        Сохраняет TF-IDF значения в файл.

        :param output_path: Путь к выходному файлу
        :param tf_data: Словарь TF
        :param idf_data: Словарь IDF
        """
        with open(output_path, 'w', encoding='utf-8') as file:
            for term in tf_data:
                idf = idf_data.get(term, 0)
                tfidf = tf_data[term] * idf
                file.write(f"{term} {idf:.6f} {tfidf:.6f}\n")

    def process_documents(self, input_pairs, mapping_fn, output_path, prefix):
        """
        Обрабатывает список документов, вычисляя TF-IDF.

        :param input_pairs: Список пар (путь_к_токенам, путь_к_леммам или None)
        :param mapping_fn: Функция преобразования токенов (например, замена на леммы)
        :param output_path: Папка для сохранения результатов
        :param prefix: Префикс имени выходных файлов
        """
        processed_docs = []

        for token_path, lemma_path in input_pairs:
            tokens = self.file_manager.read_tokens(token_path)
            mapped_tokens = mapping_fn(tokens, lemma_path)
            processed_docs.append(mapped_tokens)

        vocabulary = sorted(set(term for doc in processed_docs for term in doc))
        idf_scores = self.text_analyzer.compute_idf(vocabulary, processed_docs)

        for index, document in enumerate(processed_docs, start=1):
            tf_scores = self.text_analyzer.compute_tf(document)
            self.save_tfidf(
                os.path.join(output_path, f"{prefix}_{index}.txt"),
                tf_scores,
                idf_scores
            )

    def process_tokens(self):
        """
        Обрабатывает токены без приведения к леммам.
        """
        token_paths = self.file_manager.get_files(self.tokens_dir)
        file_combinations = [(path, None) for path in token_paths]

        def identity_mapper(tokens, _):
            return tokens

        self.process_documents(
            file_combinations,
            mapping_fn=identity_mapper,
            output_path=self.output_terms_dir,
            prefix="tf_idf_tokens"
        )

    def process_lemmas(self):
        """
        Обрабатывает токены с приведением к леммам.
        """
        token_paths = self.file_manager.get_files(self.tokens_dir)
        lemma_paths = self.file_manager.get_files(self.lemmas_dir)
        file_combinations = list(zip(token_paths, lemma_paths))

        def lemma_mapper(tokens, lemma_file):
            lemma_dict = self.file_manager.read_lemmas(lemma_file)
            return [lemma_dict.get(token, token) for token in tokens]

        self.process_documents(
            file_combinations,
            mapping_fn=lemma_mapper,
            output_path=self.output_lemmas_dir,
            prefix="tf_idf_lemmas"
        )

    def run(self):
        """
        Запускает обработку токенов и лемм.
        """
        self.process_tokens()
        self.process_lemmas()


if __name__ == '__main__':
    processor = TFIDFProcessor()
    processor.run()