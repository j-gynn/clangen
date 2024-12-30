from typing import Union, Type


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
        """
        return len(
            [
                cat
                for cat in self.all_cats_list
                if not (cat.dead or cat.exiled or cat.outside)
            ]
        )

    def get_alive_status_cats(
        self,
        get_status: list,
        working: bool = False,
        sort: bool = False,
    ) -> list:
        """
            returns a list of cat objects for all living cats of get_status in Clan
        st of statuses searching for
            :param get_status:
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
