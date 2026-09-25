import pygame as pg


class Button:
    def __init__(self, text: pg.Surface,
                 pos: tuple[int, int],
                 color: tuple[int, int, int]) -> None:
        self.margin_x: int = 35
        self.margin_y: int = 20
        self.color: tuple[int, int, int] = color
        self.text: pg.Surface = text

        self.rect: pg.Rect = self.text.get_rect()
        self.rect.inflate_ip(self.margin_x, self.margin_y)
        self.rect.topleft = pos

        self.max_hover_size: float = 15.0
        self.hover_speed: float = 2.5
        self.current_hover_size: float = 0.0

        self.is_clicked: bool = False

    def process(self, surface: pg.Surface) -> bool:
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()

        pg.draw.rect(surface, self.color, self.rect)
        # Draw text in center of box
        surface.blit(self.text, (self.rect.topleft[0] +
                                 (self.margin_x +
                                  self.current_hover_size) / 2.5,
                                 self.rect.centery - self.margin_y -
                                 (self.margin_y / 2)))

        if self.rect.collidepoint(mouse_pos):
            # Slowly lerp button size up
            if self.current_hover_size < self.max_hover_size:
                self.rect.inflate_ip(self.hover_speed, self.hover_speed)
                self.current_hover_size += self.hover_speed

            if pg.mouse.get_just_pressed()[0] == 1 and not self.is_clicked:
                self.is_clicked = True
                return True
        # Slowly lerp button size down
        elif self.current_hover_size > 0.0:
            self.rect.inflate_ip(-self.hover_speed, -self.hover_speed)
            self.current_hover_size -= self.hover_speed

        if not pg.mouse.get_pressed()[0]:
            self.is_clicked = False

        return False


class SmallButton:
    def __init__(self, shape_points: list[tuple[int, int]],
                 color: tuple[int, int, int]
                 ) -> None:
        self.shape: list[tuple[int, int]] = shape_points
        self.color: tuple[int, int, int] = color
        self.is_clicked: bool = False

    def process(self, surface: pg.Surface) -> bool:
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()

        rect = pg.draw.polygon(surface, self.color, self.shape)

        if rect.collidepoint(mouse_pos):
            if pg.mouse.get_just_pressed()[0] == 1 and not self.is_clicked:
                self.is_clicked = True
                return True

        if not pg.mouse.get_pressed()[0]:
            self.is_clicked = False

        return False

    @classmethod
    def reposition_arrows(cls, surface: pg.Rect,
                          flipped: bool = False) -> list[tuple[int, int]]:
        if flipped:
            return [(surface.left - 17,
                     surface.topleft[1] + 11),
                    (surface.left - 17,
                     surface.bottom - 10),
                    (surface.left - 60,
                     surface.centery)]
        else:
            return [(surface.right + 15,
                     surface.topright[1] + 10),
                    (surface.right + 15,
                     surface.bottom - 10),
                    (surface.right + 60,
                     surface.centery)]
