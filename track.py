import pygame
import numpy as np

from typing import Union

from particle import Particle

number = Union[int, float]

class Track(pygame.sprite.Sprite):
    def __init__(self, environment, startPosition: pygame.Vector2, endPosition: pygame.Vector2, color: tuple[number], width: int) -> None:
        super().__init__()
        
        self.environment = environment
        self.environment.tracks.add(self)
        
        self.startPosition = startPosition
        self.endPosition = endPosition
        
        self.width = width
        self.color = color
        
        self.distVector = endPosition - startPosition
        dist = self.distVector
        
        self.image = pygame.Surface((abs(dist.x), abs(dist.y)))
        self.image.set_colorkey((0, 0, 0))
        
        self.rect = self.image.get_rect()
        
        posX = np.sign(dist.x) == 1
        posY = np.sign(dist.y) == 1
        
        if posX and posY:
            pygame.draw.line(self.image, self.color, (0, 0), (dist.x, dist.y), width)
            self.rect.topleft = startPosition.x, startPosition.y
        elif not posX and posY:
            pygame.draw.line(self.image, self.color, (-dist.x, 0), (0, dist.y), width)
            self.rect.topright = startPosition.x, startPosition.y
        elif posX and not posY:
            pygame.draw.line(self.image, self.color, (0, -dist.y), (dist.x, 0), width)
            self.rect.bottomleft = startPosition.x, startPosition.y
        elif not posX and not posY:
            pygame.draw.line(self.image, self.color, (-dist.x, -dist.y), (0, 0), width)
            self.rect.bottomright = startPosition.x, startPosition.y
            
        self.slope = np.atan2(dist.y, dist.x)
        
        self.update()
        self.draw(self.environment.screen)
    
    def update(self) -> None:
        self.x, self.y = self.startPosition.x, self.startPosition.y
            
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.image, self.rect.topleft)
        
    def closestPointTo(self, particle) -> pygame.Vector2:
        P = self.startPosition
        Q = self.endPosition
        X = pygame.Vector2(particle.x, particle.y)
        
        l = ((X - P).x * (Q - P).x + (X - P).y * (Q - P).y) / (Q - P).length_squared()
    
        if l <= 0:
            return P
        elif l >= 1:
            return Q
        else:
            return P + l * (Q - P)

    def getDist(self, particle) -> float:
        return self.getDistVector(particle).length()

    def getDistVector(self, particle) -> pygame.Vector2:
        return self.closestPointTo(particle) - pygame.Vector2(particle.x, particle.y)

    def isColliding(self, particle) -> bool:
        return self.getDist(particle) <= (self.width / 2) + particle.radius
