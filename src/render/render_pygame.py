from src.render.map_process import MapProcess
from src.utils import Logs
from src.map import Map
import pygame as pg
import sys


class Colors:
    """ A class containing RGB color values. """

    MAROON: tuple[int, int,int] = 85, 0, 0,
    CRIMSON: tuple[int, int,int]  = 220, 20, 60,
    RED: tuple[int, int,int]  = 255, 0, 0,
    ORANGE: tuple[int, int,int]  = 255, 127, 0,
    BROWN: tuple[int, int,int]  = 210, 105, 30,
    GOLD: tuple[int, int,int]  = 255, 193, 110,
    YELLOW: tuple[int, int,int]  = 255, 255, 120,
    GREEN: tuple[int, int,int]  = 0, 255, 143,
    BLUE: tuple[int, int,int]  = 90, 156, 255,
    CYAN: tuple[int, int,int]  = 0, 230, 255,
    VIOLET: tuple[int, int,int]  = 127, 0, 255,
    PURPLE: tuple[int, int,int]  = 128, 0, 128,
    WHITE: tuple[int, int,int]  = 255, 255, 255,
    GRAY: tuple[int, int,int]  = 90, 90, 90,
    BLACK: tuple[int, int,int]  = 0, 0, 0


class PygameRenderer(MapProcess):
    def __init__(self, logs: Logs) -> None:
        pg.init()
        pg.display.set_caption("Fly-in")
        self.screen: pg.Surface = pg.display.set_mode((1080, 720),
                                                      flags=pg.RESIZABLE)
        super().__init__(logs)

    def map_select(self, files: list[str]) -> Map:

        zone_sprite= pg.image.load("assets/zone.svg").convert_alpha()
        zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))

        running: bool = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.screen.fill(Colors.WHITE)
            self.screen.blit(zone_sprite, zone_sprite.get_rect(
                center=self.screen.get_rect().center))
            pg.display.update()
        pg.quit()
        sys.exit()



    def process_turn(self, auto_advance: bool) -> None:
        ...

    def on_process_finished(self) -> None:
        ...

    def on_input(self) -> bool:
        ...
