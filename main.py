import random
import time

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


def point_inside_zone(point, zone):
    x, y = point
    n = len(zone)
    inside = False

    p1x, p1y = zone[0]
    for j in range(1, n + 1):
        p2x, p2y = zone[j % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def check_click_in_zones(mouse_pos, zones):
    for zone_name, zone in zones.items():
        if point_inside_zone(mouse_pos, zone):
            return zone_name
    return None


def check_character_click(mouse_pos, character_selected, rect_size):
    for i, pos in enumerate(character_selected):
        char_rect = pygame.Rect(pos[0], pos[1], rect_size[0], rect_size[1])

        if char_rect.collidepoint(mouse_pos):
            return i
    return None


def find_character_positions(character_id):
    result = None
    for zone_name, positions in pos_in_rooms.items():
        for pos_idx, (coords, occupant) in enumerate(positions):
            if occupant == character_id:
                result = zone_name
    return result

pos_in_rooms = {
    "B1": [((471, 146), -1), ((399, 212), -1), ((525, 207), -1), ((466, 248), -1)],
    "B2": [((699, 149), -1), ((628, 275), -1), ((736, 273), -1), ((842, 274), -1)],
    "B3": [((881, 135), -1), ((934, 194), -1), ((1000, 134), -1), ((1044, 186), -1)],
    "B4": [((1148, 140), -1), ((1162, 218), -1), ((1254, 221), -1), ((1223, 151), -1)],
    "B5": [((957, 300), -1), ((1014, 409), -1), ((957, 508), -1), ((1102, 412), -1)],

    "R1": [((358, 421), 0), ((432, 363), 1), ((517, 422), 2), ((428, 472), -1)],
    "R2": [((402, 600), -1), ((506, 603), -1), ((442, 683), -1), ((534, 660), -1)],
    "R3": [((608, 545), -1), ((664, 476), -1), ((690, 404), -1), ((802, 408), -1)],
    "R4": [((785, 515), -1), ((751, 583), -1), ((850, 581), -1), ((851, 517), -1)],
    "R5": [((668, 644), -1), ((695, 695), -1), ((761, 675), -1), ((839, 687), -1)],

    "G1": [((530, 782), -1), ((608, 817), -1), ((681, 817), -1), ((727, 778), -1)],
    "G2": [((813, 778), -1), ((847, 834), -1), ((901, 781), -1), ((954, 822), -1)],
    "G3": [((1105, 782), -1), ((1261, 771), -1), ((1176, 639), -1), ((1292, 668), -1)],
    "G4": [((945, 621), -1), ((945, 693), -1), ((1030, 691), -1), ((1030, 621), -1)],
    "G5": [((1213, 481), -1), ((1311, 528), -1), ((1215, 332), -1), ((1246, 405), 3)],
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

connected_zones = {
    "B1": ["R1", "B2"],
    "B2": ["R1", "B1", "B3", "B5"],
    "B3": ["B2", "B4"],
    "B4": ["B3", "G5"],
    "B5": ["B2", "R3", "R4"],

    "R1": ["R2", "R3", "B1", "B2"],
    "R2": ["R1", "R3", "R5", "G1"],
    "R3": ["R1", "R2", "B5"],
    "R4": ["R5", "B5"],
    "R5": ["R4", "R2", "G4"],

    "G1": ["R2", "G2"],
    "G2": ["G1", "G3", "B1"],
    "G3": ["G2", "G4", "G5"],
    "G4": ["G3", "R5"],
    "G5": ["G3", "B4"],
}

# starting_positions = [
#     (430, 350),
#     (350, 425),
#     (500, 425),
#     (1260, 425)
# ]

rect_size = (285, 210)

character_selected = [(1474, 166), (1474, 383), (1474, 602)]
character_selected_bool = [False, False, False]
already_do = [False, False, False]
computer_do = False

radius = 30

journal_active = False
journal_text = []
journal_font = pygame.font.SysFont("Arial", 24)
journal_surface = pygame.Surface((300, 340))
journal_rect = journal_surface.get_rect(center=(160, 720))
scroll_offset = 0
line_height = 30


current_turn = "player"
message_duration = 1.5
PLAYER_COLOR = (0, 200, 0)
COMPUTER_COLOR = (200, 0, 0)
font = pygame.font.SysFont('Arial', 100, bold=True)

message_start_time = 0
current_message = None
computer_thinking = False
computer_think_start = 0
computer_think_duration = 5

def show_turn_message(turn):
    if turn == "player":
        text = "ВАШ ХОД"
        color = PLAYER_COLOR
    else:
        text = "ХОД КОМПЬЮТЕРА"
        color = COMPUTER_COLOR

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    screen.blit(overlay, (0, 0))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

    time.sleep(message_duration)

clicked_char = None
running = True
while running:
    if current_turn == "player":
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if current_turn == "player":
                    show_turn_message("computer")
                    current_turn = "computer"
                else:
                    show_turn_message("player")
                    current_turn = "player"

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_zone = check_click_in_zones(mouse_pos, zones)
                clicked_char = check_character_click(event.pos, character_selected, rect_size)

                if clicked_char is not None:
                    if already_do[clicked_char]:
                        print('Этот персонаж уже ходил')
                    else:
                        print(f"Выбрали персонажа {clicked_char}")
                        character_selected_bool = [False, False, False]
                        character_selected_bool[clicked_char] = True
                        selected_character = clicked_char

                if clicked_zone and any(character_selected_bool):
                    selected_character = character_selected_bool.index(True)

                    if already_do[selected_character]:
                        print('Этот персонаж уже ходил')
                    else:
                        current_zone = find_character_positions(selected_character)

                        if clicked_zone == current_zone[0]:
                            print("Вы кликнули в зону с персонажем")
                        else:
                            if clicked_zone in connected_zones[current_zone]:
                                for zone_name, positions in pos_in_rooms.items():
                                    for i, (pos, occupant) in enumerate(positions):
                                        if occupant == selected_character:
                                            pos_in_rooms[zone_name][i] = (pos, -1)

                                for i, (pos, occupant) in enumerate(pos_in_rooms[clicked_zone]):
                                    if occupant == -1:
                                        pos_in_rooms[clicked_zone][i] = (pos, selected_character)
                                        print(f"Персонаж {selected_character} перемещен в {clicked_zone}")
                                        already_do[selected_character] = True
                                        break
                                else:
                                    print("В выбранной зоне нет свободных мест")
                            else:
                                print("Персонаж не может переместиться в эту зону")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    journal_active = not journal_active

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    journal_text.append("тест")
                elif event.key == pygame.K_BACKSPACE:
                    if journal_text:
                        journal_text.pop()

            if event.type == pygame.MOUSEWHEEL:
                if journal_active:
                    scroll_offset -= event.y * line_height
                    max_scroll = max(0, len(journal_text) * line_height - journal_surface.get_height())
                    scroll_offset = max(0, min(scroll_offset, max_scroll))

    screen.blit(background_image, (0, 0))

    status_font = pygame.font.SysFont('Arial', 40)
    status_text = f"Сейчас ход: {'Игрок' if current_turn == 'player' else 'Компьютер'}"
    status_surface = status_font.render(status_text, True, (0,0,0))
    screen.blit(status_surface, (20, 60))

    if journal_active:
        journal_surface.fill((200, 200, 200))

        y_offset = 10 - scroll_offset
        for line in journal_text:
            text_surface = journal_font.render(line, True, (0, 0, 0))
            if y_offset + line_height > 0 and y_offset < journal_surface.get_height():
                journal_surface.blit(text_surface, (10, y_offset))
            y_offset += line_height

        screen.blit(journal_surface, journal_rect)

    if current_turn == "computer":
        selected_char = 3
        current_zone = find_character_positions(selected_char)
        if current_zone:
            connected = connected_zones[current_zone]
            if connected:
                new_zone = random.choice(connected)
                free_spots = [i for i, (pos, occ) in enumerate(pos_in_rooms[new_zone]) if occ == -1]
                if free_spots:
                    spot_idx = random.choice(free_spots)

                    for zone_name, positions in pos_in_rooms.items():
                        for i, (pos, occupant) in enumerate(positions):
                            if occupant == selected_char:
                                pos_in_rooms[zone_name][i] = (pos, -1)
                                break

                    pos = pos_in_rooms[new_zone][spot_idx][0]
                    pos_in_rooms[new_zone][spot_idx] = (pos, selected_char)

                    journal_text.append(f"Компьютер переместил персонажа {selected_char} в {new_zone}")
        computer_do = True

    for i in pos_in_rooms:
        for zone in pos_in_rooms[i]:
            if zone[1] != -1:
                pygame.draw.circle(screen, colors[zone[1]], zone[0], radius)

    for i, pos in enumerate(character_selected):
        if character_selected_bool[i]:
            pygame.draw.rect(screen, (0, 255, 0), (character_selected[i], rect_size), width=2)

    pygame.display.flip()

    if already_do == [True, True, True]:
        character_selected_bool = [False, False, False]
        already_do = [False, False, False]
        show_turn_message("computer")
        current_turn = "computer"
    if computer_do:
        show_turn_message("player")
        current_turn = "player"
        computer_do = False
pygame.quit()
sys.exit()
