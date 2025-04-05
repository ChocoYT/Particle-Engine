import pygame
import numpy as np

from configobj import ConfigObj
from typing import Union
from os import getcwd

from particle import Particle

number = Union[int, float]

path = getcwd()
defaults = ConfigObj(f'{path}\\defaults.ini')

class Environment:
    def __init__(
            self,
            screen:           pygame.Surface,
            gravity:          number | None = None,
            gravityDirection: pygame.Vector2 | None = None,
            airResistance:    number | None = None,
            energyLoss:       number | None = None
        ) -> None:
        
        self.screen = screen
        self.screenWidth, self.screenHeight = screen.get_size()
        
        self.gravity = gravity
        self.gravityDirection = gravityDirection
        self.airResistance = airResistance
        self.energyLoss = energyLoss
        
        if self.gravity          is None:  self.gravity = 0
        if self.gravityDirection is None:  self.gravityDirection = pygame.Vector2(0, 1)
        if self.airResistance    is None:  self.airResistance = 1
        if self.energyLoss       is None:  self.energyLoss = 1
        
        self.gravityDirection = self.gravityDirection.normalize()
        
        self.particles: set[Particle] = pygame.sprite.Group()
        
    def resolveCollisions(self) -> None:
        collisionFound = True
        threshold = 1

        while collisionFound:
            collisionFound = False

            for particleA in self.particles:
                for particleB in self.particles:
                    if particleA is particleB:  continue
                    if not particleA.isColliding(particleB):  continue

                    collisionFound = True
                    
                    distVector = particleA.getDistVector(particleB)
                    dist = distVector.magnitude()

                    if dist < threshold:
                        particleB.x -= (particleA.radius + particleB.radius) * self.gravityDirection.x
                        particleB.y -= (particleA.radius + particleB.radius) * self.gravityDirection.y

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
                    velA = (normal * normalVelA + tangent * tangentVelA) * self.energyLoss
                    velB = (normal * normalVelB + tangent * tangentVelB) * self.energyLoss

                    particleA.vx, particleA.vy = velA.x, velA.y
                    particleB.vx, particleB.vy = velB.x, velB.y
        
    def step(self) -> None:
        self.resolveCollisions()
        
        for particle in self.particles:
            particle.move()
        for particle in self.particles:
            particle.update()
            particle.draw(self.screen)
