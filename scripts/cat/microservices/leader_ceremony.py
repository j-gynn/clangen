from random import choice, sample, randint
from typing import Optional, Dict

import i18n

from scripts.cat.enums import CatGroup, CatRank
from scripts.cat.registry_module.store import cat_store
from scripts.config import get_config
from scripts.events_module.text_adjust import leader_ceremony_text_adjust
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource

LEAD_CEREMONY_SC: Optional[Dict] = None
LEAD_CEREMONY_DF: Optional[Dict] = None
lead_ceremony_lang = None


def load_leader_ceremonies():
    global LEAD_CEREMONY_SC, LEAD_CEREMONY_DF, lead_ceremony_lang
    if lead_ceremony_lang == i18n.config.get("locale"):
        return
    LEAD_CEREMONY_SC = load_lang_resource("events/lead_ceremony_sc.json")
    LEAD_CEREMONY_DF = load_lang_resource("events/lead_ceremony_df.json")
    lead_ceremony_lang = i18n.config.get("locale")


load_leader_ceremonies()


def generate_lead_ceremony(cat):
    """Create a leader ceremony and add it to the history"""

    load_leader_ceremonies()

    # determine which dict we're pulling from
    if game.clan.instructor.status.group == CatGroup.DARK_FOREST:
        starclan = False
        ceremony_dict: Dict = LEAD_CEREMONY_DF
    else:
        starclan = True
        ceremony_dict: Dict = LEAD_CEREMONY_SC

    # ---------------------------------------------------------------------------- #
    #                                    INTRO                                     #
    # ---------------------------------------------------------------------------- #
    all_intros = ceremony_dict["intros"]

    # filter the intros
    possible_intros = []
    for intro in all_intros:
        tags = all_intros[intro]["tags"]

        if game.clan.age != 0 and "new_clan" in tags:
            continue
        elif game.clan.age == 0 and "new_clan" not in tags:
            continue

        if (
            all_intros[intro]["lead_trait"]
            and cat.personality.trait not in all_intros[intro]["lead_trait"]
        ):
            continue
        possible_intros.append(all_intros[intro])

    if chosen_intro := choice(possible_intros):
        intro = choice(chosen_intro["text"])
        intro = leader_ceremony_text_adjust(intro, cat)
    else:
        intro = "this should not appear"

    # ---------------------------------------------------------------------------- #
    #                                 LIFE GIVING                                  #
    # ---------------------------------------------------------------------------- #
    life_givers = []
    dead_relations = []
    life_giving_leader = None
    num_of_lives_to_give = get_config("death_related.max_leader_lives")

    # grab life givers that the cat actually knew in life and sort by amount of relationship!
    relationships = cat.relationships.values()

    for rel in relationships:
        kitty = cat_store.get(rel.cat_to)
        if kitty and kitty.dead and kitty.status.rank != CatRank.NEWBORN:
            # check where they reside
            if starclan:
                if kitty.status.group != CatGroup.STARCLAN:
                    continue
            else:
                if kitty.status.group != CatGroup.DARK_FOREST:
                    continue
            # guides aren't allowed here
            if kitty == game.clan.instructor:
                continue
            else:
                dead_relations.append(rel)

    # sort relations by the strength of their relationship
    dead_relations.sort(
        key=lambda rel: rel.romance + rel.like + rel.respect + rel.comfort + rel.trust,
        reverse=True,
    )

    # if we have relations, then make sure we only take the top 8
    if dead_relations:
        for i, rel in enumerate(dead_relations):
            if i <= num_of_lives_to_give - 1:
                break
            if rel.cat_to.status.is_leader:
                life_giving_leader = rel.cat_to
                continue
            life_givers.append(rel.cat_to.ID)

    cats_in_afterlife = (
        cat_store.query()
        .in_group(CatGroup.PLAYER_CLAN)
        .in_group(CatGroup.STARCLAN if starclan else CatGroup.DARK_FOREST)
        .filter(lambda c: c.ID not in life_givers)
    )

    # check amount of life givers, if we need more, then grab from the other dead cats
    if len(life_givers) < num_of_lives_to_give - 1:
        extra_amount_needed = (num_of_lives_to_give - 1) - len(life_givers)

        possible_dead_cats = cats_in_afterlife.with_not_rank(
            CatRank.LEADER, CatRank.NEWBORN
        ).all()
        # this part just checks how many cats are available, if there aren't enough to fill all the slots,
        # then we just take however many are available

        if len(possible_dead_cats) - 1 < extra_amount_needed:
            extra_givers = possible_dead_cats
        else:
            extra_givers = sample(possible_dead_cats, k=extra_amount_needed)

        life_givers.extend(extra_givers)

    # making sure we have a leader at the end
    ancient_leader = False
    leaders = cats_in_afterlife.with_rank(CatRank.LEADER).all()
    if not life_giving_leader and leaders:
        # choosing if the life giving leader will be the oldest leader or previous leader
        coin_flip = randint(1, 2)
        if coin_flip == 1:
            # pick the oldest leader
            leaders.sort(key=lambda x: -1 * int(x.dead_for))
            ancient_leader = True
            life_giving_leader = leaders[0]
        else:
            # pick previous leader
            leaders.sort(key=lambda x: int(x.dead_for))
            life_giving_leader = leaders[0]

    if life_giving_leader:
        life_givers.append(life_giving_leader)

    # check amount again, if more are needed then we'll add the ghost-y cats at the end
    unknown_blessing = len(life_givers) < num_of_lives_to_give

    extra_lives = num_of_lives_to_give - len(life_givers)
    possible_lives = ceremony_dict["lives"]
    lives = []
    used_lives = []
    used_virtues = []
    for giver_cat in cat_store.query().by_id(*life_givers):
        if not giver_cat:
            continue
        life_list = []
        for life in possible_lives:
            tags = possible_lives[life]["tags"]
            rank = giver_cat.status.rank

            if "unknown_blessing" in tags:
                continue

            if "guide" in tags and giver_cat != game.clan.instructor:
                continue
            if game.clan.age != 0 and "new_clan" in tags:
                continue
            elif game.clan.age == 0 and "new_clan" not in tags:
                continue
            if "old_leader" in tags and not ancient_leader:
                continue
            if "leader_parent" in tags and giver_cat.ID not in cat.get_parents():
                continue
            elif "leader_child" in tags and giver_cat.ID not in cat.get_children():
                continue
            elif "leader_sibling" in tags and giver_cat.ID not in cat.get_siblings():
                continue
            elif "leader_mate" in tags and giver_cat.ID not in cat.mate:
                continue
            elif (
                "leader_former_mate" in tags and giver_cat.ID not in cat.previous_mates
            ):
                continue
            if "leader_mentor" in tags and giver_cat.ID not in cat.former_mentor:
                continue
            if (
                "leader_apprentice" in tags
                and giver_cat.ID not in cat.former_apprentices
            ):
                continue
            if (
                possible_lives[life]["rank"]
                and rank not in possible_lives[life]["rank"]
            ):
                continue
            if (
                possible_lives[life]["lead_trait"]
                and cat.personality.trait not in possible_lives[life]["lead_trait"]
            ):
                continue
            if possible_lives[life]["star_trait"] and (
                giver_cat.personality.trait not in possible_lives[life]["star_trait"]
            ):
                continue
            life_list.extend(list(possible_lives[life]["life_giving"]))

        i = 0
        chosen_life = {}
        while i < 10:
            attempted = []
            if life_list:
                chosen_life = choice(life_list)
                if chosen_life not in used_lives and chosen_life not in attempted:
                    break
                attempted.append(chosen_life)
                i += 1
            else:
                print(
                    f"WARNING: life list had no items for giver #{giver_cat.ID}. Using default life. "
                    f"If you are a beta tester, please report and ping scribble along with "
                    f"all the info you can about the giver cat mentioned in this warning."
                )
                chosen_life = ceremony_dict["default_life"]
                break

        used_lives.append(chosen_life)
        if "virtue" in chosen_life:
            poss_virtues = [
                i for i in chosen_life["virtue"] if i not in used_virtues
            ] or ["faith", "friendship", "love", "strength"]
            virtue = choice(poss_virtues)
            used_virtues.append(virtue)
        else:
            virtue = None

        lives.append(
            leader_ceremony_text_adjust(
                chosen_life["text"], leader=cat, life_giver=giver_cat.ID, virtue=virtue
            )
        )
    if unknown_blessing:
        possible_blessing = []
        for life in possible_lives:
            tags = possible_lives[life]["tags"]

            if "unknown_blessing" not in tags:
                continue

            if (
                possible_lives[life]["lead_trait"]
                and cat.personality.trait not in possible_lives[life]["lead_trait"]
            ):
                continue
            possible_blessing.append(possible_lives[life])
        chosen_blessing = choice(possible_blessing)
        chosen_text = choice(chosen_blessing["life_giving"])
        lives.append(
            leader_ceremony_text_adjust(
                chosen_text["text"],
                leader=cat,
                virtue=chosen_text["virtue"],
                extra_lives=extra_lives,
            )
        )
    all_lives = "<br><br>".join(lives)

    # ---------------------------------------------------------------------------- #
    #                                    OUTRO                                     #
    # ---------------------------------------------------------------------------- #

    # get the outro
    all_outros = ceremony_dict["outros"]

    possible_outros = []
    for outro in all_outros:
        tags = all_outros[outro]["tags"]

        if game.clan.age != 0 and "new_clan" in tags:
            continue
        elif game.clan.age == 0 and "new_clan" not in tags:
            continue

        if (
            all_outros[outro]["lead_trait"]
            and cat.personality.trait not in all_outros[outro]["lead_trait"]
        ):
            continue
        possible_outros.append(all_outros[outro])

    chosen_outro = choice(possible_outros)

    if chosen_outro:
        if life_givers:
            giver = life_givers[-1]
        else:
            giver = None
        outro = choice(chosen_outro["text"])
        outro = leader_ceremony_text_adjust(outro, leader=cat, life_giver=giver)
    else:
        outro = "this should not appear"

    full_ceremony = "<br><br>".join([intro, all_lives, outro])
    cat.history.lead_ceremony = full_ceremony
