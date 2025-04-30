import os
import json
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFVectorSearch:
    def __init__(self, data_dir):
        self.data_dir = data_dir  # Путь к директории с данными TF-IDF.
        self.term_to_id = {}  # Словарь для отображения терминов в их уникальные индексы.
        self.idf_dict = {}  # Словарь для хранения IDF (inverse document frequency) каждого термина.
        self.doc_data = []  # Список, где каждый элемент — это словарь с ID документа и его вектором.

    def load_data(self):
        """Загружает данные из файлов и строит векторы."""
        # НЕ ПЕРЕОПРЕДЕЛЯЕМ self.data_dir
        filenames = [f for f in os.listdir(self.data_dir) if f.startswith("tf_idf_tokens_")]

        # Сначала собираем все термины и их IDF
        for filename in filenames:
            with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    term, idf, _ = line.strip().split()
                    if term not in self.term_to_id:
                        self.term_to_id[term] = len(self.term_to_id)
                        self.idf_dict[term] = float(idf)

        # Теперь строим векторы документов
        for filename in filenames:
            doc_id = int(filename.split(".")[0].split("_")[-1])
            doc_vector = np.zeros(len(self.term_to_id))

            with open(os.path.join(self.data_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    term, _, tfidf = line.strip().split()
                    term_idx = self.term_to_id[term]
                    doc_vector[term_idx] = float(tfidf)

            self.doc_data.append({
                "doc_id": doc_id,
                "vector": doc_vector.tolist()
            })

    def save_index(self):
        index_data = {
            "doc_data": self.doc_data,
            "term_to_id": self.term_to_id,
            "idf_dict": self.idf_dict
        }
        # Собираем все данные в один словарь для сохранения.

        with open("hw-5/index.json", 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=4)
            # Сохраняем данные в JSON-файл с отступами для удобочитаемости.

    def load_index(self, index_dir="hw-5"):
        """Загружает индексы из JSON."""
        with open(os.path.join(index_dir, "index.json"), 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            # Загружаем данные из JSON-файла.

        self.doc_data = index_data["doc_data"]
        self.term_to_id = index_data["term_to_id"]
        self.idf_dict = index_data["idf_dict"]
        # Восстанавливаем данные из JSON в атрибуты класса.

    def vectorize_query(self, query):
        """Преобразует запрос в TF-IDF вектор."""
        query_terms = query.lower().split()
        # Разбиваем запрос на термины и приводим их к нижнему регистру.
        query_vector = np.zeros(len(self.term_to_id))
        # Создаем нулевой вектор той же длины, что и количество уникальных терминов.

        term_counts = defaultdict(int)
        for term in query_terms:
            term_counts[term] += 1
            # Подсчитываем частоту каждого термина в запросе.

        max_tf = max(term_counts.values()) if term_counts else 1
        # Находим максимальную частоту термина в запросе (или используем 1, если запрос пустой).

        for term, tf in term_counts.items():
            if term in self.term_to_id:
                term_idx = self.term_to_id[term]
                normalized_tf = 0.5 + 0.5 * (tf / max_tf)  # Сглаженный TF.
                query_vector[term_idx] = normalized_tf * self.idf_dict.get(term, 0)
                # Вычисляем TF-IDF для термина и обновляем вектор запроса.

        return query_vector.reshape(1, -1)
        # Возвращаем вектор запроса в виде двумерного массива (для совместимости с cosine_similarity).

    def search(self, query, top_k=10):
        """Ищет документы и возвращает топ-k результатов."""
        query_vector = self.vectorize_query(query)
        # Преобразуем запрос в TF-IDF вектор.

        # Преобразуем списки векторов обратно в numpy array
        doc_vectors = np.array([doc["vector"] for doc in self.doc_data])

        similarities = cosine_similarity(query_vector, doc_vectors)
        # Вычисляем косинусное сходство между запросом и всеми документами.

        ranked_indices = np.argsort(similarities[0])[::-1][:top_k]
        # Сортируем индексы документов по убыванию сходства и выбираем топ-k.

        results = []
        for idx in ranked_indices:
            doc_id = self.doc_data[idx]["doc_id"]
            score = similarities[0][idx]
            if float(score):
                results.append({"doc_id": doc_id, "score": float(score)})
                # Формируем список результатов с ID документа и его оценкой сходства.

        return results


def interactive_search(searcher):
    """Интерактивный поиск с вводом запроса из консоли."""
    print("🔍 Введите поисковый запрос (или 'exit' для выхода):")
    while True:
        query = input("> ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        results = searcher.search(query, top_k=10)
        print(f"\nРезультаты для '{query}':")
        for res in results:
            print(f"  Документ {res['doc_id']} (схожесть: {res['score']:.4f})")
        print("\nВведите следующий запрос:")


if __name__ == "__main__":
    searcher = TFIDFVectorSearch(data_dir=r"hw-4/tf_idf_tokens")


    if os.path.exists("hw-5/index.json"):
        print("Загружаем индекс из JSON...")
        searcher.load_index()
    else:
        print("Строим индекс...")
        searcher.load_data()
        searcher.save_index()

    # Запускаем интерактивный поиск
    interactive_search(searcher)