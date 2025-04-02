import json
import re


class BoolSearch:
    """
    Класс для выполнения поиска по инвертированному индексу с использованием логических операций.

    :param file: Путь к файлу инвертированного индекса (по умолчанию "inverted_index.json").
    """

    def __init__(self, file="inverted_index.json"):
        """
        Инициализация класса для постройки инвертированного индекса.

        :param file: Путь к файлу инвертированного индекса (по умолчанию "inverted_index.json").
        """
        self.inverted_index = self.get_data(file)
        self.pages = set(page_id for docs in self.inverted_index.values() for page_id in docs)

    def get_data(self, filename):
        """
        Загрузка инвертированного индекса из файла.

        :param filename: Путь к файлу с инвертированным индексом.
        :return: Инвертированный индекс в виде словаря.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def search(self, query):
        """
        Выполнение поиска по запросу.

        :param query: Строка запроса.
        :return: Список идентификаторов документов, соответствующих запросу.
        """
        words = self._split_request(query)
        postfix = self._to_postfix(words)
        return self._get_result_searching(postfix)

    def _split_request(self, query):
        """
        Разделение запроса на отдельные элементы.

        :param query: Строка запроса.
        :return: Список элементов запроса.
        """
        return re.findall(r'\(|\)|NOT|AND|OR|\w+', query.upper())

    def _to_postfix(self, elements):
        """
        Преобразование инфиксной записи логического выражения в постфиксную.
        Используется Shunting Yard

        :param elements: Список элементов запроса.
        :return: Список элементов в постфиксной записи.
        """
        words, operators = [], []  # Списки для хранения конечного вывода
        priority_operators = ['OR', 'AND', 'NOT']  # Приоритет операторов

        for elem in elements:
            if elem == '(':
                operators.append(elem)
            elif elem == ')':
                # Пока не встретим открывающую скобку, выталкиваем операторы из стека в вывод
                while operators[-1] != '(':
                    words.append(operators.pop())
                operators.pop()  # Убираем из стека саму открывающую скобку
            elif elem in priority_operators:
                # Пока стек не пуст и верхний элемент в стеке имеет больший или равный приоритет
                while operators and operators[-1] != '(' and priority_operators.index(
                        operators[-1]) >= priority_operators.index(
                    elem):
                    words.append(
                        operators.pop())  # Перемещаем операторы с более высоким или равным приоритетом в вывод
                operators.append(elem)  # Добавляем текущий оператор в стек
            else:
                words.append(elem.lower())

        # После обработки всех элементов перемещаем оставшиеся операторы из стека в вывод
        while operators:
            words.append(operators.pop())

        return words

    def _get_result_searching(self, postfix):
        """
        Оценка постфиксного логического выражения.

        :param postfix: Список токенов в постфиксной записи.
        :return: Список идентификаторов документов, соответствующих запросу.
        """
        stack = []

        for elem in postfix:
            if elem == 'NOT':
                operand = stack.pop()
                stack.append(self.pages - operand)
            if elem == 'AND':
                right, left = stack.pop(), stack.pop()
                stack.append(left & right)
            elif elem == 'OR':
                right, left = stack.pop(), stack.pop()
                stack.append(left | right)
            else:
                stack.append(set(self.inverted_index.get(elem, [])))

        return sorted(stack.pop()) if stack else []


if __name__ == "__main__":
    """
    Основная функция для выполнения поиска.

    Запрашивает у пользователя строку запроса и выводит результаты поиска.
    """
    searcher = BoolSearch("inverted_index.json")
    query = input("Запрос: ")
    pages = searcher.search(query)
    print(f"Результат поиска:")
    print(pages)
