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

    def dead(self):
        return CatQuery(
            cat for cat in self._cats if cat.status.group.is_afterlife()
        )

    def in_group(self, *groups: CatGroup):
        return CatQuery(
            cat
            for cat in self._cats
            if cat.status.group in groups or cat.status.get_last_living_group() in groups
        )

    def in_player_clan(self):
        return CatQuery(
            cat
            for cat in self._cats
            if cat.status.group == CatGroup.PLAYER_CLAN
            or cat.status.get_last_living_group() == CatGroup.PLAYER_CLAN
        )

    def with_rank(self, *ranks: CatRank):
        return CatQuery(cat for cat in self._cats if cat.status.rank in ranks)

    def with_age(self, *ages: CatAge):
        return CatQuery(cat for cat in self._cats if cat.age in ages)

    # NICHE

    def can_work(self):
        return CatQuery(cat for cat in self._cats if not cat.not_working())

    def cannot_work(self):
        return CatQuery(cat for cat in self._cats if cat.not_working())