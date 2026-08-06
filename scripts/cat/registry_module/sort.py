from dataclasses import dataclass
from typing import Callable

from scripts.cat.enums import CatRank


@dataclass(frozen=True)
class SortKey:
    key: Callable
    reverse: bool = False

    def __call__(self, cat):
        return self.key(cat)


class CatSort:
    AGE = SortKey(lambda cat: cat.moons)
    AGE_REVERSE = SortKey(lambda cat: cat.moons, reverse=True)

    ID = SortKey(lambda cat: cat.ID)
    ID_REVERSE = SortKey(lambda cat: cat.ID, reverse=True)

    NAME = SortKey(lambda cat: cat.name.prefix.lower())
    NAME_REVERSE = SortKey(lambda cat: cat.name.prefix.lower(), reverse=True)

    RANK = SortKey(
        lambda cat: (
            cat.status.rank.order,
            cat.get_adjusted_age(cat),
        ),
        reverse=True,
    )

    EXP = SortKey(lambda cat: cat.experience, reverse=True)

    DEATH = SortKey(lambda cat: -1 * int(cat.dead_for))
