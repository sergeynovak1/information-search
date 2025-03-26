import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class WebCrawler:
    def __init__(self, start_url, output_dir="pages", index_file="index.txt", max_urls=100):
        self.start_url = start_url
        self.output_dir = output_dir
        self.index_file = index_file
        self.max_urls = max_urls
        self.domain = urlparse(self.start_url).netloc
        self.visited_urls = set()
        self.counter = 1

        os.makedirs(self.output_dir, exist_ok=True)

    def _save_url_data(self, url, content):
        # инициализируем название и место для файла
        file_name = f"{self.counter}_page.html"
        file_path = os.path.join(self.output_dir, file_name)
        print(self.counter, file_name)

        # сохраняем html страницы
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        # записываем ссылку в index.txt
        with open(self.index_file, "a", encoding="utf-8") as index:
            index.write(f"{self.counter} {url}\n")

        # увеличиваем счетчик обработанных ссылок
        self.counter += 1

    def _get_links(self, url, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        # получаем домен ссылки
        links = set()
        # проходимся по всем тегам со ссылками
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href)

            # проверка, что ссылка ведет на тот же сайт
            if urlparse(full_url).netloc == self.domain and f"{self.domain}/news" in full_url:
                links.add(full_url)

        return links

    def _crawl(self, url):
        # если обработано нужное кол-во страниц или если эту страницу уже обрабатывали - пропускаем
        if len(self.visited_urls) >= self.max_urls or url in self.visited_urls:
            return

        try:
            response = requests.get(url)
            response.raise_for_status()
            # получаем инфомацию страницы
            self._save_url_data(url, response.text)
            # сохраняем ссылку как посещенную
            self.visited_urls.add(url)

            # рекурсиво вызываем метод _crawl для всех полученных со страницы ссылок
            for link in self._get_links(url, response.text):
                if link not in self.visited_urls:
                    self._crawl(link)

        except Exception:
            pass

    def start(self):
        # парсинг первой страницы
        self._crawl(self.start_url)


if __name__ == "__main__":
    # указываем стартовую ссылку для сбора ссылок
    crawler = WebCrawler("https://www.autonews.ru/news/67e29d239a79475f543ea9dd", max_urls=100)
    crawler.start()
