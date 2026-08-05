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
        try:
            return self._cats[cat_id]
        except KeyError:
            from scripts.cat.factories.faded_cat_factory import FadedCatFactory

            return FadedCatFactory.create_cat(ID=cat_id)

    def clear(self):
        self._cats = {}

    def query(self) -> CatQuery:
        return CatQuery(lambda: iter(self._cats.values()))


cat_store: CatStore = CatStore()
