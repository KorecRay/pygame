import pygame
import math
import random
from settings import WIDTH, HEIGHT


class LvSelect:
    def __init__(self, screen):
        self.screen = screen
        # 使用更硬派的字體感
        self.title_font = pygame.font.SysFont("Verdana", 80, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 32, bold=True)
        self.tip_font = pygame.font.SysFont("Consolas", 20)

        self.buttons = []
        self.time = 0

        # --- 背景幾何元素 ---
        self.particles = []
        for _ in range(15):
            self.particles.append({
                "pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
                "size": random.randint(30, 80),
                "speed": random.uniform(0.3, 1.0),
                "angle": random.uniform(0, 360),
                "rot_speed": random.uniform(0.2, 0.6),
                "color": (20, 50, 40)  # 隱約的深綠色
            })

        # --- 掃描線元素 ---
        self.scanners = []
        for _ in range(4):
            self.scanners.append({
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(1.5, 3.5),
                "alpha": random.randint(20, 60)
            })

        # 初始化按鈕
        for i in range(1, 6):
            rect = pygame.Rect(WIDTH // 2 - 120, 240 + (i - 1) * 85, 240, 65)
            self.buttons.append({
                "rect": rect, "lv_num": i, "name": f"MISSION {i}",
                "scale": 1.0, "target_scale": 1.0
            })

    def _draw_cool_background(self):
        """背景加強：靜態網格與動態流光"""
        self.screen.fill((5, 7, 12))  # 極深底色

        # 1. 靜態背景網格 (增加結構感)
        for x in range(0, WIDTH, 50):
            pygame.draw.line(self.screen, (10, 20, 15), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(self.screen, (10, 20, 15), (0, y), (WIDTH, y), 1)

        # 2. 緩慢移動的幾何體 (線框感)
        for p in self.particles:
            p["pos"][1] -= p["speed"]
            p["angle"] += p["rot_speed"]
            if p["pos"][1] < -p["size"]:
                p["pos"][1] = HEIGHT + p["size"]

            # 繪製三角形線框
            points = []
            for j in range(3):
                ang = math.radians(p["angle"] + j * 120)
                px = p["pos"][0] + math.cos(ang) * (p["size"] // 2)
                py = p["pos"][1] + math.sin(ang) * (p["size"] // 2)
                points.append((px, py))
            pygame.draw.polygon(self.screen, p["color"], points, 1)

        # 3. 橫向掃描線 (能量流動感)
        for s in self.scanners:
            s["y"] += s["speed"]
            if s["y"] > HEIGHT: s["y"] = -10

            # 畫出一條漸變感的掃描線
            line_surf = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
            line_surf.fill((40, 100, 70, s["alpha"]))
            self.screen.blit(line_surf, (0, int(s["y"])))

    def draw(self):
        self.time += 1
        self._draw_cool_background()

        # 1. 標題：維持不動，增加沉穩的發光感
        title_text = "SHADOW RUNNER"
        title_pos = (WIDTH // 2, 110)

        # 固定層次發光
        for i in range(3, 0, -1):
            glow_surf = self.title_font.render(title_text, True, (20, 60, 40))
            self.screen.blit(glow_surf, glow_surf.get_rect(center=(title_pos[0] + i, title_pos[1] + i)))

        main_title = self.title_font.render(title_text, True, (220, 255, 230))
        self.screen.blit(main_title, main_title.get_rect(center=title_pos))

        # 2. 按鈕邏輯
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            is_hover = btn["rect"].collidepoint(mouse_pos)
            btn["target_scale"] = 1.12 if is_hover else 1.0
            btn["scale"] += (btn["target_scale"] - btn["scale"]) * 0.15

            w, h = 240 * btn["scale"], 65 * btn["scale"]
            draw_rect = pygame.Rect(0, 0, w, h)
            draw_rect.center = btn["rect"].center

            # 按鈕顏色與光澤
            if is_hover:
                bg_color = (45, 180, 110)
                border_color = (200, 255, 220)
                # Hover 時的額外外框
                pygame.draw.rect(self.screen, (30, 80, 50), draw_rect.inflate(6, 6), 2, border_radius=4)
            else:
                bg_color = (20, 40, 30)
                border_color = (60, 100, 80)

            pygame.draw.rect(self.screen, bg_color, draw_rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, draw_rect, 1, border_radius=4)

            txt_surf = self.btn_font.render(btn["name"], True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))

        # 3. 底部裝飾與說明 (固定不動)
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