from typing import Dict, List

from scripts.cat.cats import Cat
from scripts.cat.enums.SatisfactionModifier import SatisfactionModifier
from scripts.clan_resources.freshkill import MAL_PERCENTAGE, STARV_PERCENTAGE
from scripts.game_structure.game_essentials import game


class CatSatisfaction:
    war = False
    CLAN_SIZE_TARGET = 50

    def __init__(
        self,
        cat_id,
    ):
        self.cat_id = cat_id
        self._recent_events: Dict[int, Dict[SatisfactionModifier, List]] = {
            0: {
                SatisfactionModifier.POLITICAL: [],
                SatisfactionModifier.HUNGER: [],
                SatisfactionModifier.SOCIAL: [],
                SatisfactionModifier.CLANSIZE: [],
            },
            1: {
                SatisfactionModifier.POLITICAL: [],
                SatisfactionModifier.HUNGER: [],
                SatisfactionModifier.SOCIAL: [],
                SatisfactionModifier.CLANSIZE: [],
            },
            2: {
                SatisfactionModifier.POLITICAL: [],
                SatisfactionModifier.HUNGER: [],
                SatisfactionModifier.SOCIAL: [],
                SatisfactionModifier.CLANSIZE: [],
            },
            3: {
                SatisfactionModifier.POLITICAL: [],
                SatisfactionModifier.HUNGER: [],
                SatisfactionModifier.SOCIAL: [],
                SatisfactionModifier.CLANSIZE: [],
            },
        }
        self._modifier_pointer = (
            game.clan.age
        )  # This is used to track when it was last used

    def __str__(self):
        return f"\nPOLITICAL: {self.political}\nHUNGER: {self.hunger}\nSOCIAL: None\nCLANSIZE: {self.clan_size}"

    def __eq__(self, other):
        return self.overall == other

    @property
    def political(self):
        """
        A cat's opinion on the leadership of the Clan
        :return: a value representing the cat's opinion on the leadership
        """
        personality = Cat.fetch_cat(self.cat_id).personality
        lead_personality = game.clan.leader.personality
        dep_personality = game.clan.deputy.personality

        old_score = personality.similarity_score(
            lead_personality
        ) + personality.similarity_score(dep_personality)
        score = old_score

        # consider the cat's personality rq if they're leader or deputy
        if self.cat_id in [game.clan.leader.ID, game.clan.deputy.ID]:
            # alter score bcs of self-perception - by at most ~20%

            # increase it for high aggress
            aggress = (personality.aggression - 8) / 50
            if aggress > 0:
                score = (old_score * aggress) + score

            # decrease it for low social
            social = (personality.sociability - 8) / 50
            if social < 0:
                score = score - (old_score * social)

        # Add modifiers for recent events
        score += self.get_modifiers_for_category(SatisfactionModifier.POLITICAL)

        # return score constrained to 0-100
        if score < 0:
            return 0
        if score > 100:
            return 100
        return score

    @property
    def hunger(self):
        hunger_old = 100
        hunger = hunger_old
        if (
            game.clan.game_mode not in ["expanded", "cruel season"]
            or self.cat_id not in game.clan.freshkill_pile.nutrition_info
        ):
            return hunger

        if (
            game.clan.freshkill_pile.nutrition_info[self.cat_id].percentage
            < STARV_PERCENTAGE
        ):
            # kitty starving, v sad
            hunger -= 50
        elif (
            game.clan.freshkill_pile.nutrition_info[self.cat_id].percentage
            < MAL_PERCENTAGE
        ):
            # kitty malnourished, a bit sad
            hunger -= 25

        # if cats are hungy, decrease a bit more (2 points per 10 percent starving, 1 point per 10% malnourished)
        hunger -= game.clan.freshkill_pile.starv_percent / 10
        hunger -= game.clan.freshkill_pile.mal_percent / 10

        # now we add buffs & nerfs for traits
        p = Cat.fetch_cat(self.cat_id).personality

        # the higher the stability, the less the cat is affected by hunger
        stability = (p.stability - 8) / 100
        if stability > 0:
            hunger = (hunger_old * stability) + hunger

        # Add modifiers for recent events
        hunger += self.get_modifiers_for_category(SatisfactionModifier.HUNGER)

        # constrain to 1-100 for legibility
        if hunger < 0:
            hunger = 0
        if hunger > 100:
            hunger = 100

        return hunger

    @property
    def clan_size(self):
        st_dev = 5
        z_score = (self.CLAN_SIZE_TARGET - len(game.clan.clan_cats)) / st_dev
        clan = 50 - z_score * st_dev

        # add recent events
        clan += self.get_modifiers_for_category(SatisfactionModifier.CLANSIZE)

        return clan

    @property
    def overall(self) -> float:
        """
        Returns the cat's overall satisfaction, bounded between 0-100
        :return: Happiness float between 0-100
        """
        # TODO: draw the rest of the horse :)
        return -1

    # --------------------
    # SHORT-TERM MODIFIERS
    # --------------------

    @property
    def modifier_pointer(self):
        if self._modifier_pointer == game.clan.age:
            return self._modifier_pointer % 4

        age = game.clan.age
        if (age - self._modifier_pointer) >= 3:
            # it's been 3+ moons since we last looked at this cat's satisfaction, just clear the entire list
            for i in self._recent_events.keys():
                for x in self._recent_events[i]:
                    self._recent_events[i][x] = []
            self._modifier_pointer = age
        else:
            for i in range(0, age - self._modifier_pointer):
                self._modifier_pointer += 1
                for x in self._recent_events[i]:
                    self._recent_events[i][x] = []

        return self._modifier_pointer % 4

        # update the local

    def offset_pointer(self, amount: int) -> int:
        # convert a negative to the appropriate offset
        while amount < 0:
            amount = amount + 4
        return round((self.modifier_pointer + amount) % 4)

    def add_modifier(self, category: SatisfactionModifier, value, *, backdate_by=0):
        self._recent_events[self.offset_pointer(-backdate_by)][category].append(value)

    def get_modifiers_for_category(self, modifier: SatisfactionModifier):
        """
        Returns the modifier for the most recent 3 moons of satisfaction events for that modifier
        :param modifier: Which SatisfactionModifier we care about
        :return: The value for that modifier
        """
        modifier = modifier.value
        # this moon
        out = max(
            [0.0, sum(self._recent_events[self.modifier_pointer][modifier])],
            key=lambda x: abs(x[0]),
        )
        # 1 moon ago
        out += max(
            [0.0, sum(self._recent_events[self.offset_pointer(-1)][modifier]) / 2],
            key=lambda x: abs(x),
        )
        # 2 moons ago
        out += max(
            [0.0, sum(self._recent_events[self.offset_pointer(-2)][modifier]) / 3],
            key=lambda x: abs(x),
        )
        # 3 moons ago
        out += max(
            [0.0, sum(self._recent_events[self.offset_pointer(-3)][modifier]) / 4],
            key=lambda x: abs(x),
        )
        return out
