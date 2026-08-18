import unittest
import types

from scripts.cat.enums import CatGroup, CatAge, CatSocial, CatRank
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.registry_module.store import cat_store
from scripts.game_structure.discord_rpc import status_dict
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value


class TestCatStore(unittest.TestCase):
    def tearDown(self):
        cat_store.clear()

    def test_add_cat(self):
        cat = TestCatFactory.create_cat()
        self.assertIn(cat, cat_store.query_cats().all())

    def test_cat_filter(self):
        newborn = TestCatFactory.create_cat()
        senior = TestCatFactory.create_cat()
        self.assertIn(
            newborn,
            cat_store.query_cats().alive_in_player_clan().with_age(CatAge.NEWBORN),
        )
        self.assertNotIn(
            senior,
            cat_store.query_cats().alive_in_player_clan().with_age(CatAge.SENIOR),
        )

    def test_load_faded_cat(self):
        switch_set_value(Switch.clan_save_id, "Ember")
        self.assertRaises(ValueError, cat_store.get, "heehee")
        cat_store.get("7")

    def test_get_by_group(self):
        cat = TestCatFactory.create_cat(
            status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID}
        )
        cat2 = TestCatFactory.create_cat(
            status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID}
        )
        dead = TestCatFactory.create_cat(
            status_dict={"rank": CatRank.WARRIOR, "group_ID": CatGroup.STARCLAN_ID}
        )

        self.assertEqual([cat, cat2], cat_store.query_group(CatGroup.PLAYER_CLAN))
        self.assertEqual([dead], cat_store.query_group(CatGroup.STARCLAN))

    def test_iter_by_group(self):
        cat = TestCatFactory.create_cat(
            status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID}
        )
        cat2 = TestCatFactory.create_cat(
            status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID}
        )
        dead = TestCatFactory.create_cat(
            status_dict={"rank": CatRank.WARRIOR, "group_ID": CatGroup.STARCLAN_ID}
        )

        playerclan_iter = cat_store.query_group(CatGroup.PLAYER_CLAN)
        self.assertIsInstance(playerclan_iter, types.GeneratorType)
        self.assertEqual(cat, next(playerclan_iter))
        self.assertEqual(cat2, next(playerclan_iter))
        self.assertRaises(StopIteration, next, playerclan_iter)

    def test_group_size(self):
        TestCatFactory.create_cat(status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID})
        TestCatFactory.create_cat(status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID})
        TestCatFactory.create_cat(
            status_dict={"rank": CatRank.WARRIOR, "group_ID": CatGroup.STARCLAN_ID}
        )
        self.assertEqual(2, cat_store.query_group(CatGroup.PLAYER_CLAN).amount())
        self.assertEqual(1, cat_store.query_group(CatGroup.STARCLAN).amount())

    def test_query_functionality(self):
        TestCatFactory.create_cat(status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID})
        TestCatFactory.create_cat(status_dict={"group_ID": CatGroup.PLAYER_CLAN_ID})
        TestCatFactory.create_cat(status_dict={"group_ID": CatGroup.STARCLAN_ID})

        cat_store.query_cats().by_ids("1", "23", "45", "74").all()
