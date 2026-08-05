from typing import TYPE_CHECKING, Dict, List

from scripts.cat.enums import CatGroup, CatRank, CatAge

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


class CatQuery:
    def __init__(self, cats):
        self._cats = cats

    def all(self):
        return list(self._cats)

    def alive(self):
        return CatQuery(
            cat for cat in self._cats if not cat.status.group.is_afterlife()
        )

    def in_group(self, group: CatGroup):
        return CatQuery(
            cat
            for cat in self._cats
            if cat.status.group == group or cat.status.get_last_living_group() == group
        )

    def in_player_clan(self):
        return CatQuery(
            cat
            for cat in self._cats
            if cat.status.group == CatGroup.PLAYER_CLAN
            or cat.status.get_last_living_group() == CatGroup.PLAYER_CLAN
        )

    def with_rank(self, rank: CatRank):
        return CatQuery(cat for cat in self._cats if cat.status.rank == rank)

    def with_age(self, age: CatAge):
        return CatQuery(cat for cat in self._cats if cat.age == age)
