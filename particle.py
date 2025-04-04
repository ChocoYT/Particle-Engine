import pygame
from configobj import ConfigObj
from typing import Union
from os import getcwd

number = Union[int, float]

# Load Config File
path = getcwd()
defaults = ConfigObj(f'{path}\\defaults.ini')

# Variable Initialisation
screenWidth  = int(defaults['screen']['width'])
screenHeight = int(defaults['screen']['height'])

gravity       = float(defaults['constants']['gravity'])
airResistance = float(defaults['constants']['air_resistance'])

class Particle(pygame.sprite.Sprite):
    def __init__(self, x: number, y: number, size: number, color: tuple[number]) -> None:
        super().__init__()
        
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
        
        particleGroup.add(self)
        
    def move(self) -> None:
        # Apply Gravity
        self.vy -= gravity
        
        # Apply Drag Forces
        self.vx *= airResistance
        self.vy *= airResistance
        
        # Update Position
        self.x += self.vx
        self.y -= self.vy
        
        self.wallCollide()
        
    def update(self) -> None:
        self.rect.center = self.x, self.y
    
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect.topleft)
        
    def getDistanceVector(self, particle) -> pygame.Vector2:
        return pygame.Vector2(particle.x - self.x, particle.y - self.y)
    
    def getDistance(self, particle) -> float:
        return self.getDistanceVector(particle).magnitude()
    
    def isColliding(self, particles) -> bool:
        if isinstance(particles, Particle):  particles = {particles}
        
        for particle in set(particles):
            if particle is self:  continue
            if self.getDistance(particle) <= self.radius + particle.radius:  return True
            
        return False
    
    def resolveCollisions(self) -> None:
        for particle in particleGroup:
            if particle is self:  continue

            # Calculate Distance between Particles
            distanceVector = self.getDistanceVector(particle)
            distance = distanceVector.magnitude()

            min_distance = self.radius + particle.radius

            if self.isColliding(particle):
                distanceVector = distanceVector.normalize()

                overlap = min_distance - distance
                
                # Push particles apart equally
                self.x -= overlap / 2 * distanceVector.x
                self.y -= overlap / 2 * distanceVector.y
                particle.x += overlap / 2 * distanceVector.x
                particle.y += overlap / 2 * distanceVector.y
                
                newvx = self.vx
                self.vx = particle.vx; particle.vx = newvx
                newvy = self.vy
                self.vy = particle.vy; particle.vy = newvy
    
    def wallCollide(self) -> None:
        # Left & Right Wall Collision
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -1
        elif self.x > screenWidth - self.radius:
            self.x = screenWidth - self.radius
            self.vx *= -1
        
        # Top & Bottom Wall Collision
        if self.y < self.radius:
            self.y = self.radius
            self.vy *= -1
        elif self.y > screenHeight - self.radius:
            self.y = screenHeight - self.radius
            self.vy *= -1
        
particleGroup: set[Particle] = pygame.sprite.Group()