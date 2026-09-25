from src.render.map_process import MapProcess
from .buttons import Button, SmallButton
from src.utils import Logs
from src.map import Map
import pygame as pg
import sys


class Colors:
    """ A class containing RGB color values. """

    MAROON: tuple[int, int, int] = 90, 0, 0
    CRIMSON: tuple[int, int, int] = 220, 20, 60,
    RED: tuple[int, int, int] = 255, 0, 0,
    ORANGE: tuple[int, int, int] = 255, 127, 0,
    BROWN: tuple[int, int, int] = 210, 105, 30,
    GOLD: tuple[int, int, int] = 255, 193, 110,
    YELLOW: tuple[int, int, int] = 251, 200, 105,
    GREEN: tuple[int, int, int] = 0, 255, 143,
    BLUE: tuple[int, int, int] = 90, 156, 255,
    CYAN: tuple[int, int, int] = 0, 230, 255,
    VIOLET: tuple[int, int, int] = 127, 0, 255,
    PURPLE: tuple[int, int, int] = 128, 0, 128,
    WHITE: tuple[int, int, int] = 255, 255, 255,
    GRAY: tuple[int, int, int] = 90, 90, 90,
    BLACK: tuple[int, int, int] = 0, 0, 0


class PygameRenderer(MapProcess):
    def __init__(self, logs: Logs) -> None:
        pg.init()
        pg.display.set_caption("Fly-in")
        self.screen: pg.Surface = pg.display.set_mode((1080, 720),
                                                      flags=pg.RESIZABLE)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.font: pg.font.Font = pg.font.SysFont(None, 98)
        super().__init__(logs)

    def map_select(self, files: list[str]) -> Map:

        margin_left: int = 200

        zone_sprite = pg.image.load("assets/zone.svg").convert_alpha()
        zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))

        logo_text = self.font.render("Fly-in", True, Colors.WHITE)
        maps_text = self.font.render("Maps", True, Colors.WHITE)
        quit_text = self.font.render("Quit", True, Colors.WHITE)
        maps_button = Button(maps_text, (margin_left, 350), Colors.YELLOW)
        quit_button = Button(quit_text, (margin_left, 460), Colors.YELLOW)

        level_text_list: list[pg.Surface] = []
        for i in files:
            level_text_list.append(self.font.render(i[i.find("/") + 1:], True, Colors.WHITE))

        level_button = Button(level_text_list[0], (margin_left, 350),
                                   Colors.YELLOW)
        right_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect), Colors.WHITE)
        left_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect, True), Colors.WHITE)
        # left_button = SmallButton(
        #         [(level_button.rect.left - 17,
        #           level_button.rect.topleft[1] + 11),
        #          (level_button.rect.left - 17,
        #           level_button.rect.bottom - 10),
        #          (level_button.rect.left - 60,
        #           level_button.rect.centery)], Colors.WHITE)

        ## To modulate a sprite
        # zone_sprite.fill(Colors.RED, special_flags=pg.BLEND_RGBA_MIN)

        running: bool = True
        in_map_select: bool = False

        selected: int = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.screen.fill(Colors.BLACK)
            self.screen.blit(logo_text, (margin_left, 150))
            # self.screen.blit(zone_sprite, zone_sprite.get_rect(
            #     center=self.screen.get_rect().center))

            if not in_map_select:
                if maps_button.process(self.screen):
                    in_map_select = True
                if quit_button.process(self.screen):
                    running = False
            else:
                if level_button.process(self.screen):
                    in_map_select = False
                if right_button.process(self.screen):
                    if selected < len(files) - 1:
                        selected += 1
                    else:
                        selected = 0
                    level_button = Button(level_text_list[selected],
                                               (margin_left, 350),
                                               Colors.YELLOW)
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)
                if left_button.process(self.screen):
                    if selected > 0:
                        selected -= 1
                    else:
                        selected = len(files) - 1
                    level_button = Button(level_text_list[selected],
                                               (margin_left, 350),
                                               Colors.YELLOW)
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)
                    # left_button.shape = left_button.reposition_arrows(
                    #         level_button.rect, True)

            pg.display.update()
            self.clock.tick(60)
        pg.quit()
        sys.exit()

    def process_turn(self, auto_advance: bool) -> None:
        ...

    def on_process_finished(self) -> None:
        ...
