from scripts.cat.cats import Cat
from scripts.clan_resources.freshkill import MAL_PERCENTAGE, STARV_PERCENTAGE
from scripts.game_structure.game_essentials import game


class Satisfaction:
    war = False
    CLAN_SIZE_TARGET = 50

    def __init__(
        self,
        cat_id,
    ):
        self.cat_id = cat_id

    @property
    def political(self):
        personality = Cat.fetch_cat(self.cat_id).personality
        lead_personality = Cat.fetch_cat(game.clan.leader).personality
        dep_personality = Cat.fetch_cat(game.clan.deputy).personality

        return personality.similarity_score(
            lead_personality
        ) + personality.similarity_score(dep_personality)

    @property
    def hunger(self):
        hunger = 100
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

        if hunger < 0:
            hunger = 0
        return hunger

    @property
    def clan_size(self):
        st_dev = 5
        z_score = (self.CLAN_SIZE_TARGET - len(game.clan.clan_cats)) / st_dev
        return 50 - z_score * st_dev
