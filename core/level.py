import pygame
import math
import random
from settings import WIDTH, HEIGHT

class LvSelect:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont("Verdana", 80, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 32, bold=True)
        self.tip_font = pygame.font.SysFont("Consolas", 20)

        self.buttons = []
        self.time = 0

        self.particles = []
        for _ in range(18):
            self.particles.append({
                "pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
                "size": random.randint(40, 100),
                "speed": random.uniform(0.5, 1.2),
                "angle": random.uniform(0, 360),
                "rot_speed": random.uniform(0.2, 0.6),
                "color": (40, 90, 70)
            })

        self.scanners = []
        for _ in range(4):
            self.scanners.append({
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(2.0, 4.0),
                "alpha": random.randint(60, 120)
            })

        for i in range(1, 6):
            rect = pygame.Rect(WIDTH // 2 - 120, 240 + (i - 1) * 85, 240, 65)
            self.buttons.append({
                "rect": rect, "lv_num": i, "name": f"MISSION {i}",
                "scale": 1.0, "target_scale": 1.0
            })

    def _draw_cool_background(self):
        self.screen.fill((3, 5, 10)) 

        grid_color = (25, 45, 35)
        for x in range(0, WIDTH, 50):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(self.screen, grid_color, (0, y), (WIDTH, y), 1)

        for p in self.particles:
            p["pos"][1] -= p["speed"]
            p["angle"] += p["rot_speed"]
            if p["pos"][1] < -p["size"]:
                p["pos"][1] = HEIGHT + p["size"]

            points = []
            for j in range(3):
                ang = math.radians(p["angle"] + j * 120)
                px = p["pos"][0] + math.cos(ang) * (p["size"] // 2)
                py = p["pos"][1] + math.sin(ang) * (p["size"] // 2)
                points.append((px, py))
            pygame.draw.polygon(self.screen, p["color"], points, 2)

        for s in self.scanners:
            s["y"] += s["speed"]
            if s["y"] > HEIGHT: s["y"] = -10

            line_surf = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
            line_surf.fill((60, 150, 100, s["alpha"])) 
            self.screen.blit(line_surf, (0, int(s["y"])))

    def draw(self):
        self.time += 1
        self._draw_cool_background()

        title_text = "Dark Nigg...nja"
        title_pos = (WIDTH // 2, 110)

        for i in range(4, 0, -1):
            glow_surf = self.title_font.render(title_text, True, (30, 90, 60))
            self.screen.blit(glow_surf, glow_surf.get_rect(center=(title_pos[0] + i, title_pos[1] + i)))

        main_title = self.title_font.render(title_text, True, (220, 255, 230))
        self.screen.blit(main_title, main_title.get_rect(center=title_pos))


        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            is_hover = btn["rect"].collidepoint(mouse_pos)
            btn["target_scale"] = 1.12 if is_hover else 1.0
            btn["scale"] += (btn["target_scale"] - btn["scale"]) * 0.15

            w, h = 240 * btn["scale"], 65 * btn["scale"]
            draw_rect = pygame.Rect(0, 0, w, h)
            draw_rect.center = btn["rect"].center

            if is_hover:
                bg_color = (45, 180, 110)
                border_color = (200, 255, 220)
                pygame.draw.rect(self.screen, (50, 120, 80), draw_rect.inflate(8, 8), 2, border_radius=4)
            else:
                bg_color = (25, 55, 40)
                border_color = (80, 140, 110)

            pygame.draw.rect(self.screen, bg_color, draw_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, draw_rect, 2 if is_hover else 1, border_radius=4)

            txt_surf = self.btn_font.render(btn["name"], True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))

        pygame.draw.line(self.screen, (80, 200, 120), (WIDTH // 4, HEIGHT - 75), (3 * WIDTH // 4, HEIGHT - 75), 3)

        controls_text = "A/D: MOVE  |  W/SPACE: JUMP  |  Esc: PAUSE  |  R: RESET  |  CLICK MISSION"
        tip_surf = self.tip_font.render(controls_text, True, (130, 170, 150))
        self.screen.blit(tip_surf, tip_surf.get_rect(center=(WIDTH // 2, HEIGHT - 45)))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    return btn["lv_num"]
        return None