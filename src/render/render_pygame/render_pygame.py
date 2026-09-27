from .render_utils import RenderUtils, RenderZone, RenderDrone
from src.render.map_process import MapProcess
from .buttons import Button, SmallButton
from src.node import Connection
from src.utils import Logs
from src.map import Map
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
                "text2": self.utils.colors["darkbrown"],
                "button1": self.utils.colors["yellow"],
                "button2": self.utils.colors["darkbrown"],
                "road1": self.utils.colors["white"],
                }
        self.palette: dict[str, tuple[int, int, int]] = self.light_palette

    def start_process(self, map_path: str, turn_delay: float = 0) -> None:
        super().start_process(map_path, turn_delay)

        camera_pos: pg.math.Vector2 = pg.math.Vector2(
                100, self.screen.get_rect().centery)

        start_text = self.font.render("Start", True, self.palette["text1"])
        status_button = Button(start_text, (20, 20),
                              self.palette["button1"])

        start_pressed: bool = False

        # Initialize zone sprites
        zones: list[RenderZone] = []
        for zone in self._map.zones.values():
            color: tuple[int, int, int]
            try:
                color = self.utils.colors[zone.color.lower()]
            except Exception:
                color = self.utils.colors["gray"]

            if zone.color.lower() == "rainbow":
                zone_sprite = pg.image.load(
                        "assets/rainbow_zone.svg").convert_alpha()
            else:
                zone_sprite = pg.image.load("assets/zone.svg").convert_alpha()
                zone_sprite.fill(color, special_flags=pg.BLENDFACTOR_SRC_COLOR)
            zone_sprite = pg.transform.smoothscale(zone_sprite, (100, 100))
            zones.append(RenderZone(zone, zone_sprite, color))

        # Initialize drone sprites
        drones: list[RenderDrone] = []
        for i in range(self._map.nb_drones):
            drone_sprite = pg.image.load("assets/drone.svg").convert_alpha()
            drone_sprite = pg.transform.scale(drone_sprite, (75, 75))
            color = self.utils.colors["midgray"]

            drone_sprite.fill(color, special_flags=pg.BLENDFACTOR_SRC_COLOR)
            drone = RenderDrone(i + 1, drone_sprite, color)
            drone.target = pg.Vector2(self._map.start.pos)
            drones.append(drone)

        print(f"{len(drones)} drones loaded")

        level = self.screen.copy()
        scale: float = 1

        drones_turn_finished: int = 0
        current_turn: dict[str, tuple[pg.Vector2, bool]] = {}
        is_paused: bool = False
        is_finished: bool = False
        while True:
            level.fill(self.palette["bg1"])
            self.utils.draw_grid(level, self.palette["bg2"],
                                 self.grid_size, camera_pos)

            # Draw connections first so its under the zones
            for i in zones:
                from_pos: pg.Vector2 = pg.Vector2(
                        i.zone.pos[0] * self.grid_size + self.grid_size
                        / 2 + camera_pos.x, i.zone.pos[1] * self.grid_size +
                        self.grid_size / 2 + camera_pos.y)

                for connect in i.zone.get_neighbors():
                    if type(connect) is Connection and not connect.is_behind:
                        to_pos: pg.Vector2 = pg.Vector2(
                                connect.to.pos[0] * self.grid_size +
                                self.grid_size
                                / 2 + camera_pos.x,
                                connect.to.pos[1] * self.grid_size +
                                self.grid_size
                                / 2 + camera_pos.y)

                        pg.draw.aaline(level, self.palette["road1"],
                                       from_pos, to_pos, 32)

            # Draw drones here
            for i in drones:
                target_pos: pg.Vector2 = pg.Vector2(
                        i.target.x * self.grid_size + self.grid_size / 2,
                        i.target.y * self.grid_size + self.grid_size / 2)

                if i.move_to_target(level, target_pos, camera_pos, is_paused) \
                        and not i.is_at_target:
                    drones_turn_finished += 1
                    i.is_at_target = True

            for i in zones:
                pos: pg.Vector2 = pg.Vector2(i.zone.pos[0] * self.grid_size +
                                             self.grid_size
                                             / 2 + camera_pos.x,
                                             i.zone.pos[1] * self.grid_size +
                                             self.grid_size
                                             / 2 + camera_pos.y)
                i.process(level, pos, scale, self)

            if start_pressed and drones_turn_finished == self._map.nb_drones \
                    and not self._map.is_finished and not is_paused:
                self.process_turn(False)
                drones_turn_finished = 0
                next_moves = self._logs.turns[-1].split()
                current_turn.clear()

                for move in next_moves:
                    next_turn = move.split("-", maxsplit=1)
                    if next_turn[1].startswith("connection-"):
                        to_zone = self._map.zones[next_turn[1][
                            next_turn[1].find("-") + 1:]].pos

                        current_turn[next_turn[0]] = pg.Vector2(to_zone), True
                    else:
                        current_turn[next_turn[0]] = pg.Vector2(
                                self._map.zones[next_turn[1]].pos), False

                wait_time = 0
                prev_drone: RenderDrone = drones[-1]
                for drone in drones:
                    drone.is_at_target = False
                    try:
                        if current_turn[drone.id][1]:
                            drone.target = pg.Vector2(
                                    (current_turn[drone.id][0].x -
                                     drone.target.x) / 2 + drone.target.x,
                                    (current_turn[drone.id][0].y -
                                     drone.target.y) / 2 + drone.target.y)
                        else:
                            drone.target = current_turn[drone.id][0]
                    except KeyError:
                        pass
                    else:
                        if drone.pos == prev_drone.pos:
                            drone.offset_movement = wait_time
                            wait_time += 30
                        else:
                            wait_time = 0
                        prev_drone = drone

                print(self._logs.turns[-1])

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[0]:
                    camera_pos.x += event.rel[0]
                    camera_pos.y += event.rel[1]
                if event.type == pg.MOUSEBUTTONDOWN:
                    # Scroll up
                    if event.button == 4:
                        scale += 0.1
                        if scale == 1.0:
                            level = pg.transform.scale(level, self.screen.size)
                    # Scroll down
                    if event.button == 5 and scale > 0.6:
                        scale -= 0.1
                        if scale < 1.0:
                            level = pg.transform.scale_by(level, 1.2)

                if event.type == pg.VIDEORESIZE:
                    scale = 1.0
                    level = pg.transform.scale(level, self.screen.size)
                    level = self.screen.copy()

            # -- Buttons/UI --
            if status_button.process(level):
                if is_finished:
                    pg.quit()
                    sys.exit()
                elif start_pressed:
                    is_paused = not is_paused
                    if is_paused:
                        resume_text = self.font.render("Resume", True,
                                                       self.palette["text1"])
                        status_button = Button(resume_text, (20, 20),
                                              self.palette["button1"])
                    elif not is_paused:
                        pause_text = self.font.render("Pause", True,
                                                      self.palette["text1"])
                        status_button = Button(pause_text, (20, 20),
                                              self.palette["button1"])
                else:
                    start_pressed = True
                    pause_text = self.font.render("Pause", True,
                                                  self.palette["text1"])
                    status_button = Button(pause_text, (20, 20),
                                          self.palette["button1"])

            if self._map.is_finished and \
                    drones_turn_finished == self._map.nb_drones and not \
                    is_finished:
                quit_text = self.font.render("Quit", True,
                                              self.palette["text1"])
                status_button = Button(quit_text, (20, 20),
                                      self.palette["button1"])
                is_finished = True

            turn_text = self.font.render(f"Turn {len(self._logs.turns)}", True,
                                         self.palette["text2"])
            level.blit(turn_text, (20, 140))

                # if quit_button.process(level):
                #     pg.quit()
                #     sys.exit()

            self.screen.blit(pg.transform.smoothscale_by(level, scale))
            pg.display.update()
            self.clock.tick(60)

    def map_select(self, files: list[str]) -> Map:

        margin_left: int = 200

        # -- Main menu objects --
        logo_font = pg.font.SysFont(None, 160)
        logo_text = logo_font.render("Fly-in", True,
                                     self.palette["text2"])
        maps_text = self.font.render("Maps", True, self.palette["text1"])
        maps_button = Button(maps_text, (margin_left, 450),
                             self.palette["button1"])
        quit_text = self.font.render("Quit", True, self.palette["text1"])
        quit_button = Button(quit_text, (margin_left, 560),
                             self.palette["button1"])

        # -- Map select objects --
        level_text_list: list[pg.Surface] = []
        current_dir: list[str] = files
        for i in current_dir:
            level_text_list.append(self.font.render(
                i[i.find("/") + 1:], True, self.palette["text1"]))

        level_button = Button(level_text_list[0], (margin_left, 450),
                              self.palette["button1"])
        right_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect), self.palette["button1"])
        left_button = SmallButton(SmallButton.reposition_arrows(
            level_button.rect, True), self.palette["button1"])
        back_text = self.font.render("Back", True, self.palette["text1"])
        back_button = Button(back_text, (margin_left, 560),
                             self.palette["button1"])

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
                                              (margin_left, 450),
                                              self.palette["button1"])
                        right_button.shape = right_button.reposition_arrows(
                                level_button.rect)
                if right_button.process(self.screen):
                    if selected < len(current_dir) - 1:
                        selected += 1
                    else:
                        selected = 0
                    level_button = Button(level_text_list[selected],
                                          (margin_left, 450),
                                          self.palette["button1"])
                    right_button.shape = right_button.reposition_arrows(
                            level_button.rect)
                if left_button.process(self.screen):
                    if selected > 0:
                        selected -= 1
                    else:
                        selected = len(current_dir) - 1
                    level_button = Button(level_text_list[selected],
                                          (margin_left, 450),
                                          self.palette["button1"])
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
                                          (margin_left, 450),
                                          self.palette["button1"])
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
