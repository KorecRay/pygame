import pygame
from settings import TILE_SIZE, resource_path

GRAVITY = 0.7


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range, speed):
        super().__init__()

        # --- Animation Settings ---
        self.frame_index = 0
        self.animation_speed = 0.15  # Smaller number = slower animation
        self.state = "run"  # Initial state
        self.facing_right = True  # Facing direction

        # Load and slice images (assuming paths below)
        self.animations = {
            "idle": self._load_frames("assets/sprites/enemy_idle.png", 4),
            "run": self._load_frames("assets/sprites/enemy_run.png", 6)
        }

        # Set initial image
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Physics and Movement
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.start_x = x
        self.move_range = move_range
        self.speed = speed
        self.direction = 1
        self.is_dead = False

    def _load_frames(self, path, frame_count):
        """Helper to slice spritesheet."""
        frames = []
        try:
            sheet = pygame.image.load(resource_path(path)).convert_alpha()
            for i in range(frame_count):
                # Each action is 32x32, sliced horizontally
                frame = sheet.subsurface((i * 32, 0, 32, 32))
                # Scale if TILE_SIZE is not 32
                if TILE_SIZE != 32:
                    frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                frames.append(frame)
        except Exception as e:
            print(f"Animation load error {path}: {e}")
            # Fallback: Red square
            dummy = pygame.Surface((TILE_SIZE, TILE_SIZE))
            dummy.fill((255, 0, 0))
            frames = [dummy]
        return frames

    def _animate(self):
        """Handle frame switching and flipping."""
        animation = self.animations[self.state]

        # Increment index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Get current frame
        current_frame = animation[int(self.frame_index)]

        # 🚨 Handle flipping
        # Flip if direction is -1 and currently facing right
        if self.direction < 0:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame

    def update(self, walls, *args, **kwargs):
        """
        Accepts *args to prevent errors,
        Fixes previous TypeError: Enemy.update() takes 2 positional arguments but 4 were given
        """
        if self.is_dead:
            return

        self._apply_gravity()
        self._patrol_move()

        # Determine state based on speed
        self.state = "run" if self.vel.x != 0 else "idle"

        # Execute X/Y movement
        self.rect.x = int(self.pos.x + self.vel.x)
        self._collide_and_resolve_x(walls)
        self.rect.y = int(self.pos.y + self.vel.y)
        self._collide_and_resolve_y(walls)

        self.pos.x = self.rect.x
        self.pos.y = self.rect.y

        # Update animation
        self._animate()

    # --- _apply_gravity, _patrol_move, _collide_and_resolve logic remains same ---
    def _apply_gravity(self):
        self.vel.y += GRAVITY
        if self.vel.y > 10: self.vel.y = 10

    def _patrol_move(self):
        self.vel.x = self.direction * self.speed
        current_center_x = self.pos.x + self.rect.width / 2
        if current_center_x <= self.start_x - self.move_range / 2:
            self.direction = 1
        elif current_center_x >= self.start_x + self.move_range / 2:
            self.direction = -1

    def _collide_and_resolve_x(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                self.direction *= -1
                if self.direction > 0:
                    self.rect.right = wall.left
                else:
                    self.rect.left = wall.right
                break

    def _collide_and_resolve_y(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel.y > 0:
                    self.rect.bottom = wall.top
                else:
                    self.rect.top = wall.bottom
                self.vel.y = 0
                break

    def explode(self):
        pass
        # self.is_dead = True
        # self.kill()