import os
from typing import List

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
    # do not alter the order of this unless you want weird things to happen
    # also do not directly import
    _familyterms: List[FamilyTerm] = [
        FamilyTerm("0.0.0", "version", False),
        FamilyTerm("grandparent", "grandparent", False),
        FamilyTerm("parent", "parent", False),
        FamilyTerm("{parent}'s sibling", "parents_sibling", True),
        FamilyTerm("sibling", "sibling", False),
        FamilyTerm("cousin", "cousin", False),
        FamilyTerm("kit", "kit", False),
        FamilyTerm("{sibling}'s kit", "siblings_kit", True),
        FamilyTerm("grandkit", "grandkit", False),
        FamilyTerm("grandmother", "grandparent", False),
        FamilyTerm("mother", "parent", False),
        FamilyTerm("aunt", "parents_sibling", False),
        FamilyTerm("sister", "sibling", False),
        FamilyTerm("niece", "siblings_kit", False),
        FamilyTerm("grandfather", "grandparent", False),
        FamilyTerm("father", "parent", False),
        FamilyTerm("uncle", "parents_sibling", False),
        FamilyTerm("brother", "sibling", False),
        FamilyTerm("nephew", "siblings_kit", False),
        FamilyTerm("mate", "mate", False),
        FamilyTerm("{sibling}'s mate", "siblings_mate", True),
        FamilyTerm("{kit}'s mate", "kits_mate", True),
        FamilyTerm("cat", "self", False),
        FamilyTerm("she-cat", "self", False),
        FamilyTerm("tom", "self", False),
    ]

    @classmethod
    def get_term(cls, indexes: List[int], can_have_intermediary: bool = False):
        try:
            if can_have_intermediary:
                val = [cls._familyterms[item].term for item in indexes]
            else:
                val = [
                    cls._familyterms[item].term
                    for item in indexes
                    if not cls._familyterms[item].has_intermediary
                ]
            if len(val) > 0:
                return val
        except IndexError:
            return ["error5_index_out_of_range"]
        return ["error4_no_familial_match"]

    @classmethod
    def get_familial_term_by_group(cls, group):
        return [term for term in cls._familyterms if term.category == group]

    @classmethod
    def load_familial(cls):
        """
        TODO: DOCS
        """
        if not game.clan.name:
            return

        file_path = get_save_dir() + f"/{game.clan.name}/familial_terms.json"

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as rel_file:
                json_string = ujson.dumps(
                    [familyterm.to_dict() for familyterm in cls._familyterms], indent=4
                )
                rel_file.write(json_string)
            return

        with open(
            file_path, "r", encoding="utf-8"
        ) as read_file:  # pylint: disable=redefined-outer-name
            dump = ujson.load(read_file)
            cls._familyterms = [
                FamilyTerm(item["term"], item["category"], item["has_intermediary"])
                for item in dump
            ]

    @classmethod
    def save_familial(cls):
        """
        TODO: DOCS
        """
        if not game.clan.name:
            return

        file_path = get_save_dir() + f"/{game.clan.name}/familial_terms.json"

        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as rel_file:
                json_string = ujson.dumps(
                    [familyterm.to_dict() for familyterm in cls._familyterms], indent=4
                )
                rel_file.write(json_string)
            return

        game.safe_save(
            f"{get_save_dir()}/{game.clan.name}/familial_terms.json",
            ujson.dumps(
                [familyterm.to_dict() for familyterm in cls._familyterms], indent=4
            ),
        )


familyterms = FamilyTerms()
