"""Hellbound: a small, asset-free, two-level ray-casting shooter."""

from __future__ import annotations

import argparse
import math
import sys

import pygame

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FOV = math.radians(66)
RAY_COUNT = 320
MAX_RAY_DISTANCE = 24.0
LEVELS = (
    {
        "name": "THE FORGOTTEN KEEP",
        "wall": (150, 54, 42),
        "map": (
            "################",
            "#....#.........#",
            "#....#..##.....#",
            "#..............#",
            "#..##....#.....#",
            "#......E.#..E..#",
            "#..............#",
            "#....##........#",
            "#...........#..#",
            "#..P......E.X..#",
            "#..............#",
            "################",
        ),
    },
    {
        "name": "THE ABYSSAL FOUNDRY",
        "wall": (85, 100, 125),
        "map": (
            "################",
            "#..............#",
            "#.##...##......#",
            "#....E.........#",
            "#..........##..#",
            "#..##..........#",
            "#.....##....E..#",
            "#..............#",
            "#..E..#.....##.#",
            "#..P..#...E..X.#",
            "#......E.......#",
            "################",
        ),
    },
)


def normalize_angle(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def parse_level(level_index: int) -> tuple[list[str], tuple[float, float], tuple[float, float], list[dict]]:
    rows = list(LEVELS[level_index]["map"])
    player = None
    exit_tile = None
    enemies = []
    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            if tile == "P":
                player = (x + 0.5, y + 0.5)
                rows[y] = row[:x] + "." + row[x + 1 :]
            elif tile == "X":
                exit_tile = (x + 0.5, y + 0.5)
                rows[y] = row[:x] + "." + row[x + 1 :]
            elif tile == "E":
                enemies.append({"x": x + 0.5, "y": y + 0.5, "hp": 3, "attack": 0.0})
                rows[y] = row[:x] + "." + row[x + 1 :]
    if player is None or exit_tile is None:
        raise ValueError(f"Level {level_index + 1} must have one player start and one exit")
    return rows, player, exit_tile, enemies


def is_wall(world_map: list[str], x: float, y: float) -> bool:
    cell_x, cell_y = int(x), int(y)
    return (
        cell_y < 0
        or cell_y >= len(world_map)
        or cell_x < 0
        or cell_x >= len(world_map[0])
        or world_map[cell_y][cell_x] == "#"
    )


def cast_ray(
    world_map: list[str], origin_x: float, origin_y: float, ray_angle: float
) -> tuple[float, float, int]:
    """Return wall distance, wall texture coordinate, and hit side."""
    ray_x = math.cos(ray_angle)
    ray_y = math.sin(ray_angle)
    cell_x, cell_y = int(origin_x), int(origin_y)
    delta_x = abs(1.0 / ray_x) if abs(ray_x) > 1e-10 else math.inf
    delta_y = abs(1.0 / ray_y) if abs(ray_y) > 1e-10 else math.inf
    step_x = 1 if ray_x >= 0 else -1
    step_y = 1 if ray_y >= 0 else -1
    side_x = (cell_x + 1 - origin_x) * delta_x if step_x > 0 else (origin_x - cell_x) * delta_x
    side_y = (cell_y + 1 - origin_y) * delta_y if step_y > 0 else (origin_y - cell_y) * delta_y

    for _ in range(128):
        if side_x < side_y:
            side_x += delta_x
            cell_x += step_x
            side = 0
        else:
            side_y += delta_y
            cell_y += step_y
            side = 1
        if (
            cell_y < 0
            or cell_y >= len(world_map)
            or cell_x < 0
            or cell_x >= len(world_map[0])
            or world_map[cell_y][cell_x] == "#"
        ):
            distance = max(0.001, side_x - delta_x if side == 0 else side_y - delta_y)
            hit = origin_y + distance * ray_y if side == 0 else origin_x + distance * ray_x
            return distance, hit - math.floor(hit), side
    return MAX_RAY_DISTANCE, 0.0, 0


def has_line_of_sight(world_map: list[str], x1: float, y1: float, x2: float, y2: float) -> bool:
    distance = math.hypot(x2 - x1, y2 - y1)
    steps = max(1, int(distance * 12))
    for step in range(1, steps):
        ratio = step / steps
        if is_wall(world_map, x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio):
            return False
    return True


def validate_levels() -> None:
    for index, level in enumerate(LEVELS):
        rows, player, exit_tile, enemies = parse_level(index)
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError(f"Level {index + 1} has inconsistent map dimensions")
        for x, y in (player, exit_tile):
            if is_wall(rows, x, y):
                raise ValueError(f"Level {index + 1} starts inside a wall")
        if not enemies:
            raise ValueError(f"Level {index + 1} needs at least one enemy")


def make_enemy_sprite() -> pygame.Surface:
    sprite = pygame.Surface((96, 112), pygame.SRCALPHA)
    pygame.draw.ellipse(sprite, (0, 0, 0, 100), (14, 91, 68, 15))
    pygame.draw.polygon(sprite, (74, 27, 24), [(26, 32), (9, 5), (41, 25)])
    pygame.draw.polygon(sprite, (74, 27, 24), [(70, 32), (87, 5), (55, 25)])
    pygame.draw.ellipse(sprite, (128, 43, 35), (20, 23, 56, 57))
    pygame.draw.ellipse(sprite, (183, 67, 47), (29, 33, 38, 35))
    pygame.draw.ellipse(sprite, (255, 210, 115), (34, 45, 9, 8))
    pygame.draw.ellipse(sprite, (255, 210, 115), (53, 45, 9, 8))
    pygame.draw.polygon(sprite, (36, 25, 26), [(46, 54), (41, 65), (51, 65)])
    pygame.draw.polygon(sprite, (130, 34, 27), [(31, 70), (65, 70), (81, 101), (15, 101)])
    pygame.draw.line(sprite, (196, 73, 54), (28, 77), (10, 96), 10)
    pygame.draw.line(sprite, (196, 73, 54), (68, 77), (86, 96), 10)
    pygame.draw.line(sprite, (48, 29, 28), (34, 95), (29, 110), 12)
    pygame.draw.line(sprite, (48, 29, 28), (62, 95), (67, 110), 12)
    return sprite


def make_exit_sprite() -> pygame.Surface:
    sprite = pygame.Surface((80, 112), pygame.SRCALPHA)
    pygame.draw.ellipse(sprite, (0, 0, 0, 100), (8, 98, 64, 12))
    pygame.draw.ellipse(sprite, (247, 177, 48), (10, 9, 60, 94))
    pygame.draw.ellipse(sprite, (92, 40, 155), (18, 17, 44, 78))
    pygame.draw.ellipse(sprite, (17, 19, 33), (25, 24, 30, 64))
    pygame.draw.arc(sprite, (255, 226, 132), (7, 7, 66, 99), 0.2, 2.9, 3)
    return sprite


class Hellbound:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("HELLBOUND")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 22, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 16, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 64, bold=True)
        self.enemy_sprite = make_enemy_sprite()
        self.exit_sprite = make_exit_sprite()
        self.level_index = 0
        self.state = "title"
        self.minimap = False
        self.message_timer = 0.0
        self.shot_cooldown = 0.0
        self.muzzle_timer = 0.0
        self.damage_flash = 0.0
        self.reset_game()

    def reset_game(self) -> None:
        self.level_index = 0
        self.health = 100
        self.load_level()
        self.state = "title"

    def load_level(self) -> None:
        self.world_map, position, self.exit_position, self.enemies = parse_level(self.level_index)
        self.player_x, self.player_y = position
        self.angle = 0.0
        self.message_timer = 2.5

    def set_playing(self, playing: bool) -> None:
        pygame.event.set_grab(playing)
        pygame.mouse.set_visible(not playing)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEMOTION and self.state == "playing":
                self.angle = normalize_angle(self.angle + event.rel[0] * 0.003)
            if event.type == pygame.KEYDOWN:
                if self.state == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = "playing"
                    self.set_playing(True)
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                        self.set_playing(False)
                    elif event.key == pygame.K_TAB:
                        self.minimap = not self.minimap
                    elif event.key == pygame.K_SPACE:
                        self.shoot()
                elif self.state == "paused":
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        self.state = "playing"
                        self.set_playing(True)
                    elif event.key == pygame.K_q:
                        return False
                elif self.state in ("dead", "won"):
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == "playing":
                self.shoot()
        return True

    def shoot(self) -> None:
        if self.shot_cooldown > 0:
            return
        self.shot_cooldown = 0.32
        self.muzzle_timer = 0.09
        best_enemy = None
        best_distance = 7.0
        for enemy in self.enemies:
            distance = math.hypot(enemy["x"] - self.player_x, enemy["y"] - self.player_y)
            target_angle = math.atan2(enemy["y"] - self.player_y, enemy["x"] - self.player_x)
            tolerance = 0.055 + 0.11 / max(1.0, distance)
            if (
                distance < best_distance
                and abs(normalize_angle(target_angle - self.angle)) < tolerance
                and has_line_of_sight(self.world_map, self.player_x, self.player_y, enemy["x"], enemy["y"])
            ):
                best_enemy = enemy
                best_distance = distance
        if best_enemy:
            best_enemy["hp"] -= 1
            if best_enemy["hp"] <= 0:
                self.enemies.remove(best_enemy)

    def move_player(self, delta_time: float) -> None:
        keys = pygame.key.get_pressed()
        forward = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(
            keys[pygame.K_s] or keys[pygame.K_DOWN]
        )
        strafe = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
        if forward == 0 and strafe == 0:
            return
        length = math.hypot(forward, strafe)
        forward /= length
        strafe /= length
        speed = 4.0 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 2.65
        move_x = (math.cos(self.angle) * forward - math.sin(self.angle) * strafe) * speed * delta_time
        move_y = (math.sin(self.angle) * forward + math.cos(self.angle) * strafe) * speed * delta_time
        radius = 0.22
        next_x = self.player_x + move_x
        if not any(
            is_wall(self.world_map, next_x + dx, self.player_y + dy)
            for dx, dy in ((-radius, -radius), (radius, -radius), (-radius, radius), (radius, radius))
        ):
            self.player_x = next_x
        next_y = self.player_y + move_y
        if not any(
            is_wall(self.world_map, self.player_x + dx, next_y + dy)
            for dx, dy in ((-radius, -radius), (radius, -radius), (-radius, radius), (radius, radius))
        ):
            self.player_y = next_y

    def update_enemies(self, delta_time: float) -> None:
        for enemy in self.enemies:
            dx = self.player_x - enemy["x"]
            dy = self.player_y - enemy["y"]
            distance = math.hypot(dx, dy)
            enemy["attack"] = max(0.0, enemy["attack"] - delta_time)
            if distance < 9.0 and distance > 1.05 and has_line_of_sight(
                self.world_map, enemy["x"], enemy["y"], self.player_x, self.player_y
            ):
                speed = 0.8 * delta_time
                next_x = enemy["x"] + dx / distance * speed
                next_y = enemy["y"] + dy / distance * speed
                if not is_wall(self.world_map, next_x, enemy["y"]):
                    enemy["x"] = next_x
                if not is_wall(self.world_map, enemy["x"], next_y):
                    enemy["y"] = next_y
            elif distance <= 1.05 and enemy["attack"] <= 0:
                self.health = max(0, self.health - 8)
                enemy["attack"] = 0.85
                self.damage_flash = 0.18
        if not self.enemies and math.hypot(
            self.exit_position[0] - self.player_x, self.exit_position[1] - self.player_y
        ) < 0.75:
            self.advance_level()

    def advance_level(self) -> None:
        self.set_playing(False)
        if self.level_index + 1 == len(LEVELS):
            self.state = "won"
            return
        self.level_index += 1
        self.load_level()

    def update(self, delta_time: float) -> None:
        self.shot_cooldown = max(0.0, self.shot_cooldown - delta_time)
        self.muzzle_timer = max(0.0, self.muzzle_timer - delta_time)
        self.damage_flash = max(0.0, self.damage_flash - delta_time)
        self.message_timer = max(0.0, self.message_timer - delta_time)
        if self.state != "playing":
            return
        self.move_player(delta_time)
        self.update_enemies(delta_time)
        if self.health <= 0:
            self.state = "dead"
            self.set_playing(False)

    def draw_world(self) -> None:
        horizon = SCREEN_HEIGHT // 2
        self.screen.fill((28, 31, 48))
        pygame.draw.rect(self.screen, (49, 43, 39), (0, horizon, SCREEN_WIDTH, horizon))
        z_buffer = [MAX_RAY_DISTANCE] * RAY_COUNT
        column_width = SCREEN_WIDTH / RAY_COUNT
        wall_color = LEVELS[self.level_index]["wall"]
        for column in range(RAY_COUNT):
            camera = (2.0 * (column + 0.5) / RAY_COUNT) - 1.0
            ray_angle = self.angle + math.atan(camera * math.tan(FOV / 2))
            raw_distance, texture, side = cast_ray(
                self.world_map, self.player_x, self.player_y, ray_angle
            )
            distance = max(0.05, raw_distance * math.cos(ray_angle - self.angle))
            z_buffer[column] = distance
            wall_height = min(SCREEN_HEIGHT * 2, int(SCREEN_HEIGHT / distance))
            top = max(0, horizon - wall_height // 2)
            bottom = min(SCREEN_HEIGHT, horizon + wall_height // 2)
            shade = max(0.2, 1.0 - distance / MAX_RAY_DISTANCE)
            stripe = 0.72 if int(texture * 12) % 2 == 0 else 1.0
            if side:
                stripe *= 0.72
            color = tuple(int(channel * shade * stripe) for channel in wall_color)
            x = int(column * column_width)
            width = max(1, math.ceil(column_width))
            pygame.draw.rect(self.screen, color, (x, top, width, bottom - top))
            if wall_height > 18 and int(texture * 12) % 6 == 0:
                pygame.draw.line(self.screen, (22, 20, 24), (x, top), (x, bottom), 1)
        self.draw_billboards(z_buffer)
        self.draw_weapon()
        self.draw_hud()
        if self.minimap:
            self.draw_minimap()

    def draw_billboard(
        self, sprite: pygame.Surface, world_x: float, world_y: float, z_buffer: list[float]
    ) -> None:
        dx = world_x - self.player_x
        dy = world_y - self.player_y
        distance = math.hypot(dx, dy)
        relative_angle = normalize_angle(math.atan2(dy, dx) - self.angle)
        if distance < 0.2 or abs(relative_angle) > FOV * 0.72:
            return
        screen_x = SCREEN_WIDTH / 2 + math.tan(relative_angle) * (
            SCREEN_WIDTH / 2 / math.tan(FOV / 2)
        )
        height = min(SCREEN_HEIGHT * 1.4, SCREEN_HEIGHT / distance * 0.82)
        width = height * sprite.get_width() / sprite.get_height()
        scaled = pygame.transform.smoothscale(sprite, (max(1, int(width)), max(1, int(height))))
        left = int(screen_x - width / 2)
        top = int(SCREEN_HEIGHT / 2 - height / 2)
        first_column = max(0, left)
        last_column = min(SCREEN_WIDTH, left + int(width))
        for screen_column in range(first_column, last_column):
            ray_column = min(RAY_COUNT - 1, int(screen_column / SCREEN_WIDTH * RAY_COUNT))
            if distance >= z_buffer[ray_column]:
                continue
            source_x = min(scaled.get_width() - 1, screen_column - left)
            strip = scaled.subsurface((source_x, 0, 1, scaled.get_height()))
            self.screen.blit(strip, (screen_column, top))

    def draw_billboards(self, z_buffer: list[float]) -> None:
        objects = [(enemy["x"], enemy["y"], self.enemy_sprite) for enemy in self.enemies]
        if not self.enemies:
            objects.append((self.exit_position[0], self.exit_position[1], self.exit_sprite))
        objects.sort(
            key=lambda item: math.hypot(item[0] - self.player_x, item[1] - self.player_y),
            reverse=True,
        )
        for x, y, sprite in objects:
            self.draw_billboard(sprite, x, y, z_buffer)

    def draw_weapon(self) -> None:
        center = SCREEN_WIDTH // 2
        pygame.draw.polygon(
            self.screen, (42, 42, 48),
            [(center - 115, SCREEN_HEIGHT), (center - 83, 510), (center + 70, 510),
             (center + 120, SCREEN_HEIGHT)],
        )
        pygame.draw.rect(self.screen, (75, 75, 81), (center - 40, 467, 80, 105), border_radius=12)
        pygame.draw.rect(self.screen, (35, 36, 42), (center - 21, 438, 42, 72), border_radius=5)
        pygame.draw.rect(self.screen, (112, 108, 91), (center - 12, 435, 24, 42))
        if self.muzzle_timer > 0:
            pygame.draw.polygon(
                self.screen, (255, 223, 126),
                [(center, 418), (center - 27, 451), (center - 7, 447),
                 (center, 465), (center + 8, 446), (center + 29, 451)],
            )
            pygame.draw.circle(self.screen, (255, 246, 199), (center, 447), 9)

    def draw_hud(self) -> None:
        panel = pygame.Rect(0, SCREEN_HEIGHT - 54, SCREEN_WIDTH, 54)
        pygame.draw.rect(self.screen, (16, 17, 21), panel)
        pygame.draw.line(self.screen, (121, 93, 56), (0, panel.top), (SCREEN_WIDTH, panel.top), 2)
        self.draw_text(f"HP {self.health:03}", 24, panel.top + 15, (227, 79, 65))
        self.draw_text(f"LEVEL {self.level_index + 1}/2", 180, panel.top + 15, (225, 199, 130))
        self.draw_text(f"DEMONS {len(self.enemies)}", 380, panel.top + 15, (223, 217, 194))
        hint = "FIND THE EXIT" if self.enemies else "EXIT OPEN - FIND THE PORTAL"
        self.draw_text(hint, 620, panel.top + 15, (224, 196, 118))
        if self.message_timer > 0:
            self.draw_center_text(LEVELS[self.level_index]["name"], 72, self.font, (247, 213, 149))
        if self.damage_flash > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(flash, (180, 0, 0, 62), flash.get_rect())
            self.screen.blit(flash, (0, 0))

    def draw_minimap(self) -> None:
        tile_size = 10
        origin_x, origin_y = 18, 18
        background = pygame.Rect(origin_x - 4, origin_y - 4, len(self.world_map[0]) * tile_size + 8,
                                 len(self.world_map) * tile_size + 8)
        pygame.draw.rect(self.screen, (11, 12, 16), background)
        for y, row in enumerate(self.world_map):
            for x, cell in enumerate(row):
                color = (96, 72, 66) if cell == "#" else (35, 37, 43)
                pygame.draw.rect(self.screen, color, (origin_x + x * tile_size, origin_y + y * tile_size,
                                                     tile_size - 1, tile_size - 1))
        if not self.enemies:
            pygame.draw.rect(
                self.screen, (255, 200, 66),
                (origin_x + int(self.exit_position[0] * tile_size) - 3,
                 origin_y + int(self.exit_position[1] * tile_size) - 3, 7, 7),
            )
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, (230, 58, 48),
                               (origin_x + int(enemy["x"] * tile_size),
                                origin_y + int(enemy["y"] * tile_size)), 3)
        player_pos = (origin_x + int(self.player_x * tile_size),
                      origin_y + int(self.player_y * tile_size))
        pygame.draw.circle(self.screen, (110, 232, 145), player_pos, 3)
        pygame.draw.line(self.screen, (110, 232, 145), player_pos,
                         (player_pos[0] + int(math.cos(self.angle) * 8),
                          player_pos[1] + int(math.sin(self.angle) * 8)), 2)

    def draw_text(
        self, text: str, x: int, y: int, color: tuple[int, int, int], font: pygame.font.Font | None = None
    ) -> None:
        rendered = (font or self.small_font).render(text, True, color)
        self.screen.blit(rendered, (x, y))

    def draw_center_text(
        self, text: str, y: int, font: pygame.font.Font, color: tuple[int, int, int]
    ) -> None:
        rendered = font.render(text, True, color)
        self.screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, y))

    def draw_overlay(self, title: str, subtitle: str, footer: str) -> None:
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((8, 9, 15, 208))
        self.screen.blit(shade, (0, 0))
        self.draw_center_text(title, 188, self.title_font, (208, 58, 43))
        self.draw_center_text(subtitle, 285, self.font, (236, 216, 167))
        self.draw_center_text(footer, 365, self.small_font, (202, 202, 196))

    def draw(self) -> None:
        if self.state == "title":
            self.draw_world()
            self.draw_overlay("HELLBOUND", "A two-level retro FPS", "ENTER TO START  |  WASD MOVE  |  MOUSE LOOK")
            self.draw_center_text("SPACE / CLICK TO FIRE   |   SHIFT RUN   |   TAB MAP   |   ESC PAUSE",
                                  408, self.small_font, (183, 183, 179))
        elif self.state in ("playing", "paused", "dead", "won"):
            self.draw_world()
            if self.state == "paused":
                self.draw_overlay("PAUSED", "The demons are waiting...", "ENTER / ESC TO RESUME  |  Q QUIT")
            elif self.state == "dead":
                self.draw_overlay("YOU DIED", "The underworld claims another soul", "R RESTART  |  Q QUIT")
            elif self.state == "won":
                self.draw_overlay("YOU SURVIVED", "The portals are sealed. For now.", "R PLAY AGAIN  |  Q QUIT")
        pygame.display.flip()

    def run(self) -> None:
        self.set_playing(False)
        while self.handle_events():
            delta_time = min(self.clock.tick(60) / 1000.0, 0.05)
            self.update(delta_time)
            self.draw()
        self.set_playing(False)
        pygame.quit()


def self_test() -> None:
    validate_levels()
    rows, player, _, _ = parse_level(0)
    distance, _, _ = cast_ray(rows, player[0], player[1], 0.0)
    if not math.isfinite(distance) or distance <= 0:
        raise AssertionError("Ray caster did not return a valid wall distance")
    print(f"OK: {len(LEVELS)} levels validated; ray casting is working.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hellbound, a two-level retro FPS.")
    parser.add_argument("--self-test", action="store_true", help="validate the maps and ray caster, then exit")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    Hellbound().run()


if __name__ == "__main__":
    main()
