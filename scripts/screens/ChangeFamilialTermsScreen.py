from random import choice
from typing import Dict, Optional

import pygame
import pygame_gui
from pygame_gui.core import IContainerLikeInterface

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UIModifiedScrollingContainer,
)
from scripts.screens.Screens import Screens
from scripts.utility import scale, get_text_box_theme


class ChangeFamilialTermsScreen(Screens):
    condition_details_box = image_cache.load_image(
        "resources/images/condition_details_box.png"
    ).convert_alpha()

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.elements: Dict[
            str, pygame_gui.core.UIElement | IContainerLikeInterface
        ] = {}
        self.selected_cat_elements: Dict[str, pygame_gui.core.UIElement] = {}

        self.the_cat: Optional[Cat] = None
        self.previous_cat: Optional[str] = None
        self.next_cat: Optional[str] = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    game.switches["root_cat"] = Cat.all_cats[self.previous_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    game.switches["root_cat"] = Cat.all_cats[self.next_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid next cat", self.next_cat)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_screen(game.last_screen_forupdate)

    def screen_switches(self):
        self.next_cat_button = UIImageButton(
            scale(pygame.Rect((1244, 50), (306, 60))),
            "",
            object_id="#next_cat_button",
            manager=MANAGER,
        )
        self.previous_cat_button = UIImageButton(
            scale(pygame.Rect((50, 50), (306, 60))),
            "",
            object_id="#previous_cat_button",
            manager=MANAGER,
        )
        self.back_button = UIImageButton(
            scale(pygame.Rect((50, 120), (210, 60))),
            "",
            object_id="#back_button",
            manager=MANAGER,
        )
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((100, 200), (1398, 1040))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/gender_framing.png"
                ).convert_alpha(),
                (699, 520),
            ),
            manager=MANAGER,
        )

        right_side_rect: pygame.Rect = scale(pygame.Rect((0, 574), (277, 330)))
        right_side_rect.topright = right_side_rect[:2]
        self.elements["sibling_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 574), (277, 330))),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )
        self.elements["parent_box"] = UIModifiedScrollingContainer(
            right_side_rect,
            manager=MANAGER,
            anchors={"right": "right", "right_target": self.elements["sibling_box"]},
        )
        self.elements["grandparent_box"] = UIModifiedScrollingContainer(
            right_side_rect,
            manager=MANAGER,
            anchors={"right": "right", "right_target": self.elements["parent_box"]},
        )
        self.elements["kit_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 574), (277, 330))),
            manager=MANAGER,
            anchors={"left_target": self.elements["sibling_box"]},
        )
        self.elements["grandkit_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 574), (277, 330))),
            manager=MANAGER,
            anchors={"left_target": self.elements["kit_box"]},
        )

        self.elements["mate_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 0), (277, 330))),
            manager=MANAGER,
            anchors={"top_target": self.elements["sibling_box"], "centerx": "centerx"},
        )

        right_side_rect: pygame.Rect = scale(pygame.Rect((0, 574), (277, 330)))
        right_side_rect.topright = (0, 0)
        self.elements["siblings_mate_box"] = UIModifiedScrollingContainer(
            right_side_rect,
            manager=MANAGER,
            anchors={
                "top": "top",
                "top_target": self.elements["parent_box"],
                "right": "right",
                "right_target": self.elements["mate_box"],
            },
        )
        self.elements["parents_sibling_box"] = UIModifiedScrollingContainer(
            right_side_rect,
            manager=MANAGER,
            anchors={
                "top_target": self.elements["grandparent_box"],
                "right": "right",
                "right_target": self.elements["siblings_mate_box"],
            },
        )
        self.elements["kits_mate_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 0), (277, 330))),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["parent_box"],
                "left_target": self.elements["mate_box"],
            },
        )

        self.elements["siblings_kit_box"] = UIModifiedScrollingContainer(
            scale(pygame.Rect((0, 0), (277, 330))),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["parent_box"],
                "left_target": self.elements["kits_mate_box"],
            },
        )

        self.populate_term_box("mate", "mate")
        self.populate_term_box("sibling", "sibling")
        self.populate_term_box("parent", "parent")
        self.populate_term_box("grandparent", "grandparent")
        self.populate_term_box("parents_sibling", "parent's sibling")
        self.populate_term_box("siblings_mate", "sibling's mate")
        self.populate_term_box("siblings_kit", "sibling's kit")
        self.populate_term_box("kit", "kit")
        self.populate_term_box("kits_mate", "kit's mate")
        self.populate_term_box("grandkit", "grandkit")

        self.update_selected_cat()
        self.determine_previous_and_next_cat()

    def exit_screen(self):
        self.back_button.kill()
        self.previous_cat_button.kill()
        self.next_cat_button.kill()

        [item.kill() for item in self.elements.values()]
        self.elements = {}

        [item.kill() for item in self.selected_cat_elements.values()]
        self.selected_cat_elements = {}

    def update_selected_cat(self):
        self.the_cat = Cat.fetch_cat(game.switches["cat"])

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((360, 210), (300, 300))),
            pygame.transform.scale(self.the_cat.sprite, (300, 300)),
            manager=MANAGER,
        )

        self.selected_cat_elements["cat_gender"] = pygame_gui.elements.UITextBox(
            self.the_cat.genderalign,
            scale(pygame.Rect((260, 500), (500, 500))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )
        name = str(self.the_cat.name)
        header = "Update " + name + "'s Familial Terms"
        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect((300, 50), (1000, 100))),
            header,
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
        )
        self.selected_cat_elements["description"] = pygame_gui.elements.UITextBox(
            f"<br> Here you can customize the terms that {name}'s kin will use "
            f"to refer to {choice(self.the_cat.pronouns)['object']}. This has no effect on gameplay.",
            scale(pygame.Rect((660, 265), (600, 200))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
        )

    def determine_previous_and_next_cat(self):
        """Determines where the next and previous buttons point to."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if (
            self.the_cat.dead
            and not is_instructor
            and self.the_cat.df == game.clan.instructor.df
            and not (self.the_cat.outside or self.the_cat.exiled)
        ):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if (
                    next_cat == 0
                    and check_cat.ID != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    previous_cat = check_cat.ID

                elif (
                    next_cat == 1
                    and check_cat != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

    def populate_term_box(self, term_name, term_text):
        self.elements[f"{term_name}_backdrop"] = pygame_gui.elements.UIImage(
            pygame.Rect((0, 0), self.elements[f"{term_name}_box"].rect[2:]),
            pygame.transform.scale(
                self.condition_details_box, self.elements[f"{term_name}_box"].rect[2:]
            ),
            manager=MANAGER,
            container=self.elements[f"{term_name}_box"],
        )
        self.elements[f"{term_name}_heading"] = pygame_gui.elements.UILabel(
            scale(pygame.Rect(0, 10, -1, 60)),
            term_text,
            container=self.elements[f"{term_name}_box"],
            object_id="#text_box_30_horizcenter",
        )
        self.elements[f"{term_name}_heading"].set_dimensions(
            (
                self.elements[f"{term_name}_box"].rect[2],
                self.elements[f"{term_name}_heading"].rect[3],
            )
        )
