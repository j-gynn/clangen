from typing import TYPE_CHECKING

import ujson

if TYPE_CHECKING:
    from scripts.screens.Screens import Screens

from math import floor
from typing import Optional, Tuple

import pygame
import pygame_gui

from scripts.game_structure.ui_manager import UIManager
from scripts.ui.generate_screen_scale_json import generate_screen_scale


offset = (0, 0)
screen_x = 800
screen_y = 700
screen_scale = 1
game_screen_size = (800, 700)
fullscreen_size: Tuple[int, int] = (0, 0)
windowed_size: Tuple[int, int] = (800, 700)
MANAGER: Optional[pygame_gui.UIManager] = None
screen: Optional[pygame.Surface] = None
curr_variable_dict = {}

display_change_in_progress = False  # this acts as a lock to ensure we don't end up in a loop of fullscreen changes


def set_display_mode(
    fullscreen: bool = None,
    source_screen: Optional["Screens"] = None,
    show_confirm_dialog: bool = True,
    ingame_switch: bool = True,
    override_screen_size=None,
):
    """
    Change the display settings here. Called when the game first runs and whenever the screen size changes
    (e.g. windowed resizing or swapping to fullscren)
    :param fullscreen: Whether to put the game in fullscreen, default None
    :param source_screen: The screen that called this request, default None
    :param show_confirm_dialog: Whether to display the "are you sure you want to make these changes" dialog, default True
    :param ingame_switch: True if we need to load in data from the game after rebuilding
    :param override_screen_size: Used exclusively to handle minimum size banding
    :return: None
    """
    global display_change_in_progress

    # if we're already in the process of changing the display
    if display_change_in_progress:
        return

    global offset
    global screen_x
    global screen_y
    global screen_scale
    global game_screen_size
    global fullscreen_size
    global windowed_size
    global screen
    global MANAGER
    global curr_variable_dict

    display_change_in_progress = True

    old_offset = offset
    old_scale = screen_scale
    mouse_pos = pygame.mouse.get_pos()

    from scripts.game_structure.game_essentials import game

    if fullscreen is None:
        fullscreen = game.settings["fullscreen"]

    with open("resources/screen_config.json", "r") as read_config:
        screen_config = ujson.load(read_config)

    display_sizes = pygame.display.get_desktop_sizes()  # the primary display
    screen_config["fullscreen_display"] = (
        screen_config["fullscreen_display"]
        if screen_config["fullscreen_display"] < len(display_sizes)
        else 0
    )
    fullscreen_size = display_sizes[screen_config["fullscreen_display"]]
    # display_size = [3840, 2160]

    if source_screen is not None:
        curr_variable_dict = source_screen.display_change_save()

    # Getting the correct screen sizes
    if fullscreen:
        display_size = fullscreen_size
        # display_size = [3840, 2160]

        if ingame_switch:
            # set the windowed size to whatever it was before we fullscreened
            windowed_size = screen.get_size()

        determine_screen_scale(display_size, ingame_switch)

        screen = pygame.display.set_mode(
            display_size,
            flags=pygame.FULLSCREEN,
            display=screen_config["fullscreen_display"],
        )
    else:
        if screen is not None and not bool(screen.get_flags() & pygame.FULLSCREEN):
            windowed_size = (
                override_screen_size
                if override_screen_size is not None
                else screen.get_size()
            )
        determine_screen_scale(windowed_size, ingame_switch)
        screen = pygame.display.set_mode(
            windowed_size, flags=pygame.RESIZABLE | pygame.DOUBLEBUF
        )

    try:
        source_screen.show_bg(blur_only=True)
        pygame.display.flip()
    except AttributeError:
        screen.fill(
            game.config["theme"][
                "dark_mode_background"
                if game.settings["dark mode"]
                else "light_mode_background"
            ]
        )
        pygame.display.flip()

    # BUILD THE MANAGER (or modify it appropriately)
    if source_screen is None:
        MANAGER = load_manager((screen_x, screen_y), offset, scale=screen_scale)
    elif old_scale != screen_scale:
        # generate new theme
        origin = "resources/theme/master_screen_scale.json"
        theme_location = "resources/theme/generated/screen_scale.json"
        generate_screen_scale(origin, theme_location, screen_scale)
        MANAGER.get_theme().load_theme(theme_location)

    # HANDLE IN-GAME SCREEN SWITCHING
    if source_screen is not None:
        import scripts.screens.screens_core.screens_core

        MANAGER.set_window_resolution(game_screen_size)
        MANAGER.set_offset(offset)
        scripts.screens.screens_core.screens_core.rebuild_core(should_rebuild_bgs=False)
        if old_scale != screen_scale:
            from scripts.screens.all_screens import AllScreens
            import scripts.debug_menu

            game.save_settings(currentscreen=source_screen)
            try:
                source_screen.exit_screen()
            except AttributeError:
                pass

            MANAGER.clear_and_reset()
            MANAGER.set_window_resolution(game_screen_size)
            MANAGER.set_offset(offset)

            AllScreens.rebuild_all_screens()

            scripts.screens.screens_core.screens_core.rebuild_core(
                should_rebuild_bgs=False
            )
            scripts.debug_menu.debugmode.rebuild_console()

            screen_name = source_screen.name.replace(" ", "_")
            new_screen: "Screens" = getattr(AllScreens, screen_name)
            new_screen.screen_switches()
            if ingame_switch:
                new_screen.display_change_load(curr_variable_dict)
                new_screen.show_bg()

    # REPOPULATE THE GAME
    if curr_variable_dict is not None and show_confirm_dialog:
        from scripts.screens.all_screens import AllScreens

        new_screen: "Screens" = getattr(
            AllScreens, game.switches["cur_screen"].replace(" ", "_")
        )
        new_screen.display_change_load(curr_variable_dict)

    # preloading the associated fonts
    if not MANAGER.ui_theme.get_font_dictionary().check_font_preloaded(
        f"notosans_bold_aa_{floor(11 * screen_scale)}"
    ):
        MANAGER.preload_fonts(
            [
                {
                    "name": "notosans",
                    "point_size": floor(11 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(13 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(15 * screen_scale),
                    "style": "bold",
                },
                {
                    "name": "notosans",
                    "point_size": floor(13 * screen_scale),
                    "style": "italic",
                },
                {
                    "name": "notosans",
                    "point_size": floor(15 * screen_scale),
                    "style": "italic",
                },
                {
                    "name": "notosans",
                    "point_size": floor(17 * screen_scale),
                    "style": "bold",
                },  # this is only used on the allegiances screen?
                {
                    "name": "clangen",
                    "point_size": floor(18 * screen_scale),
                    "style": "regular",
                },
            ]
        )

    display_change_in_progress = False
    if source_screen is not None and show_confirm_dialog:
        from scripts.game_structure.windows import ConfirmDisplayChanges

        ConfirmDisplayChanges(source_screen=source_screen)


def determine_screen_scale(xy: Tuple[int, int], ingame_switch):
    """
    Determines how big to render contents.
    :param xy: The screen size
    :return: None
    """
    global screen_scale, screen_x, screen_y, offset, game_screen_size

    x, y = xy

    if ingame_switch:
        from scripts.game_structure.game_essentials import game

        screen_config = game.settings
    else:
        with open("saves/settings.json", "r") as read_config:
            screen_config = ujson.load(read_config)

    if "fullscreen scaling" in screen_config and screen_config["fullscreen scaling"]:
        scalex = (x - 20) // 80
        scaley = (y - 20) // 70

        if screen_config["fullscreen"] or x // 8 == y // 7:
            # if scaling is dynamic, we can say that the border can be omitted if we're the perfect size
            scalex = x // 80
            scaley = y // 70

        screen_scale = min(scalex, scaley) / 10

        screen_x = 800 * screen_scale
        screen_y = 700 * screen_scale
    else:
        # this means screen scales in multiples of 200 x 175 which has a reasonable tradeoff for crunch
        scalex = x // 200
        scaley = y // 175
        screen_scale = min(scalex, scaley) / 4
        screen_x = 800 * screen_scale
        screen_y = 700 * screen_scale

    offset = (
        floor((x - screen_x) / 2),
        floor((y - screen_y) / 2),
    )
    game_screen_size = (screen_x, screen_y)


def toggle_fullscreen(
    fullscreen: Optional[bool] = None,
    source_screen: Optional["Screens"] = None,
    show_confirm_dialog: bool = True,
    ingame_switch: bool = True,
):
    """
    Swap between fullscreen modes. Wraps the necessary game save to store the new value.
    :param fullscreen: Can be used to override the toggle to an explicit value. Leave as None to simply toggle.
    :param source_screen: Screen requesting the fullscreen toggle.
    :param show_confirm_dialog: True to show the confirm changes dialog, default True. Does nothing if source_screen is None.
    :param ingame_switch: Whether this was triggered by a user. Default True
    :return:
    """
    global display_change_in_progress

    # if we're already in the process of changing the display, do nothing
    while display_change_in_progress:
        continue

    from scripts.game_structure.game_essentials import game

    if fullscreen is None:
        fullscreen = not game.settings["fullscreen"]

    game.settings["fullscreen"] = fullscreen
    game.save_settings()

    set_display_mode(
        fullscreen=fullscreen,
        source_screen=source_screen,
        show_confirm_dialog=show_confirm_dialog,
        ingame_switch=ingame_switch,
    )


def load_manager(res: Tuple[int, int], screen_offset: Tuple[int, int], scale: float):
    global MANAGER
    if MANAGER is not None:
        MANAGER = None

    # initialize pygame_gui manager, and load themes
    manager = UIManager(
        res,
        screen_offset,
        scale,
        None,
        enable_live_theme_updates=False,
    )
    manager.add_font_paths(
        font_name="notosans",
        regular_path="resources/fonts/NotoSans-Medium.ttf",
        bold_path="resources/fonts/NotoSans-ExtraBold.ttf",
        italic_path="resources/fonts/NotoSans-MediumItalic.ttf",
        bold_italic_path="resources/fonts/NotoSans-ExtraBoldItalic.ttf",
    )
    manager.add_font_paths(
        font_name="clangen", regular_path="resources/fonts/clangen.ttf"
    )

    generate_screen_scale(
        "resources/theme/master_screen_scale.json",
        "resources/theme/generated/screen_scale.json",
        screen_scale,
    )

    manager.get_theme().load_theme("resources/theme/generated/screen_scale.json")
    manager.get_theme().load_theme("resources/theme/themes/dark.json")

    return manager
