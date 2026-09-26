from src.render.map_process import MapProcess
from .buttons import Button, SmallButton
from .render_utils import RenderUtils
from src.utils import Logs
from src.node import Zone
from src.map import Map
from time import sleep
import pygame as pg
import sys


class PygameRenderer(MapProcess):
    def __init__(self, logs: Logs) -> None:
        super().__init__(logs)
        pg.init()
        pg.display.set_caption("Fly-in")
        self.screen: pg.Surface = pg.display.set_mode((1920, 1080),
                                                      flags=pg.RESIZABLE)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.font: pg.font.Font = pg.font.SysFont(None, 98)

        self.in_map_select: bool = False
        self.grid_size: int = 300

        self.utils: RenderUtils = RenderUtils()
        self.light_palette: dict[str, tuple[int, int, int]] = {
                "bg1": self.utils.colors["lightgray"],
                "bg2": self.utils.colors["midgray"],
                "text1": self.utils.colors["white"],
                "text2": self.utils.colors["black"],
                }
        self.palette: dict[str, tuple[int, int, int]] = self.light_palette

    def start_process(self, map_path: str, turn_delay: float = 0) -> None:
        super().start_process(map_path, turn_delay)

        camera_pos: pg.math.Vector2 = pg.math.Vector2(
                100, self.screen.get_rect().centery)

        zones: dict[Zone, pg.Surface] = {}
        for zone in self._map.zones.values():
            color: tuple[int, int, int]
            try:
                color = self.utils.colors[zone.color.lower()]
            except Exception:
                color = self.utils.colors["gray"]

            zone_sprite = pg.image.load("assets/zone.svg").convert_alpha()
            zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))
            zone_sprite.fill(color,
                             special_flags=pg.BLEND_RGBA_MIN)
            zones[zone] = zone_sprite

        # while not self._map.is_finished:
        while True:
            self.screen.fill(self.palette["bg1"])
            self.utils.draw_grid(self.screen, self.palette["bg2"],
                                 self.grid_size, camera_pos)

            for k, v in zones.items():
                self.screen.blit(v, (k.pos[0] * self.grid_size + self.grid_size
                                     / 2 + camera_pos.x -
                                     v.get_rect().centerx,
                                     k.pos[1] * self.grid_size + self.grid_size
                                     / 2 + camera_pos.y -
                                     v.get_rect().centery))
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
        logo_text = self.font.render("Fly-in", True,
                                     self.palette["text2"])
        maps_text = self.font.render("Maps", True, self.palette["text1"])
        quit_text = self.font.render("Quit", True, self.palette["text1"])
        maps_button = Button(maps_text, (margin_left, 350),
                             self.utils.colors["yellow"])
        quit_button = Button(quit_text, (margin_left, 460),
                             self.utils.colors["yellow"])

        # -- Map select objects --
        level_text_list: list[pg.Surface] = []
        current_dir: list[str] = files
        for i in current_dir:
            level_text_list.append(self.font.render(
                i[i.find("/") + 1:], True, self.palette["text1"]))

        level_button = Button(level_text_list[0], (margin_left, 350),
                              self.utils.colors["yellow"])
        right_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect), self.utils.colors["gray"])
        left_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect, True), self.utils.colors["gray"])
        back_text = self.font.render("Back", True, self.palette["text1"])
        back_button = Button(back_text, (margin_left, 460),
                             self.utils.colors["yellow"])

        running: bool = True

        selected: int = 0
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    sys.exit()
            self.screen.fill(self.palette["bg1"])
            self.utils.draw_grid(self.screen, self.palette["bg2"],
                                 self.grid_size, pg.math.Vector2(0, 0))
            self.screen.blit(logo_text, (margin_left, 150))

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
                                i[i.rfind("/", 0, len(i) - 1) + 1:], True,
                                self.palette["text1"]))

                        level_button = Button(level_text_list[0],
                                              (margin_left, 350),
                                              self.utils.colors["yellow"])
                        right_button.shape = right_button.reposition_arrows(
                                level_button.rect)
                if right_button.process(self.screen):
                    if selected < len(current_dir) - 1:
                        selected += 1
                    else:
                        selected = 0
                    level_button = Button(level_text_list[selected],
                                          (margin_left, 350),
                                          self.utils.colors["yellow"])
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)
                if left_button.process(self.screen):
                    if selected > 0:
                        selected -= 1
                    else:
                        selected = len(current_dir) - 1
                    level_button = Button(level_text_list[selected],
                                          (margin_left, 350),
                                          self.utils.colors["yellow"])
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
                            i[i.find("/") + 1:], True,
                            self.palette["text1"]))

                    level_button = Button(level_text_list[0],
                                          (margin_left, 350),
                                          self.utils.colors["yellow"])
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
