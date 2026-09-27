from src.node import Zone
from typing import Any
import pygame as pg
import math


class RenderUtils:
    def __init__(self) -> None:
        self.colors: dict[str, tuple[int, int, int]] = {
                "darkred": (80, 0, 0),
                "maroon": (90, 0, 0),
                "crimson": (220, 20, 60),
                "red": (255, 0, 0),
                "orange": (255, 127, 0),
                "darkbrown": (76, 63, 56),
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
        offset: pg.math.Vector2 = pg.math.Vector2(
                (camera_pos.x % grid_size, camera_pos.y % grid_size))

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


class RenderZone:
    def __init__(self, zone: Zone, sprite: pg.Surface,
                 color: tuple[int, int, int]) -> None:
        self.zone: Zone = zone
        self.sprite: pg.Surface = sprite
        self.color: tuple[int, int, int] = color
        self.font: pg.font.Font = pg.font.SysFont(None, 28)
        self.pos: pg.Vector2 = pg.Vector2(0, 0)

    def process(self, surface: pg.Surface, pos: pg.Vector2,
                scale: float, parent: Any) -> None:
        self.pos = pos
        mouse_pos = pg.mouse.get_pos()

        surface.blit(self.sprite, (pos[0] - self.sprite.get_rect().centerx,
                                   pos[1] - self.sprite.get_rect().centery))

        text = self.font.render((f"{self.zone.__str__()}\n"
                                 f"rule: {self.zone.rule}\n"
                                 f"drones: {self.zone.drone_amount}\n"
                                 f"max_drones: {self.zone.max_drones}\n"
                                 f"cost: {self.zone.distance}"), True,
                                parent.palette["text2"])
        rect = text.get_rect()
        rect.topleft = pos

        if self.sprite.get_rect(center=(pos * scale)).collidepoint(mouse_pos):
            surface.blit(text,
                         (pos[0], pos[1] + self.sprite.get_rect().bottom / 2))

class RenderDrone:
    def __init__(self, id: int, sprite: pg.Surface,
                 color: tuple[int, int, int]) -> None:
        self.id: str = f"D{id}"
        self.sprite: pg.Surface = sprite
        self.rect: pg.Rect = self.sprite.get_rect()
        self.color: tuple[int, int, int] = color

        self.pos: pg.Vector2 = pg.Vector2(0, 0)
        self.target: pg.Vector2 = pg.Vector2(0, 0)
        self.is_connection: bool = False
        self.is_at_target: bool = False
        self.offset_movement: int = 0

    def move_to_target(self, surface: pg.Surface, to_pos: pg.Vector2,
                       offset: pg.Vector2) -> bool:
        if not self.pos:
            self.pos = to_pos

        surface.blit(self.sprite,
                (self.pos.x - self.rect.centerx + offset.x,
                 self.pos.y - self.rect.centery + offset.y))

        if self.offset_movement:
            self.offset_movement -= 1
            return False

        self.pos = self.pos.move_towards(to_pos, 3.0)
        
        if self.pos == to_pos:
            return True
        return False
