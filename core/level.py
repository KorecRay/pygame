import pygame
import math
import random
from settings import WIDTH, HEIGHT


class LvSelect:
    def __init__(self, screen):
        self.screen = screen
        # Hardcore font style
        self.title_font = pygame.font.SysFont("Verdana", 80, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 32, bold=True)
        self.tip_font = pygame.font.SysFont("Consolas", 20)

        self.buttons = []
        self.time = 0

        # --- Background Geometry ---
        self.particles = []
        for _ in range(15):
            self.particles.append({
                "pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
                "size": random.randint(30, 80),
                "speed": random.uniform(0.3, 1.0),
                "angle": random.uniform(0, 360),
                "rot_speed": random.uniform(0.2, 0.6),
                "color": (20, 50, 40)  # Subtle dark green
            })

        # --- Scanlines ---
        self.scanners = []
        for _ in range(4):
            self.scanners.append({
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(1.5, 3.5),
                "alpha": random.randint(20, 60)
            })

        # Init buttons
        for i in range(1, 6):
            rect = pygame.Rect(WIDTH // 2 - 120, 240 + (i - 1) * 85, 240, 65)
            self.buttons.append({
                "rect": rect, "lv_num": i, "name": f"MISSION {i}",
                "scale": 1.0, "target_scale": 1.0
            })

    def _draw_cool_background(self):
        """Enhanced background: Static grid & dynamic flow."""
        self.screen.fill((5, 7, 12))  # Very dark base

        # 1. Static Grid
        for x in range(0, WIDTH, 50):
            pygame.draw.line(self.screen, (10, 20, 15), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(self.screen, (10, 20, 15), (0, y), (WIDTH, y), 1)

        # 2. Slow moving geometry (Wireframe feel)
        for p in self.particles:
            p["pos"][1] -= p["speed"]
            p["angle"] += p["rot_speed"]
            if p["pos"][1] < -p["size"]:
                p["pos"][1] = HEIGHT + p["size"]

            # Draw triangle wireframe
            points = []
            for j in range(3):
                ang = math.radians(p["angle"] + j * 120)
                px = p["pos"][0] + math.cos(ang) * (p["size"] // 2)
                py = p["pos"][1] + math.sin(ang) * (p["size"] // 2)
                points.append((px, py))
            pygame.draw.polygon(self.screen, p["color"], points, 1)

        # 3. Horizontal Scanlines (Energy flow)
        for s in self.scanners:
            s["y"] += s["speed"]
            if s["y"] > HEIGHT: s["y"] = -10

            # Draw gradient scanline
            line_surf = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
            line_surf.fill((40, 100, 70, s["alpha"]))
            self.screen.blit(line_surf, (0, int(s["y"])))

    def draw(self):
        self.time += 1
        self._draw_cool_background()

        # 1. Title: Static with steady glow
        title_text = "Dark Ning...ja"
        title_pos = (WIDTH // 2, 110)

        # Layered glow
        for i in range(3, 0, -1):
            glow_surf = self.title_font.render(title_text, True, (20, 60, 40))
            self.screen.blit(glow_surf, glow_surf.get_rect(center=(title_pos[0] + i, title_pos[1] + i)))

        main_title = self.title_font.render(title_text, True, (220, 255, 230))
        self.screen.blit(main_title, main_title.get_rect(center=title_pos))

        # 2. Button Logic
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            is_hover = btn["rect"].collidepoint(mouse_pos)
            btn["target_scale"] = 1.12 if is_hover else 1.0
            btn["scale"] += (btn["target_scale"] - btn["scale"]) * 0.15

            w, h = 240 * btn["scale"], 65 * btn["scale"]
            draw_rect = pygame.Rect(0, 0, w, h)
            draw_rect.center = btn["rect"].center

            # Button color & gloss
            if is_hover:
                bg_color = (45, 180, 110)
                border_color = (200, 255, 220)
                # Extra border on hover
                pygame.draw.rect(self.screen, (30, 80, 50), draw_rect.inflate(6, 6), 2, border_radius=4)
            else:
                bg_color = (20, 40, 30)
                border_color = (60, 100, 80)

            pygame.draw.rect(self.screen, bg_color, draw_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, draw_rect, 1, border_radius=4)

            txt_surf = self.btn_font.render(btn["name"], True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))

        # 3. Footer & Tips (Static)
        pygame.draw.line(self.screen, (60, 150, 100), (WIDTH // 4, HEIGHT - 75), (3 * WIDTH // 4, HEIGHT - 75), 2)

        controls_text = "A/D: MOVE  |  W/SPACE: JUMP  |  Esc: PAUSE  |  R: RESET  |  CLICK MISSION"
        tip_surf = self.tip_font.render(controls_text, True, (100, 130, 115))
        self.screen.blit(tip_surf, tip_surf.get_rect(center=(WIDTH // 2, HEIGHT - 45)))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    return btn["lv_num"]
        return None