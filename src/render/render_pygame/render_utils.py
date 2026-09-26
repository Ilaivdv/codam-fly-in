import pygame as pg
import math

class RenderUtils:
    def __init__(self) -> None:
        self.colors: dict[str, tuple[int, int, int]] = {
                "darkred": (50, 0, 0),
                "maroon": (90, 0, 0),
                "crimson": (220, 20, 60),
                "red": (255, 0, 0),
                "orange": (255, 127, 0),
                "brown": (210, 105, 30),
                "gold": (255, 193, 110),
                "yellow": (251, 200, 105),
                "green": (0, 255, 143),
                "blue": (90, 156, 255),
                "cyan": (0, 230, 255),
                "violet": (127, 0, 255),
                "purple": (128, 0, 128),
                "white": (255, 255, 255),
                "lightgray": (236, 237, 239),
                "midgray": (215, 224, 232),
                "gray": (90, 90, 90),
                "black": (0, 0, 0)
                }

    def draw_grid(self, surface: pg.Surface, color: tuple[int, int, int],
                  grid_size: int, camera_pos: pg.math.Vector2) -> None:
        offset: pg.math.Vector2 = pg.math.Vector2((camera_pos.x % grid_size,
                                                camera_pos.y % grid_size))

        tilesx: int = math.ceil(surface.width / grid_size)
        for x in range(0, tilesx):
            posx = x * grid_size + offset.x
            pg.draw.aaline(surface, color, (posx, 0),
                           (posx, surface.height), 5)

        tilesy: int = math.ceil(surface.height / grid_size)
        for y in range(0, tilesy):
            posy = y * grid_size + offset.y
            pg.draw.aaline(surface, color, (0, posy),
                           (surface.width, posy), 5)
