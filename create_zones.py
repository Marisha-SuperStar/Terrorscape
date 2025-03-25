import pygame
import sys

pygame.init()

width, height = 1800, 900
screen = pygame.display.set_mode((width, height))

background_image = pygame.image.load('assets/background.png')
background_image = pygame.transform.scale(background_image, (width, height))

pygame.display.set_caption("Terrorscape zones")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

polygons = []
current_polygon = []


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                current_polygon.append(event.pos)
            elif event.button == 3:
                if len(current_polygon) >= 3:
                    polygons.append(current_polygon)
                    current_polygon = []
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with open("zones.txt", "w") as file:
                    for polygon in polygons:
                        file.write(str(polygon) + "\n")
                print("Зоны сохранены")

    screen.blit(background_image, (0, 0))


    for polygon in polygons:
        if len(polygon) >= 2:
            pygame.draw.lines(screen, RED, True, polygon, 2)

    if len(current_polygon) >= 2:
        pygame.draw.lines(screen, BLACK, False, current_polygon, 2)

    for point in current_polygon:
        pygame.draw.circle(screen, BLACK, point, 5)

    pygame.display.flip()

pygame.quit()
sys.exit()