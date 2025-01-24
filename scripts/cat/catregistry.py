import logging
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)


class CatRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.all_cats = {}  # Initialize the global list
        return cls._instance

    def add_cat(self, cat):
        self.all_cats[cat.ID] = cat

    def remove_cat(self, cat_id):
        self.all_cats.pop(cat_id)

    def fetch_cat(self, cat_id):
        return self.all_cats[cat_id]

    @property
    def all_cats_list(self):
        return list(self.all_cats.values())

    @property
    def living_cats_list(self):
        """
        Gets a list of all living clan cats
        :return:
        """
        return [cat for cat in registry.all_cats_list if not (cat.dead or cat.outside)]

    @property
    def get_living_cat_count(self) -> int:
        """
        Returns the int of all living cats, both in and out of the Clan
        """
        return len([cat for cat in registry.all_cats_list if not cat.dead])

    @property
    def get_living_clan_cat_count(self) -> int:
        """
        Returns the int of all living cats within the Clan
        :return: int
        """
        return len(
            [
                cat
                for cat in self.all_cats_list
                if not (cat.dead or cat.exiled or cat.outside)
            ]
        )

    @property
    def get_alive_clan_queens(self) -> Tuple[Dict, List]:
        queen_dict = {}
        living_kits = [
            cat
            for cat in self.living_cats_list
            if not (cat.dead or cat.outside) and cat.status in ["kitten", "newborn"]
        ]
        for cat in living_kits.copy():
            parents = cat.get_parents()
            parents = [
                self.fetch_cat(i)
                for i in parents
                if self.fetch_cat(i) in self.living_cats_list
            ]
            if not parents:
                continue

            # determining which cat is the queen
            if (
                len(parents) == 1
                or len(parents) > 2
                or all(i.gender == "male" for i in parents)
                or parents[0].gender == "female"
            ):
                # cat 0 is the queen
                queen_id = parents[0].ID
            elif len(parents) == 2:
                # cat 1 is the queen
                # this should never happen I don't think?
                logger.warning("Cat with ID %s has queen as the second parent", cat.ID)
                queen_id = parents[1].ID
            else:
                logger.error("Cat with ID %s has impossible parents!", cat.ID)
                continue

            try:
                queen_dict[queen_id].append(cat)
            except KeyError:
                queen_dict[queen_id] = [cat]
            living_kits.remove(cat)

        return queen_dict, living_kits

    def get_alive_status_cats(
        self,
        get_status: list,
        working: bool = False,
        sort: bool = False,
    ) -> list:
        """
        returns a list of cat objects for all living cats of get_status in Clan
        :param get_status: list of statuses searching for
        :param bool working: default False, set to True if you would like the list to only include working cats
        :param bool sort: default False, set to True if you would like list sorted by descending moon age
        """

        alive_cats = [
            i
            for i in self.all_cats_list
            if i.status in get_status and not i.dead and not i.outside
        ]

        if working:
            alive_cats = [i for i in alive_cats if not i.not_working()]

        if sort:
            alive_cats = sorted(alive_cats, key=lambda cat: cat.moons, reverse=True)

        return alive_cats


registry: CatRegistry = CatRegistry()
