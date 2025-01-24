import logging
from random import choice, random
from typing import Tuple, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

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
        return self.all_cats.get(cat_id)

    @property
    def all_cats_list(self):
        return list(self.all_cats.values())

    @all_cats_list.setter
    def all_cats_list(self, value):
        self._instance.all_cats = {cat.ID: cat for cat in value}

    @property
    def living_clan_cats_list(self):
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
            for cat in self.living_clan_cats_list
            if not (cat.dead or cat.outside) and cat.status in ["kitten", "newborn"]
        ]
        for cat in living_kits.copy():
            parents = list(cat.get_parents())
            if isinstance(parents[0], str):
                parents = [
                    self.fetch_cat(i)
                    for i in parents
                    if self.fetch_cat(i) in self.living_clan_cats_list
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

    def get_cats_same_age(self, cat: "Cat", age_range=10):
        """
        Look for all cats in the Clan and returns a list of cats which are in the same age range as the given cat.
        :param cat: the given cat
        :param int age_range: The allowed age difference between the two cats, default 10
        :returns: a list of Cat objects of all eligible cats
        """
        eligible_cats = []
        for inter_cat in self.living_clan_cats_list:
            if inter_cat.ID == cat.ID:
                continue

            if abs(inter_cat.moons - cat.moons) > age_range:
                continue

            if inter_cat.ID not in cat.relationships:
                cat.create_one_relationship(inter_cat)

            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)

            eligible_cats.append(inter_cat)

        return eligible_cats

    def get_possible_mates(self, cat: "Cat"):
        """
        Returns a list of cats which are possible mates for the input cat
        :param cat: the given cat
        :return: a list of Cat objects of all eligible cats
        """
        eligible_cats = []
        for inter_cat in self.living_clan_cats_list:
            if inter_cat.ID == cat.ID:
                continue

            if inter_cat.ID not in cat.relationships:
                cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)

            if inter_cat.is_potential_mate(cat, for_love_interest=True):
                eligible_cats.append(inter_cat)

        return eligible_cats

    def get_random_moon_cat(
        self, main_cat: "Cat", parent_child_modifier=True, mentor_app_modifier=True
    ):
        """
        returns a random cat for use in moon events
        :param main_cat: cat object of main cat in event
        :param parent_child_modifier: increase the chance of the random cat being a
        parent of the main cat. Default True
        :param mentor_app_modifier: increase the chance of the random cat being a mentor or
        app of the main cat. Default True
        """
        possible_rc = [
            cat for cat in registry.living_clan_cats_list if cat.ID != main_cat.ID
        ]

        if not possible_rc:
            return None

        random_cat = choice(possible_rc)

        if parent_child_modifier and not int(random() * 3):
            # this interaction will try to run with parent-child
            possible_parents = []
            for cat in [main_cat.parent1, main_cat.parent2]:
                if self.fetch_cat(cat) in possible_rc:
                    possible_parents.append(cat)
            for cat in main_cat.adoptive_parents:
                if self.fetch_cat(cat) in possible_rc:
                    possible_parents.append(cat)

            if possible_parents:
                random_cat = self.fetch_cat(choice(possible_parents))

        if mentor_app_modifier and (
            main_cat.status
            in ["apprentice", "mediator apprentice", "medicine cat apprentice"]
            and main_cat.mentor
            and not int(random() * 3)
        ):
            random_cat = self.fetch_cat(main_cat.mentor)
        elif mentor_app_modifier and main_cat.apprentice and not int(random() * 3):
            random_cat = self.fetch_cat(choice(main_cat.apprentice))

        return random_cat


registry: CatRegistry = CatRegistry()
