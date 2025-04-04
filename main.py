import pygame
from configobj import ConfigObj
from typing import Union
from os import getcwd

from particle import Particle, particleGroup

pygame.init()

number = Union[int, float]

if __name__ == "__main__":
    
    # Load Config File
    path = getcwd()
    defaults = ConfigObj(f'{path}\\defaults.ini')
    
    # Variable Initialisation
    screenWidth  = int(defaults['screen']['width'])
    screenHeight = int(defaults['screen']['height'])
    FPS          = int(defaults['screen']['FPS'])
    
    aspectRatio = screenWidth / screenHeight
    
    centerX = screenWidth / 2
    centerY = screenHeight / 2
    
    smallDim = min(screenWidth, screenHeight)
    largeDim = max(screenWidth, screenHeight)
    
    # Screen Setup
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Particle Engine")
    
    # Create Particles
    size = 10
    color = 255, 255, 255
    
    def createGrid(width: int, height: int) -> None:
        maxDim = max(width, height)
        
        spacing = smallDim / maxDim
        halfSpacing = spacing / 2
        
        for x in range(width):
            for y in range(height):
                Particle(
                    x * spacing + centerX - ((width  - 1) * halfSpacing),
                    y * spacing + centerY - ((height - 1) * halfSpacing),
                    size, color
                )   
    createGrid(1, 2)
    
    # Main Loop
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        screen.fill((0, 0, 0))
        
        # Update Particles
        for particle in particleGroup:
            particle.move()
        for particle in particleGroup:
            while particle.isColliding(particleGroup):  particle.resolveCollisions()
            
            particle.update()
            particle.draw(screen)
        
        pygame.display.update()
        clock.tick(FPS)
    
pygame.quit()
exit()