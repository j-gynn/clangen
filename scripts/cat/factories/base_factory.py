from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


from scripts.cat.cats import Cat
from scripts.cat.registry_module.store import CatStore, cat_store


class BaseCatFactory(ABC):
    @classmethod
    def create_cat(cls, **kwargs) -> Cat:
        cat = cls._build_cat(**kwargs)
        cat_store.add(cat)
        return cat

    @classmethod
    @abstractmethod
    def _build_cat(cls, **kwargs) -> Cat:
        pass
