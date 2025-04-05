import pygame
import numpy as np
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
energyLoss    = float(defaults['constants']['energy_loss'])

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
        
        self.update()
        self.draw(pygame.display.get_surface())
        
    def move(self) -> None:
        # Apply Gravity
        self.vy += gravity
        
        # Apply Drag Forces
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
            
    @classmethod
    def resolveCollisions(cls) -> None:
        collisionFound = True
        threshold = 1e-6

        while collisionFound:
            collisionFound = False

            for particleA in particleGroup:
                for particleB in particleGroup:
                    if particleA is particleB:
                        continue
                    if not particleA.isColliding(particleB):
                        continue

                    collisionFound = True

                    distVector = particleA.getDistVector(particleB)
                    dist = distVector.magnitude()

                    if dist == 0:
                        particleB.y -= (particleA.radius + particleB.radius) * np.sign(gravity)
                        distVector = particleA.getDistVector(particleB)
                        dist = distVector.magnitude()

                    overlap = particleA.radius + particleB.radius - dist
                    correction = distVector.normalize() * (overlap / 2 + threshold)

                    particleA.x -= correction.x
                    particleA.y -= correction.y
                    particleB.x += correction.x
                    particleB.y += correction.y

                    posA = pygame.Vector2(particleA.x, particleA.y)
                    posB = pygame.Vector2(particleB.x, particleB.y)
                    velA = pygame.Vector2(particleA.vx, particleA.vy)
                    velB = pygame.Vector2(particleB.vx, particleB.vy)

                    normal = (posB - posA).normalize()
                    tangent = pygame.Vector2(-normal.y, normal.x)

                    # Calculate Trig for Velocities
                    normalVelA = velA.dot(normal)
                    tangentVelA = velA.dot(tangent)
                    normalVelB = velB.dot(normal)
                    tangentVelB = velB.dot(tangent)

                    # Swap Velocities
                    normalVelA, normalVelB = normalVelB, normalVelA

                    # Calculate Final Velocities
                    velA = normal * normalVelA + tangent * tangentVelA * energyLoss
                    velB = normal * normalVelB + tangent * tangentVelB * energyLoss

                    particleA.vx, particleA.vy = velA.x, velA.y
                    particleB.vx, particleB.vy = velB.x, velB.y
    
        
particleGroup: set[Particle] = pygame.sprite.Group()