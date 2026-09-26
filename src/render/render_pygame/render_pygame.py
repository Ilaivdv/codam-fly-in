from src.render.map_process import MapProcess
from .buttons import Button, SmallButton
from src.utils import Logs
from src.node import Zone
from src.map import Map
from time import sleep
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
        self.screen: pg.Surface = pg.display.set_mode((1920, 1080),
                                                      flags=pg.RESIZABLE)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.font: pg.font.Font = pg.font.SysFont(None, 98)
        super().__init__(logs)

        self.in_map_select: bool = False
        self.camera_pos: tuple[int, int] = self.screen.get_rect().center

    def start_process(self, map_path: str, turn_delay: float = 0) -> None:
        super().start_process(map_path, turn_delay)

        grid_offset: int = 300
        camera_pos: pg.math.Vector2 = pg.math.Vector2(
                100, self.screen.get_rect().centery)
        # camera_pos: tuple[int, int] = 0, 0

        zones: dict[Zone, pg.Surface] = {}

        ## To modulate a sprite
        # zone_sprite.fill(Colors.RED, special_flags=pg.BLEND_RGBA_MIN)

        for zone in self._map.zones.values():
            zone_sprite = pg.image.load("assets/zone.svg").convert_alpha()
            zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))
            zones[zone] = zone_sprite

        # while not self._map.is_finished:
        while True:
            self.screen.fill(Colors.WHITE)
            for k, v in zones.items():
                self.screen.blit(v, (k.pos[0] * grid_offset + camera_pos.x,
                                     k.pos[1] * grid_offset + camera_pos.y))
            self.process_turn(self._auto_advance_turns)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[0]:
                    camera_pos.x += event.rel[0]
                    camera_pos.y += event.rel[1]
            
            if self._auto_advance_turns:
                sleep(turn_delay)

            pg.display.update()
            self.clock.tick(60)
        self.on_process_finished()
        pg.quit()

    def map_select(self, files: list[str]) -> Map:

        margin_left: int = 200

        # -- Main menu objects --
        logo_text = self.font.render("Fly-in", True, Colors.BLACK)
        maps_text = self.font.render("Maps", True, Colors.WHITE)
        quit_text = self.font.render("Quit", True, Colors.WHITE)
        maps_button = Button(maps_text, (margin_left, 350), Colors.YELLOW)
        quit_button = Button(quit_text, (margin_left, 460), Colors.YELLOW)

        # -- Map select objects --
        level_text_list: list[pg.Surface] = []
        current_dir: list[str] = files
        for i in current_dir:
            level_text_list.append(self.font.render(i[i.find("/") + 1:],
                                                    True, Colors.WHITE))

        level_button = Button(level_text_list[0], (margin_left, 350),
                              Colors.YELLOW)
        right_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect), Colors.GRAY)
        left_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect, True), Colors.GRAY)
        back_text = self.font.render("Back", True, Colors.WHITE)
        back_button = Button(back_text, (margin_left, 460), Colors.YELLOW)

        running: bool = True

        selected: int = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
            self.screen.fill(Colors.WHITE)
            self.screen.blit(logo_text, (margin_left, 150))
            # self.screen.blit(zone_sprite, zone_sprite.get_rect(
            #     center=self.screen.get_rect().center))

            if not self.in_map_select:
                if maps_button.process(self.screen):
                    self.in_map_select = True
                if quit_button.process(self.screen):
                    running = False
            else:
                if level_button.process(self.screen):
                    if current_dir[selected].endswith(".txt"):
                        return self._map_validator.validate_map(
                                    current_dir[selected])
                    else:
                        current_dir = self.get_options(current_dir[selected])
                        level_text_list.clear()
                        selected = 0
                        for i in current_dir:
                            level_text_list.append(self.font.render(
                                i[i.rfind("/", 0, len(i) - 1) + 1:], True, Colors.WHITE))

                        level_button = Button(level_text_list[0],
                                              (margin_left, 350),
                                              Colors.YELLOW)
                        right_button.shape = right_button.reposition_arrows(
                                level_button.rect)
                if right_button.process(self.screen):
                    if selected < len(current_dir) - 1:
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
                        selected = len(current_dir) - 1
                    level_button = Button(level_text_list[selected],
                                          (margin_left, 350),
                                          Colors.YELLOW)
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)
                if back_button.process(self.screen):
                    if current_dir == files:
                        self.in_map_select = False
                        continue
                    current_dir = files
                    level_text_list.clear()
                    selected = 0
                    for i in current_dir:
                        level_text_list.append(self.font.render(
                            i[i.find("/") + 1:], True, Colors.WHITE))

                    level_button = Button(level_text_list[0],
                                          (margin_left, 350),
                                          Colors.YELLOW)
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)

            pg.display.update()
            self.clock.tick(60)
        pg.quit()
        sys.exit()

    def process_turn(self, auto_advance: bool) -> None:
        self._map.advance_turn()


    def on_process_finished(self) -> None:
        ...
