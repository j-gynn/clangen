from typing import TYPE_CHECKING, Dict, List

from scripts.cat.enums import CatGroup, CatRank, CatAge

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


class CatQuery:
    def __init__(self, source):
        self._source = source

    def __iter__(self):
        return iter(self._source())

    def all(self):
        return list(self)

    def filter(self, predicate):
        return CatQuery(lambda: (cat for cat in self if predicate(cat)))

    # common combinations

    def alive_in_player_clan(self):
        return self.filter(lambda cat: cat.status.alive_in_player_clan)

    # granular

    def alive(self):
        return self.filter(lambda cat: not cat.status.group.is_afterlife())

    def dead(self):
        return self.filter(lambda cat: cat.status.group.is_afterlife())

    def in_group(self, *groups: CatGroup):
        return self.filter(
            lambda cat: cat.status.group in groups
            or cat.status.get_last_living_group() in groups
        )

    def in_player_clan(self):
        return self.filter(
            lambda cat: cat.status.group == CatGroup.PLAYER_CLAN
            or cat.status.get_last_living_group() == CatGroup.PLAYER_CLAN
        )

    def outsiders(self):
        return self.filter(lambda cat: cat.status.is_outsider)

    def with_rank(self, *ranks: CatRank):
        return self.filter(lambda cat: cat.status.rank in ranks)

    def with_age(self, *ages: CatAge):
        return self.filter(lambda cat: cat.age in ages)

    def near_group_id(self, *groups):
        if not groups:
            groups = {CatGroup.PLAYER_CLAN_ID}
        return self.filter(
            lambda cat: all(cat.status.is_near(group) for group in groups)
        )

    def exiled_from_group_id(self, *groups):
        if not groups:
            groups = {CatGroup.PLAYER_CLAN_ID}
        return self.filter(
            lambda cat: all(cat.status.is_exiled(group) for group in groups)
        )

    def not_exiled_from_group_id(self, *groups):
        if not groups:
            groups = {CatGroup.PLAYER_CLAN_ID}
        return self.filter(
            lambda cat: not any(cat.status.is_exiled(group) for group in groups)
        )

    # NICHE

    def can_work(self):
        return self.filter(lambda cat: not cat.not_working())

    def cannot_work(self):
        return self.filter(lambda cat: cat.not_working())
