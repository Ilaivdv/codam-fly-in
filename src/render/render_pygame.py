from src.render.map_process import MapProcess
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
        self.font: pg.font.Font = pg.font.SysFont("arialblack", 98)
        super().__init__(logs)

    def map_select(self, files: list[str]) -> Map:

        zone_sprite = pg.image.load("assets/zone.svg").convert_alpha()
        zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))
        text = self.font.render("Quit", True, Colors.WHITE)
        button = self.Button(text, (100, 100), Colors.YELLOW)
        button2 = self.Button(text, (100, 210), Colors.YELLOW)

        ## To modulate a sprite
        # zone_sprite.fill(Colors.RED, special_flags=pg.BLEND_RGBA_MIN)

        running: bool = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.screen.fill(Colors.BLACK)
            self.screen.blit(zone_sprite, zone_sprite.get_rect(
                center=self.screen.get_rect().center))

            if button.process(self.screen, text):
                running = False
            if button2.process(self.screen, text):
                running = False

            pg.display.update()
            self.clock.tick(60)
        pg.quit()
        sys.exit()

    def process_turn(self, auto_advance: bool) -> None:
        ...

    def on_process_finished(self) -> None:
        ...

    # -- CLASSES --
    class Button:
        def __init__(self, text: pg.Surface,
                     pos: tuple[int, int], color: Colors) -> None:
            self.margin_x: int = 35
            self.margin_y: int = 20
            self.color: Colors = color
            self.text: pg.Surface = text

            self.rect: pg.Rect = self.text.get_rect()
            self.rect.inflate_ip(self.margin_x, self.margin_y)
            self.rect.topleft = pos

            self.max_hover_size: float = 15.0
            self.hover_speed: float = 2.5
            self.current_hover_size: float = 0.0

            self.is_clicked: bool = False

        def process(self, surface: pg.Surface, text: pg.Surface) -> bool:
            mouse_pos: tuple[int, int] = pg.mouse.get_pos()

            # pg.draw.rect(surface, self.color, self.rect)
            pg.draw.rect(surface, self.color, self.rect)
            surface.blit(text, (self.rect.topleft[0] +
                                (self.margin_x +
                                 self.current_hover_size) / 2.5,
                                self.rect.topleft[1] + self.margin_y / 1.5))

            if self.rect.collidepoint(mouse_pos):
                if self.current_hover_size < self.max_hover_size:
                    self.rect.inflate_ip(self.hover_speed, self.hover_speed)
                    self.current_hover_size += self.hover_speed

                if pg.mouse.get_pressed()[0] == 1 and not self.is_clicked:
                    self.is_clicked = True
                    return True
            elif self.current_hover_size > 0.0:
                self.rect.inflate_ip(-self.hover_speed, -self.hover_speed)
                self.current_hover_size -= self.hover_speed

            if not pg.mouse.get_pressed()[0]:
                self.is_clicked = False

            return False
