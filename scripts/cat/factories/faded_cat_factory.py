import ujson

from scripts.cat.cats import Cat
from scripts.cat.enums import CatGroup
from scripts.cat.factories.base_factory import BaseCatFactory
from scripts.cat.factories.typed_dicts import InheritanceDict, GenderDict
from scripts.cat.names import Name
from scripts.cat.status import Status
from scripts.game_structure.game import switch_get_value, Switch
from scripts.housekeeping.datadir import get_save_dir


# be aware that there are many, many warnings in this file.
# this will continue to be the case until someone makes faded cats separate from regular cats.


class FadedCatFactory(BaseCatFactory):
    @classmethod
    def create_cat(cls, **kwargs) -> Cat:
        return cls._build_cat(**kwargs)

    @classmethod
    def _build_cat(cls, **kwargs) -> Cat:
        # just preventing any attempts to load something that isn't a cat ID
        cat = kwargs["ID"]

        if not cat.isdigit():
            raise ValueError(f"Faded cat ID {cat} is not numerical!")

        try:
            clan = switch_get_value(Switch.clan_save_id)

            with open(
                get_save_dir() + "/" + clan + "/faded_cats/" + cat + ".json",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
                # If loading cats is attempted before the Clan is loaded, we would need to use this.
        except AttributeError:
            # NOPE, cats are always loaded before the Clan, so doesn't make sense to throw an error
            with open(
                get_save_dir()
                + "/"
                + switch_get_value(Switch.clan_list)[0]
                + "/faded_cats/"
                + cat
                + ".json",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_info = ujson.loads(read_file.read())
        except:
            print("ERROR: in loading faded cat")
            raise

        if isinstance(cat_info["status"], str):
            status = Status(rank=cat_info["status"])
            # they are definitely dead
            status.send_to_afterlife(
                CatGroup.DARK_FOREST_ID
                if cat_info.get("df", False)
                else CatGroup.STARCLAN_ID
            )
        else:
            status = Status(**cat_info["status"])

        if isinstance(cat_info["status"], str):
            status = Status(rank=cat_info["status"])
            # they are definitely dead
            status.send_to_afterlife(
                CatGroup.DARK_FOREST_ID
                if cat_info.get("df", False)
                else CatGroup.UNKNOWN_RESIDENCE
                if status.is_outsider and not status.is_former_clancat
                else CatGroup.STARCLAN_ID
            )
        else:
            status = Status(**cat_info["status"])

        cat = Cat(
            ID=kwargs["ID"],
            gender_dict=GenderDict(sex=None, genderalign=None),
            pelt=None,
            moons=cat_info["moons"],
            status=status,
            backstory="",
            skills=None,
            personality=None,
            mentorship={},
            inheritance=InheritanceDict(
                parent1=cat_info["parent1"],
                parent2=cat_info["parent2"],
                adoptive_parents=cat_info["adoptive_parents"],
                mate=[],
                previous_mates=[],
                faded_offspring=cat_info["faded_offspring"],
            ),
            affinity={},
            toggles={},
            experience=0,
            birth_cooldown=0,
            specsuffix_hidden=False,
            faded=True,
        )
        cat.name = Name(
            prefix=cat_info["name_prefix"], suffix=cat_info["name_suffix"], cat=cat
        )
        cat.dead_for = cat_info.get("dead_for", 0)

        cat.set_faded()
        return cat
