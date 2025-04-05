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
    icon = pygame.Surface((32, 32)); icon.fill((250, 240, 240))
    
    pygame.display.set_caption("Particle Engine | FPS: N/A | Particles: N/A")
    pygame.display.set_icon(icon)
    
    # Create Particles
    size = 30
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
    #createGrid(1, 8)
    
    mousePosition = pygame.Vector2(pygame.mouse.get_pos())
    mouseButtons = pygame.mouse.get_pressed(); oldMouseButtons = mouseButtons
    
    # Main Loop
    run = True
    while run:
        mouseButtons = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                mousePosition = pygame.Vector2(pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                run = False
                
        screen.fill((0, 0, 0))
        
        # Spawn Particles with Mouse
        if mouseButtons[0] and not oldMouseButtons[0]:
            Particle(mousePosition.x, mousePosition.y, size, color)
        
        # Update Particles
        Particle.resolveCollisions()
        
        for particle in particleGroup:
            particle.move() 
        for particle in particleGroup:
            particle.update()
            particle.draw(screen)
        
        pygame.display.update()
        clock.tick(FPS)
        
        pygame.display.set_caption(f"Particle Engine | FPS: {clock.get_fps():.2f} | Particles: {len(particleGroup)}")
        
        oldMouseButtons = mouseButtons
    
pygame.quit()
exit()