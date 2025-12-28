import pygame

class Debugger:
    @staticmethod
    def draw_hitboxes(screen, player, enemies, props_group, dest_group, map_handler):
        # 1. Player (Green)
        if player:
            pygame.draw.rect(screen, (0, 255, 0), player.rect, 2)
        
        # 2. Enemies (Red)
        for e in enemies:
            pygame.draw.rect(screen, (255, 0, 0), e.rect, 2)
        
        # 3. Props (Yellow)
        for p in props_group:
            pygame.draw.rect(screen, (255, 255, 0), p.rect, 2)
        
        # 4. Destination (Cyan)
        for d in dest_group:
            pygame.draw.rect(screen, (0, 255, 255), d.rect, 2)

        # 5. Walls (Pink)
        for wall in map_handler.walls:
            pygame.draw.rect(screen, (200, 100, 200), wall, 1)
        
        # 6. Hazards (Orange)
        for hazard in map_handler.hazards:
            pygame.draw.rect(screen, (255, 165, 0), hazard, 1)

        # 7. Bouncers (Blue)
        for bouncer in map_handler.bouncers:
            pygame.draw.rect(screen, (0, 0, 255), bouncer, 1)