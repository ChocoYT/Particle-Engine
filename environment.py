import pygame
import numpy as np

from configobj import ConfigObj
from typing import Union
from os import getcwd

from particle import Particle
from track import Track

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
        
        self.particles: set[Particle] = set()
        self.tracks:    set[Track]    = set()
        
    def resolveCollisions(self) -> None:
        threshold = 1e-4
        # (Optional for debugging: temporarily cap iterations)
        maxIterations = 1000  
        iteration = 0
        anyCollision = True

        while anyCollision and iteration < maxIterations:
            iteration += 1
            anyCollision = False

            for particle in self.particles:
                for obj in self.particles.union(self.tracks):
                    if particle is obj:
                        continue
                    if not obj.isColliding(particle):
                        continue

                    anyCollision = True

                    # Compute the vector and distance from the particle to the object
                    distVector = obj.getDistVector(particle)
                    dist = distVector.length()

                    if dist < threshold:
                        # When distance is too small, force a separation:
                        if isinstance(obj, Particle):
                            normal = pygame.Vector2(np.random.uniform(-1, 1), np.random.uniform(-1, 1)).normalize()
                        elif isinstance(obj, Track):
                            normal = pygame.Vector2(-obj.distVector.y, obj.distVector.x).normalize()
                        
                        particle.x += normal.x * particle.size
                        particle.y += normal.y * particle.size
                        
                        continue

                    if isinstance(obj, Particle):
                        overlap = particle.radius + obj.radius - dist
                        
                        if overlap <= 0:  continue
                        
                        correction = distVector.normalize() * (overlap / 2 + threshold)

                        particle.x -= correction.x
                        particle.y -= correction.y
                        obj.x += correction.x
                        obj.y += correction.y

                        pA = pygame.Vector2(particle.x, particle.y)
                        pB = pygame.Vector2(obj.x, obj.y)
                        vA = pygame.Vector2(particle.vx, particle.vy)
                        vB = pygame.Vector2(obj.vx, obj.vy)

                        normal_vec = (pB - pA).normalize()
                        tangent = pygame.Vector2(-normal_vec.y, normal_vec.x)

                        vA_n = vA.dot(normal_vec)
                        vA_t = vA.dot(tangent)
                        vB_n = vB.dot(normal_vec)
                        vB_t = vB.dot(tangent)

                        vA_n, vB_n = vB_n, vA_n

                        new_vA = (normal_vec * vA_n + tangent * vA_t) * self.energyLoss
                        new_vB = (normal_vec * vB_n + tangent * vB_t) * self.energyLoss

                        particle.vx, particle.vy = new_vA.x, new_vA.y
                        obj.vx, obj.vy = new_vB.x, new_vB.y

                    elif isinstance(obj, Track):
                        overlap = particle.radius + obj.width - dist
                        
                        if overlap <= 0:  continue
                        
                        correction = distVector.normalize() * (overlap + threshold)
                        particle.x -= correction.x
                        particle.y -= correction.y

                        velocity = pygame.Vector2(particle.vx, particle.vy).magnitude()
                        normalVec = obj.getDistVector(particle).normalize()
                    
                        velocity = pygame.Vector2(particle.vx, particle.vy)
                        reflected = velocity - 2 * velocity.dot(normalVec) * normalVec * self.energyLoss
                        
                        particle.x += overlap * normalVec.x - (self.gravity * self.gravityDirection.x)
                        particle.y += overlap * normalVec.y - (self.gravity * self.gravityDirection.y)
                        
                        particle.vx, particle.vy = reflected.x, reflected.y

            # After processing all collisions, update wall constraints.
            for particle in self.particles:
                particle.wallCollide(False)

        if iteration >= maxIterations:
            print("⚠️ Max collision iterations hit — possible infinite loop")


        
    def step(self) -> None:
        # Update Particles
        for particle in self.particles:
            particle.move()
            
        self.resolveCollisions()
        
        for particle in self.particles:
            particle.update()
            particle.draw(self.screen)
            
        # Update Tracks
        for track in self.tracks:
            track.update()
            track.draw(self.screen)
