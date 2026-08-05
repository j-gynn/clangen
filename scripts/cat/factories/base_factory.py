from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


from scripts.cat.cats import Cat
from scripts.cat.registry_module.store import CatStore, cat_store


class BaseCatFactory(ABC):
    def create_cat(self, **kwargs) -> Cat:
        cat = self._build_cat(**kwargs)
        cat_store.add(cat)
        return cat

    @abstractmethod
    def _build_cat(self, **kwargs) -> Cat:
        pass
