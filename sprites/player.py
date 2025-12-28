import pygame
from settings import TILE_SIZE, GRAVITY, PLAYER_SPEED, JUMP_STRENGTH, BOOST_JUMP_STRENGTH, resource_path

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.facing_right = True
        self.is_dead = False
        self.on_ground = False
        
        # Load slices (Width 96px, Height 128px)
        self.run_frames = self._load_run_frames("assets/sprites/only_run.png", 6)
        
        self.image = self.run_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Use Vector2 for precise movement, avoiding integer rounding jitter
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)

    def _load_run_frames(self, path, count):
        frames = []
        try:
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            f_w, f_h, spacing = 96, 128, 32
            for i in range(count):
                x_pos = i * (f_w + spacing)
                frame = sheet.subsurface((x_pos, 0, f_w, f_h))
                # Scale to fit game (Width ~0.8 tiles, Height ~1.2 tiles)
                frame = pygame.transform.scale(frame, (int(TILE_SIZE * 0.8), int(TILE_SIZE * 1.2)))
                frames.append(frame)
        except:
            surf = pygame.Surface((32, 48))
            surf.fill((0, 0, 255))
            frames = [surf]
        return frames

    def _animate(self):
        # Ensure self.image has a value even if not moving
        if self.vel.x != 0 and self.on_ground:
            self.frame_index += self.animation_speed
        else:
            # Fix to frame 0 when idle
            self.frame_index = 0
            
        if self.frame_index >= len(self.run_frames):
            self.frame_index = 0
        
        # Update image
        img = self.run_frames[int(self.frame_index)]
        self.image = pygame.transform.flip(img, True, False) if not self.facing_right else img

    def update(self, walls, hazards, bouncers,has_shield, *args, **kwargs):
        self._get_input()
        self._apply_gravity()

        # Separate X and Y movement and collision to prevent diagonal wall clipping
        # 1. X Axis
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self._collide_with_walls(walls, 'x')

        # 2. Y Axis
        self.on_ground = False # Reset every frame, confirmed by collision detection
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self._collide_with_walls(walls, 'y')

        self._animate()

        if self._check_lethal(hazards) and not has_shield:
            self.is_dead = True
        self._check_bouncers(bouncers)

    def _get_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
            self.facing_right = True
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = JUMP_STRENGTH
            self.on_ground = False

    def _apply_gravity(self):
        self.vel.y += GRAVITY
        if self.vel.y > 10: self.vel.y = 10

    def _collide_with_walls(self, walls, direction):
        for wall in walls:
            if self.rect.colliderect(wall):
                if direction == 'x':
                    if self.vel.x > 0: self.rect.right = wall.left
                    if self.vel.x < 0: self.rect.left = wall.right
                    self.pos.x = self.rect.x
                    self.vel.x = 0
                if direction == 'y':
                    if self.vel.y > 0:
                        self.rect.bottom = wall.top
                        self.on_ground = True
                    if self.vel.y < 0:
                        self.rect.top = wall.bottom
                    self.pos.y = self.rect.y
                    self.vel.y = 0

    def _check_lethal(self, hazards):
        return any(self.rect.colliderect(h) for h in hazards)

    def _check_bouncers(self, bouncers):
        if self.vel.y > 0:
            for b in bouncers:
                if self.rect.colliderect(b) and (self.rect.bottom - self.vel.y) <= b.top:
                    self.vel.y = BOOST_JUMP_STRENGTH
                    self.rect.bottom = b.top
                    self.pos.y = self.rect.y
                    self.on_ground = False