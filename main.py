import globals
import pygame
import pygame_textinput


running = True

textInput = pygame_textinput.TextInputVisualizer(font_object=globals.default_font)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    events = pygame.event.get()
    textInput.update(events)
    
    
    globals.screen.fill("blue")
    
    globals.screen.blit(textInput.surface, (10,10))
    globals.screen.blit(globals.default_font.render("Hello world", True, (255,0,0)), (0,0))

    pygame.display.flip()

    globals.clock.tick(60)

pygame.quit()