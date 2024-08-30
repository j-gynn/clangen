import itertools
import os
from typing import List, Dict

import ujson

from scripts.game_structure.game_essentials import game
from scripts.housekeeping.datadir import get_save_dir


class FamilyTerm:
    def __init__(self, term: str, category: str, has_intermediary: bool):
        self.term = term
        self.category = category
        self.has_intermediary = has_intermediary

    def __str__(self):
        return self.term

    def __repr__(self):
        return f"FamilyTerm('{self.term}', category={self.category}" + (
            f", has_intermediary={self.has_intermediary})"
            if self.has_intermediary
            else ")"
        )

    def to_dict(self):
        return {
            "term": self.term,
            "category": self.category,
            "has_intermediary": self.has_intermediary,
        }


class FamilyTerms:
    bad_import = (
        False  # used so we don't save over a failed import & wipe a clan's custom terms
    )
    _dict: Dict[int, FamilyTerm] = {
        0: FamilyTerm("0.0.1", "version", False),
        1: FamilyTerm("grandparent", "grandparent", False),
        2: FamilyTerm("parent", "parent", False),
        3: FamilyTerm("{parent}'s sibling", "parents_sibling", True),
        4: FamilyTerm("sibling", "sibling", False),
        5: FamilyTerm("cousin", "cousin", False),
        6: FamilyTerm("kit", "kit", False),
        7: FamilyTerm("{sibling}'s kit", "siblings_kit", True),
        8: FamilyTerm("grandkit", "grandkit", False),
        9: FamilyTerm("grandmother", "grandparent", False),
        10: FamilyTerm("mother", "parent", False),
        11: FamilyTerm("aunt", "parents_sibling", False),
        12: FamilyTerm("sister", "sibling", False),
        13: FamilyTerm("niece", "siblings_kit", False),
        14: FamilyTerm("grandfather", "grandparent", False),
        15: FamilyTerm("father", "parent", False),
        16: FamilyTerm("uncle", "parents_sibling", False),
        17: FamilyTerm("brother", "sibling", False),
        18: FamilyTerm("nephew", "siblings_kit", False),
        19: FamilyTerm("mate", "mate", False),
        20: FamilyTerm("{sibling}'s mate", "siblings_mate", True),
        21: FamilyTerm("{kit}'s mate", "kits_mate", True),
        22: FamilyTerm("cat", "self", False),
        23: FamilyTerm("she-cat", "self", False),
        24: FamilyTerm("tom", "self", False),
    }
    _iter = itertools.count(start=len(_dict))
    _templates: Dict[int, Dict[str, str | List[int]]] = {
        0: {
            "name": "default (neutral)",
            "grandparent": [0],
            "parent": [1],
            "parents_sibling": [2],
            "mate": [18],
            "sibling": [4],
            "siblings_mate": [20],
            "cousin": [5],
            "kit": [6],
            "kits_mate": [21],
            "siblings_kit": [7],
            "grandkit": [8],
        },
        1: {
            "name": "default (feminine)",
            "grandparent": [9],
            "parent": [10],
            "parents_sibling": [11],
            "mate": [19],
            "sibling": [12],
            "siblings_mate": [20],
            "cousin": [5],
            "kit": [6],
            "kits_mate": [21],
            "siblings_kit": [13],
            "grandkit": [8],
        },
        2: {
            "name": "default (masculine)",
            "self": [22],
            "grandparent": [14],
            "parent": [15],
            "parents_sibling": [16],
            "mate": [19],
            "sibling": [17],
            "siblings_mate": [20],
            "cousin": [5],
            "kit": [6],
            "kits_mate": [21],
            "siblings_kit": [18],
            "grandkit": [8],
        },
    }

    @classmethod
    def get_term(
        cls, indexes: List[int], can_have_intermediary: bool = False
    ) -> List[str]:
        """
        Returns the terms from the dictionary that correspond to the indexes.
        :param indexes: A list of indexes for the dictionary.
        :param can_have_intermediary:
        :return:
        """
        try:
            if can_have_intermediary:
                val = [cls._dict[item].term for item in indexes]
            else:
                val = [
                    cls._dict[item].term
                    for item in indexes
                    if not cls._dict[item].has_intermediary
                ]
            if len(val) > 0:
                return val
        except KeyError:
            return ["error5_index_not_found"]
        return ["error4_no_familial_match"]

    @classmethod
    def get_familial_term_by_group(cls, group) -> Dict[int, FamilyTerm]:
        return {key: term for key, term in cls._dict.items() if term.category == group}

    @classmethod
    def get_template(cls, index):
        return cls._templates[index]

    @classmethod
    def get_templates(cls) -> Dict[int, Dict[str, str | List[int]]]:
        """
        Return all templates that can be loaded in
        :return: all possible templates for cat familial terms
        """
        return cls._templates

    @classmethod
    def load_familial(cls) -> None:
        """
        TODO: DOCS
        """
        if not game.clan.name:
            return

        try:
            file_path = get_save_dir() + f"/{game.clan.name}/familial_terms.json"

            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as rel_file:
                    json_string = ujson.dumps(
                        {
                            key: familyterm.to_dict()
                            for key, familyterm in cls._dict.items()
                        },
                        indent=4,
                    )
                    rel_file.write(json_string)
                return

            with open(
                file_path, "r", encoding="utf-8"
            ) as read_file:  # pylint: disable=redefined-outer-name
                dump = ujson.load(read_file)

                familyterms = {
                    item["index"]: FamilyTerm(
                        item["term"], item["category"], item["has_intermediary"]
                    )
                    for item in dump
                }

                if familyterms[0].term != cls._dict[0].term:
                    # version numbers are not synced, must run migration
                    familyterms = cls.migrate_old(familyterms)
        except:
            cls.bad_import = True
            return

        cls._dict = familyterms

    @classmethod
    def save_familial(cls, save_dict: Dict[int, FamilyTerm] = None) -> None:
        """
        Save the familial terms dictionary to file.
        :param save_dict: Use to override the default save. Useful for migration! Default None
        """
        if not game.clan.name or cls.bad_import:
            # if no clan name can be found or the import went wonky
            return

        if save_dict is None:
            save_dict = cls._dict

        game.safe_save(
            f"{get_save_dir()}/{game.clan.name}/familial_terms.json",
            ujson.dumps(
                {key: familyterm.to_dict() for key, familyterm in save_dict.items()},
                indent=4,
            ),
        )

    @classmethod
    def migrate_old(cls, old_list: Dict[int, FamilyTerm]) -> Dict[int, FamilyTerm]:
        """
        Call to migrate an old version of the familial terms JSON to the latest version
        :param old_list: The old version of the familial terms JSON
        :return: The new version
        """
        version = old_list[0].term

        if version == "0.0.1":
            # make any changes needed between this and the next version, then move on
            version = "0.0.1"

        # if version == "0.0.2":
        # etc, etc.
        cls.save_familial(old_list)
        return old_list


familyterms = FamilyTerms()


def rebuild_familial_terms():
    global familyterms
    familyterms = FamilyTerms()
