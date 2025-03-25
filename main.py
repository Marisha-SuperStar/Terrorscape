import pygame
import sys
import math

pygame.init()

width, height = 1800, 900
screen = pygame.display.set_mode((width, height))

background_image = pygame.image.load('assets/background.png')

background_image = pygame.transform.scale(background_image, (width, height))

pygame.display.set_caption("Terrorscape")

colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 0, 0)
]

pos_in_rooms = {
    "R1": [(430, 350), (350, 425), (500, 425), (430, 500)],
    "R2": [(459, 603), (412, 681), (530, 646), (468, 690)],
    "R3": [(624, 531), (668, 448), (725, 398), (827, 387)]
}

starting_positions = [
    (430, 350),
    (350, 425),
    (500, 425),
    (1260, 425)
]

rect_size = (285, 210)

character_selected = [(1474, 166), (1474, 383), (1474, 602)]
character_selected_bool = [False, False, False]

radius = 30

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            print(f"{mouse_pos}")

            for i, pos in enumerate(starting_positions):
                distance = math.sqrt((mouse_pos[0] - pos[0]) ** 2 + (mouse_pos[1] - pos[1]) ** 2)
                if distance <= radius:
                    print(f"{colors[i]}")
                    character_selected_bool = [False, False, False]
                    character_selected_bool[i] = True
                    break

    screen.blit(background_image, (0, 0))

    for i, pos in enumerate(starting_positions):
        pygame.draw.circle(screen, colors[i], pos, radius)

    for i, pos in enumerate(character_selected):
        if character_selected_bool[i]:
            pygame.draw.rect(screen, (0, 255, 0), (character_selected[i], rect_size), width=2)

    pygame.display.flip()

pygame.quit()
sys.exit()