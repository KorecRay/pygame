import pygame
from settings import WIDTH, HEIGHT

class LvSelect:
    def __init__(self, screen):
        self.screen = screen
        # 確保系統有字體，否則用預設
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.buttons = []
        
        # 建立 5 個 lv 按鈕 (垂直排列)
        for i in range(1, 6):
            rect = pygame.Rect(WIDTH // 2 - 100, 120 + (i-1) * 80, 200, 60)
            self.buttons.append({"rect": rect, "lv_num": i, "name": f"Level {i}"})

    def draw(self):
        self.screen.fill((15, 15, 25)) # 極深藍背景
        title = self.font.render("CHOOSE YOUR MISSION", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            # 懸停效果
            is_hover = btn["rect"].collidepoint(mouse_pos)
            color = (80, 200, 120) if is_hover else (40, 100, 60) # 忍者風綠色
            
            pygame.draw.rect(self.screen, color, btn["rect"], border_radius=12)
            pygame.draw.rect(self.screen, (200, 200, 200), btn["rect"], 2, border_radius=12)
            
            txt = self.font.render(btn["name"], True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=btn["rect"].center))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    return btn["lv_num"]
        return None