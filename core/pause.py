import pygame
from settings import WIDTH, HEIGHT


class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Verdana", 50, bold=True)
        self.btn_font = pygame.font.SysFont("Verdana", 30, bold=True)

        # Define buttons
        self.resume_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 40, 240, 60)
        self.menu_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 50, 240, 60)

    def draw(self):
        # 1. Draw semi-transparent overlay to darken game screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 2. Draw "PAUSED" text
        title_surf = self.font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

        # 3. Draw buttons
        mouse_pos = pygame.mouse.get_pos()

        for rect, text, color in [
            (self.resume_rect, "RESUME", (45, 180, 110)),
            (self.menu_rect, "MAIN MENU", (180, 45, 45))
        ]:
            is_hover = rect.collidepoint(mouse_pos)
            # Highlight on hover
            draw_color = [min(c + 40, 255) if is_hover else c for c in color]

            pygame.draw.rect(self.screen, draw_color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)

            txt_surf = self.btn_font.render(text, True, (255, 255, 255))
            self.screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    def handle_input(self, event):
        """Returns state string to tell main.py what to do"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.resume_rect.collidepoint(event.pos):
                return "RESUME"
            if self.menu_rect.collidepoint(event.pos):
                return "MAIN_MENU"
        return None