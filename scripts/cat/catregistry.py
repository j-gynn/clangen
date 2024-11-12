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


registry: CatRegistry = CatRegistry()
