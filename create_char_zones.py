import pygame
import sys

pygame.init()

width, height = 1800, 900
screen = pygame.display.set_mode((width, height))

background_image = pygame.image.load('assets/background.png')

background_image = pygame.transform.scale(background_image, (width, height))

pygame.display.set_caption("Terrorscape char")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

circles = {}

current_circle = None
current_radius = 20

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_circle is None:
                    center = event.pos
                    current_circle = (center, current_radius)
                else:
                    circle_id = f"C{len(circles) + 1}"
                    circles[circle_id] = current_circle
                    current_circle = None

        elif event.type == pygame.MOUSEWHEEL:
            if current_circle is not None:
                current_radius = max(10, current_radius + event.y * 5)
                current_circle = (current_circle[0], current_radius)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                with open("char.txt", "w") as file:
                    for circle_id, (center, radius) in circles.items():
                        file.write(f"{circle_id}: {center}, {radius}\n")
                print("Места для персонажей сохранены")

    screen.blit(background_image, (0, 0))

    for circle_id, (center, radius) in circles.items():
        pygame.draw.circle(screen, RED, center, radius, 2)
        font = pygame.font.SysFont(None, 24)
        text = font.render(circle_id, True, BLACK)
        screen.blit(text, (center[0] + radius + 5, center[1]))

    if current_circle is not None:
        center, radius = current_circle
        pygame.draw.circle(screen, BLACK, center, radius, 2)

    pygame.display.flip()

pygame.quit()
sys.exit()