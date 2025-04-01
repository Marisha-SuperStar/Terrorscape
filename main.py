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
    "B1": [((471, 146), False), ((399, 212), False), ((525, 207), False), ((466, 248), False)],
    "B2": [((699, 149), False), ((628, 275), False), ((736, 273), False), ((842, 274), False)],
    "B3": [((881, 135), False), ((934, 194), False), ((1000, 134), False), ((1044, 186), False)],
    "B4": [((1148, 140), False), ((1162, 218), False), ((1254, 221), False), ((1223, 151), False)],
    "B5": [((957, 300), False), ((1014, 409), False), ((957, 508), False), ((1102, 412), False)],

    "R1": [((358, 421), False), ((432, 363), False), ((517, 422), False), ((428, 472), False)],
    "R2": [((402, 600), False), ((506, 603), False), ((442, 683), False), ((534, 660), False)],
    "R3": [((608, 545), False), ((664, 476), False), ((690, 404), False), ((802, 408), False)],
    "R4": [((785, 515), False), ((751, 583), False), ((850, 581), False), ((851, 517), False)],
    "R5": [((668, 644), False), ((695, 695), False), ((761, 675), False), ((839, 687), False)],

    "G1": [((530, 782), False), ((608, 817), False), ((681, 817), False), ((727, 778), False)],
    "G2": [((813, 778), False), ((847, 834), False), ((901, 781), False), ((954, 822), False)],
    "G3": [((1105, 782), False), ((1261, 771), False), ((1176, 639), False), ((1292, 668), False)],
    "G4": [((945, 621), False), ((945, 693), False), ((1030, 691), False), ((1030, 621), False)],
    "G5": [((1213, 481), False), ((1311, 528), False), ((1215, 332), False), ((1246, 405), False)],
}

zones = {
    "B1": [(350, 167), (350, 278), (519, 279), (576, 224), (574, 109), (408, 108), (351, 165)],
    "B2": [(598, 107), (602, 230), (545, 288), (609, 349), (636, 323), (879, 321), (879, 244), (826, 236), (818, 111), (598, 105)],
    "B3": [(845, 109), (847, 208), (1083, 210), (1087, 110), (845, 108)],
    "B4": [(1112, 108), (1115, 216), (1173, 268), (1282, 267), (1285, 166), (1232, 111), (1112, 105)],
    "B5": [(912, 238), (916, 559), (1093, 560), (1143, 502), (1145, 298), (1093, 241), (914, 236)],

    "R1": [(305, 344), (307, 494), (347, 529), (515, 526), (581, 460), (583, 376), (513, 311), (353, 308), (306, 343)],
    "R2": [(353, 560), (354, 669), (411, 727), (578, 721), (580, 631), (515, 569), (354, 560)],
    "R3": [(552, 544), (609, 601), (719, 492), (720, 456), (881, 451), (878, 356), (647, 355), (622, 378), (617, 469), (554, 543)],
    "R4": [(697, 564), (743, 609), (880, 608), (880, 483), (745, 480), (743, 511), (698, 563)],
    "R5": [(667, 601), (625, 639), (626, 717), (882, 721), (881, 648), (728, 642), (669, 601)],

    "G1": [(486, 756), (493, 835), (527, 853), (762, 856), (758, 750), (486, 757)],
    "G2": [(774, 754), (775, 854), (1008, 858), (1005, 753), (774, 751)],
    "G3": [(1026, 750), (1032, 853), (1312, 850), (1342, 818), (1346, 620), (1248, 603), (1225, 550), (1168, 531), (1117, 581), (1119, 680), (1107, 708), (1075, 737), (1027, 750)],
    "G4": [(910, 593), (913, 722), (1029, 724), (1064, 704), (1088, 676), (1087, 595), (910, 593)],
    "G5": [(1176, 301), (1176, 511), (1235, 535), (1254, 581), (1336, 599), (1341, 199), (1311, 178), (1312, 290), (1175, 301)],
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
already_do = [False, False, False]

radius = 30

journal_active = False
journal_text = []
journal_font = pygame.font.SysFont("Arial", 24)
journal_surface = pygame.Surface((300, 340))
journal_rect = journal_surface.get_rect(center=(160, 720))

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

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_j:
                journal_active = not journal_active

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                journal_text.append("тест")
            elif event.key == pygame.K_BACKSPACE:
                if journal_text:
                    journal_text.pop()

    screen.blit(background_image, (0, 0))

    if journal_active:
        journal_surface.fill((200, 200, 200))

        y_offset = 10
        for line in journal_text:
            text_surface = journal_font.render(line, True, (0, 0, 0))
            journal_surface.blit(text_surface, (10, y_offset))
            y_offset += 30

        screen.blit(journal_surface, journal_rect)

    for i, pos in enumerate(pos_in_rooms['R1']):
        pygame.draw.circle(screen, colors[i], pos[0], radius)

    for i, pos in enumerate(character_selected):
        if character_selected_bool[i]:
            pygame.draw.rect(screen, (0, 255, 0), (character_selected[i], rect_size), width=2)

    pygame.display.flip()

pygame.quit()
sys.exit()