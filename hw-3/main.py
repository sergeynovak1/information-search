import os
import json
from collections import defaultdict
from typing import Dict, List


class InvertedIndexBuilder:
    """Класс для построения инвертированного индекса из файлов с токенами."""

    def __init__(self, directory_path: str):
        """
        Инициализация класса для постройки инвертированного индекса.

        :param directory_path: Путь к директории с файлами токенов.
        """
        self.directory_path = directory_path
        self.inverted_index: Dict[str, List[int]] = defaultdict(list)

    def _process_file(self, file_path: str, page_id: int):
        """
        Обрабатывает файл, извлекая токены и привязывая их к page_id.

        :param file_path: Путь к файлу с токенами.
        :param page_id: Идентификатор документа.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().split(":")[0]  # Извлекаем нормализованное слово (до ":")
                if word:
                    self.inverted_index[word].append(page_id)

    def build(self) -> Dict[str, List[int]]:
        """
        Строит инвертированный индекс из всех файлов в указанной директории.

        :return: Инвертированный индекс в виде словаря {слово: [page_id, ...]}.
        :raises FileNotFoundError: Если указанной директории не существует.
        """
        if not os.path.exists(self.directory_path):
            raise FileNotFoundError("Указанная директория не существует")

        for token_file in os.listdir(self.directory_path):
            try:
                # Извлекаем page_id из имени файла, например "lemmas_1_page.txt" → 1
                page_id = int(token_file.split(".")[0].split("_")[1])
                self._process_file(os.path.join(self.directory_path, token_file), page_id)
            except (IndexError, ValueError):
                print(f"Некорректное имя файла: {token_file}. Пропущен.")

        return self.inverted_index


class InvertedIndexSaver:
    """Класс для сохранения инвертированного индекса в JSON-файл."""

    @staticmethod
    def save(inverted_index: Dict[str, List[int]], output_file: str = "inverted_index.json"):
        """
        Сохраняет инвертированный индекс в JSON-файл.

        :param inverted_index: Словарь {слово: [page_id, ...]}.
        :param output_file: Имя выходного файла.
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(inverted_index, f, ensure_ascii=False, indent=None, separators=(',', ': '))

        # Добавляем перенос строки после "],"
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace("],", "],\n")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)


if __name__ == "__main__":
    # Путь к директории с файлами токенов
    directory_path = "../hw-2/lemmas"

    # Создание инвертированного индекса
    builder = InvertedIndexBuilder(directory_path)
    inverted_index = builder.build()

    # Сохранение индекса в JSON-файл
    saver = InvertedIndexSaver()
    saver.save(inverted_index)

    print("Завершено!")
