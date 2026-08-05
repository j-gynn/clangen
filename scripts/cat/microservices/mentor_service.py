from random import choice
from typing import TYPE_CHECKING, Optional, Tuple

from scripts.cat.enums import CatRank
from scripts.cat.registry_module.store import cat_store

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


mentor_type = {
    CatRank.MEDICINE_CAT: [CatRank.MEDICINE_CAT],
    CatRank.WARRIOR: [
        CatRank.WARRIOR,
        CatRank.DEPUTY,
        CatRank.LEADER,
        CatRank.ELDER,
    ],
    CatRank.MEDIATOR: [CatRank.MEDIATOR],
}


def get_mentor(cat) -> Optional["Cat"]:
    return cat_store.get(cat.mentor) if cat.mentor else None


def add_mentorship(mentor_id, app_id):
    """
    Create a new mentorship between the mentor and app
    :param mentor_id: ID of the future mentor
    :param app_id: ID of the future apprentice
    :return: None
    """
    if mentor_id is None or app_id is None:
        return
    mentor = cat_store.get(mentor_id)
    app = cat_store.get(app_id)

    if app.mentor is not None:
        remove_mentorship(app.mentor, app_id)

    app.mentor = mentor_id
    mentor.apprentice.append(app_id)


def remove_mentorship(mentor_id, *app_ids):
    """
    Removes one or more apprentices from a mentor
    :param mentor_id: ID of the mentor to retire
    :param app_ids: ID of the apprentice to remove as args
    :return: None
    """
    if mentor_id is None:
        return
    mentor = cat_store.get(mentor_id)
    apps = list(cat_store.query().by_id(*app_ids))
    for app in apps:
        if app.ID in mentor.apprentice:
            mentor.apprentice.remove(app.ID)
        if app.moons > 6:
            if app.ID not in mentor.former_apprentices:
                mentor.former_apprentices.append(app.ID)
            if mentor.ID not in app.former_mentor:
                app.former_mentor.append(mentor.ID)
        app.mentor = None


def update_mentorship(*apps: "Cat"):
    if not apps or not apps[0]:
        return
    for app in apps:
        if (
            not app.status.rank.is_any_apprentice_rank()
            or app.status.is_outsider
            or app.dead
        ):
            remove_mentorship(app.mentor, app.ID)
            return

        if app.mentor and not is_valid_mentor_for_app(cat_store.get(app.mentor), app):
            remove_mentorship(app.mentor, app.ID)

        if not app.mentor:
            add_mentorship(choose_random_mentor(app), app.ID)


def is_valid_mentor_for_app(mentor, app):
    return (
        app.status.is_any_apprentice_rank()
        and app.status.group_ID == mentor.status.group_ID
        and mentor.status.rank in mentor_type[app.status.rank.get_adult_version()]
    )


def choose_random_mentor(app):
    potential_mentors = (
        cat_store.query()
        .alive()
        .in_group(app.status.group)
        .with_rank(*mentor_type[app.status.rank.get_adult_version()])
    )
    priority_mentors = potential_mentors.filter(lambda cat: not cat.apprentice).filter(
        lambda cat: not cat.not_working()
    )

    if priority_mentors or potential_mentors:
        return choice(priority_mentors if priority_mentors else potential_mentors).ID
    return None


def get_dead_former_mentor(cat):
    """
    Gets the cat's most recent dead mentor. Returns the ID of the first dead mentor found, or None
    :param cat: Cat object whose former mentor we are finding
    :return:
    """
    return cat_store.query().by_id(reversed(cat.former_mentor)).dead().first()


def determine_mentor_tag_for_ceremony(
    cat: "Cat", rank: CatRank
) -> Tuple[str, Optional["Cat"]]:
    mentor_query = cat_store.query().by_id(cat.former_mentor).alive().in_player_clan()
    if rank in mentor_type:
        mentor_query.with_rank(mentor_type[rank])

    if mentor_query.all():
        mentor = list(mentor_query)[-1]
        return f"alive_{'leader_' if mentor.status.is_leader else ''}mentor", mentor
    return "no_valid_previous_mentor", None


def get_current_apprentices(cat_id):
    cat = cat_store.get(cat_id)
    return [cat_store.get(app) for app in cat.apprentice]
