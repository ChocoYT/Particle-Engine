import pygame

from configobj import ConfigObj
from typing import Union
from os import getcwd

from environment import Environment
from particle import Particle
from track import Track

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
    
    gravity       = float(defaults['constants']['gravity'])
    airResistance = float(defaults['constants']['air_resistance'])
    energyLoss    = float(defaults['constants']['energy_loss'])
    
    aspectRatio = screenWidth / screenHeight
    
    centerX = screenWidth / 2
    centerY = screenHeight / 2
    
    smallDim = min(screenWidth, screenHeight)
    largeDim = max(screenWidth, screenHeight)
    
    # Screen Setup
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    icon = pygame.Surface((32, 32)); icon.set_colorkey((0, 0, 0))
    
    pygame.display.set_caption("Particle Engine | FPS: N/A | Particles: N/A")
    pygame.display.set_icon(icon)
    
    # Create Particles
    environment = Environment(screen, gravity, pygame.Vector2(0, 1), airResistance, energyLoss)
    
    size = 30
    color = 255, 255, 255
    
    def createGrid(width: int, height: int) -> None:
        maxDim = max(width, height)
        
        spacing = smallDim / maxDim
        halfSpacing = spacing / 2
        
        for x in range(width):
            for y in range(height):
                Particle(
                    environment,
                    x * spacing + centerX - ((width  - 1) * halfSpacing),
                    y * spacing + centerY - ((height - 1) * halfSpacing),
                    size, color
                )
    
    mousePosition = pygame.Vector2(pygame.mouse.get_pos())
    mouseButtons = pygame.mouse.get_pressed(); oldMouseButtons = mouseButtons
    
    startPlacement = mousePosition
    
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
        if not mouseButtons[0] and oldMouseButtons[0]:
            Particle(environment, mousePosition.x, mousePosition.y, size, color)
            
        if mouseButtons[2] and not oldMouseButtons[2]:
            startPlacement = mousePosition
        if not mouseButtons[2] and oldMouseButtons[2]:
            Track(environment, startPlacement, mousePosition, color, 2)
        
        # Update Particles
        environment.step()
        
        pygame.display.update()
        clock.tick(FPS)
        
        pygame.display.set_caption(f"Particle Engine | FPS: {clock.get_fps():.2f} | Particles: {len(environment.particles)}")
        
        oldMouseButtons = mouseButtons
    
pygame.quit()
exit()