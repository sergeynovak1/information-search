# Загрузка индекса (doc_id -> url)
def load_index(index_path: str) -> dict[int, str]:
    index = {}
    with open(index_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                doc_id, url = parts
                index[int(doc_id)] = url
    return index

