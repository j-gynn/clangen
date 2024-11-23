import unittest

from scripts.cat.satisfaction import CatSatisfaction

from scripts.cat.cats import Cat
from scripts.cat.enums.SatisfactionModifier import SatisfactionModifier
from scripts.clan import Clan
from scripts.game_structure.game_essentials import game


class TestSatisfactionModifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        game.clan = Clan()

        cls.cat1 = Cat()

    def setUp(self):
        game.clan.age = 0
        game.clan.satisfaction[self.cat1.ID] = CatSatisfaction(self.cat1.ID)

    def test_add_modifier(self):
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 5)
        self.assertEqual(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 5
        )
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 5)

    def test_add_multiple_modifier(self):
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 5)
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 5)
        self.assertEqual(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 10
        )

    def test_add_multiple_moons(self):
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 5)
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 10, backdate_by=1)
        self.assertEqual(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 10
        )

    def test_modifier_skip(self):
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 100)

        self.assertEqual(
            satisfaction._recent_events[0][SatisfactionModifier.SOCIAL], [100]
        )
        game.clan.age = 1
        # we have moved forward one moon, check pointer moved
        self.assertEqual(satisfaction.modifier_pointer, game.clan.age % 3)

        # check that the value has decreased through decay
        self.assertLess(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 100
        )

    def test_modifier_manyskips(self):
        game.clan.age = 0
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 100)

        game.clan.age = 5
        self.assertEqual(satisfaction.modifier_pointer, 1)
        # assert that it's now equal to a newly-initialised CatSatisfaction (i.e. empty)
        self.assertEqual(
            satisfaction._recent_events, CatSatisfaction(None)._recent_events
        )

    def test_overwrite_moons(self):
        game.clan.age = 4
        satisfaction = game.clan.satisfaction[self.cat1.ID]
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 15)
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 15, backdate_by=1)
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 15, backdate_by=2)
        satisfaction.add_modifier(SatisfactionModifier.SOCIAL, 15, backdate_by=3)
        self.assertEqual(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 31.25
        )
        game.clan.age = 5
        self.assertLessEqual(
            satisfaction.get_modifiers_for_category(SatisfactionModifier.SOCIAL), 31.25
        )
