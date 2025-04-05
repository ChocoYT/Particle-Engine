import pygame

from typing import Union

number = Union[int, float]

class Particle(pygame.sprite.Sprite):
    def __init__(self, environment, x: number, y: number, size: number, color: tuple[number]) -> None:
        super().__init__()
        
        self.environment = environment
        self.environment.particles.add(self)
        
        self.x,  self.y  = x, y
        self.vx, self.vy = 0, 0
        
        self.color  = color
        self.size   = size
        self.radius = self.size / 2
        
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        
        self.update()
        self.draw(environment.screen)
        
    def move(self) -> None:
        # Apply Gravity
        gravity = self.environment.gravity
        gravityDirection = self.environment.gravityDirection
        
        self.vx += gravity * gravityDirection.x
        self.vy += gravity * gravityDirection.y
        
        # Apply Drag Forces
        airResistance = self.environment.airResistance
        
        self.vx *= airResistance
        self.vy *= airResistance
        
        # Update Position
        self.x += self.vx
        self.y += self.vy
        
        self.wallCollide()
        
    def update(self) -> None:
        self.rect.center = self.x, self.y
    
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect.topleft)
        
    def getDistVector(self, particle) -> pygame.Vector2:
        return pygame.Vector2(particle.x - self.x, particle.y - self.y)
    
    def getDist(self, particle) -> float:
        return self.getDistVector(particle).magnitude()
    
    def isColliding(self, particles) -> bool:
        if isinstance(particles, Particle):  particles = {particles}
        
        for particle in set(particles):
            if particle is self:  continue
            if self.getDist(particle) <= self.radius + particle.radius:  return True
            
        return False
    
    def wallCollide(self) -> None:
        screenWidth, screenHeight = self.environment.screenWidth, self.environment.screenHeight
        energyLoss = self.environment.energyLoss
        
        # Left & Right Wall Collision
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -energyLoss
        elif self.x > screenWidth - self.radius:
            self.x = screenWidth - self.radius
            self.vx *= -energyLoss
        
        # Top & Bottom Wall Collision
        if self.y < self.radius:
            self.y = self.radius
            self.vy *= -energyLoss
        elif self.y > screenHeight - self.radius:
            self.y = screenHeight - self.radius
            self.vy *= -energyLoss
