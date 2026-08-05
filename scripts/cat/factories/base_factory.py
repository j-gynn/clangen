from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


from scripts.cat.cats import Cat
from scripts.cat.registry_module.store import CatStore


class BaseCatFactory(ABC):
    def __init__(self, store: CatStore):
        self._cat_store = store

    def create_cat(self, **kwargs) -> Cat:
        cat = self._build_cat(**kwargs)
        self._cat_store.add(cat)
        return cat

    @abstractmethod
    def _build_cat(self, **kwargs) -> Cat:
        pass
