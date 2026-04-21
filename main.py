import globals
import pygame
import pygame_textinput

running = True

textInput = pygame_textinput.TextInputVisualizer(font_object=globals.default_font)
pygame.key.set_repeat(400, 25)
while running:

    events = pygame.event.get()


    textInput.update(events)

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    globals.screen.fill("blue")
    
    globals.screen.blit(textInput.surface, (10,10))
    globals.screen.blit(globals.default_font.render("Hello World", True, (255,0,0)), (0,0))

    pygame.display.flip()

    globals.clock.tick(60)

pygame.quit()