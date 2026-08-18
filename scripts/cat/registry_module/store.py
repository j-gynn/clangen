from collections import defaultdict
from typing import TYPE_CHECKING, Dict, DefaultDict, Generator

from scripts.cat.enums import CatGroup
from scripts.cat.registry_module._query import CatQuery
from scripts.game_structure.events.custom_event import CAT_GROUP_CHANGE

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


class CatStore:
    def __init__(self):
        self._cats: Dict[str, "Cat"] = {}
        self._groups: DefaultDict[CatGroup, list[str]] = defaultdict(list)

    def process_event(self, event):
        if event.type != CAT_GROUP_CHANGE:
            return False

        self._groups[event.data["old_group"]].remove(event.data["cat_id"])
        self._groups[event.data["new_group"]].append(event.data["cat_id"])
        return True

    def add(self, cat: "Cat"):
        self._cats[cat.ID] = cat
        self._groups[cat.status.group].append(cat.ID)

    def remove(self, cat_id: str):
        self._cats.pop(cat_id)
        self._groups[self._cats[cat_id].status.group].remove(cat_id)

    def get(self, cat_id) -> "Cat":
        try:
            return self._cats[cat_id]
        except KeyError:
            from scripts.cat.factories.faded_cat_factory import FadedCatFactory

            return FadedCatFactory.create_cat(ID=cat_id)

    def clear(self):
        self._cats.clear()
        self._groups.clear()

    def query_ids(self, *ids) -> CatQuery:
        return CatQuery(lambda: iter(self.get(cat_id) for cat_id in ids))

    def query_cats(self) -> CatQuery:
        return CatQuery(lambda: iter(self._cats.values()))

    def query_group(self, group: CatGroup = None) -> CatQuery:
        return CatQuery(lambda: iter(self._cats[c] for c in self._groups[group]))


cat_store: CatStore = CatStore()
