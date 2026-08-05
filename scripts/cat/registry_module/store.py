from typing import TYPE_CHECKING, Dict

from scripts.cat.registry_module._query import CatQuery

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


class CatStore:
    def __init__(self):
        self._cats: Dict[str, "Cat"] = {}

    def add(self, cat: "Cat"):
        self._cats[cat.ID] = cat

    def remove(self, cat_id: str):
        self._cats.pop(cat_id)

    def get(self, cat_id) -> "Cat":
        return self._cats[cat_id]

    def clear(self):
        self._cats = {}

    def query(self) -> CatQuery:
        return CatQuery(list(self._cats.items()))


cat_store: CatStore = CatStore()
