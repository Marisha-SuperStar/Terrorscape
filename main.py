import json
import random
import time
from collections import deque

import pygame
import sys


class Item: #карточки предметов
    def __init__(self, image, name, filename):
        self.item_image = image
        self.item_name = name
        self.image_filename = filename

    def to_dict(self):
        return {
            'image_filename': self.image_filename
        }

    @staticmethod
    def from_dict(data):
        match data['image_filename']:
            case Game.heal_item.image_filename:
                return Game.heal_item
            case Game.key_item.image_filename:
                return Game.key_item
            case Game.gun_item.image_filename:
                return Game.gun_item
            case Game.ammo_item.image_filename:
                return Game.ammo_item
            case Game.sword_item.image_filename:
                return Game.sword_item
            case Game.def1_item.image_filename:
                return Game.def1_item

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.health = 2
        self.scare = 0
        self.inventory = []
        self.has_acted = False
        self.position = None

    def use_item(self, item): #когда персонаж находит ключ, метод автоматически вызывается и ключ "используется"
        if item == Game.key_item:
            Game.keys += 1
            Game.journal.add_entry(f"Персонаж {self.id} нашёл ключ {item.item_name}")
        elif item == Game.heal_item:
            if self.health == 1:
                self.health += 1
            self.inventory.remove(item)
            Game.journal.add_entry(f"Персонаж {self.id} использовал {item.item_name}")

    def defense_bonus(self):
        bonus = 0
        for item in self.inventory[:]:
            if item == Game.gun_item and Game.ammo_item in self.inventory:
                bonus += 5
                Game.journal.add_entry(f"Персонаж {self.id} использовал для защиты Револьвер и Патроны")
                self.inventory.remove(Game.ammo_item)
            elif item == Game.sword_item:
                bonus += 2
                Game.journal.add_entry(f"Персонаж {self.id} использовал для защиты Меч")
            elif item == Game.def1_item:
                bonus += 3
                Game.journal.add_entry(f"Персонаж {self.id} использовал для защиты Мешок с цементом")
                self.inventory.remove(item)
        return bonus

    def is_alive(self):
        return self.health > 0


    def to_dict(self):
        return {
            'id': self.id,
            'health': self.health,
            'scare': self.scare,
            'inventory': [item.to_dict() for item in self.inventory],
            'has_acted': self.has_acted,
            'position': self.position
        }

    @classmethod
    def from_dict(cls, data): #метод чтобы создать объект класса игрок во время загрузки игры
        player = cls(data['id'])
        player.health = data['health']
        player.scare = data['scare']
        player.inventory = [Item.from_dict(item_data) for item_data in data['inventory']]
        player.has_acted = data['has_acted']
        player.position = data['position']
        return player


class Killer:
    def __init__(self):
        self.id = 3
        self.position = None

    def to_dict(self):
        return {
            'id': self.id,
            'position': self.position
        }

    @classmethod
    def from_dict(cls, data): #метод чтобы создать объект класса убийца во время загрузки игры
        killer = cls()
        killer.id = data['id']
        killer.position = data['position']
        return killer

    def move(self):
        current_room = self.get_position()
        for pos, occupant in Game.pos_in_rooms[current_room]: #occupant id персонажа/убийцы в комнатах, где персонажи могут находиться
            if occupant != -1 and occupant != self.id: #-1 комната пустая просто потому что; если в комнате есть игрок, происходит столкновение
                return False

        target_room = self.find_best_room()
        if not target_room: # защита от ошибки, скорее всего никогда не понадобится, но пусть будет
            available_rooms = Game.connected_zones.get(current_room, [])
            if not available_rooms:
                return False
            target_room = random.choice(available_rooms)

        for i, (pos, occupant) in enumerate(Game.pos_in_rooms[current_room]): #выгоняем убийцу из комнаты
            if occupant == self.id:
                Game.pos_in_rooms[current_room][i] = (pos, -1)
                break

        for i, (pos, occupant) in enumerate(Game.pos_in_rooms[target_room]): # убийца занимает новую комнату
            if occupant == -1:
                Game.pos_in_rooms[target_room][i] = (pos, self.id)
                Game.journal.add_entry(f"Убийца переместился из {current_room} в {target_room}")
                return True

        return False

    def find_best_room(self):
        current_room = self.get_position()
        if not current_room: #защита от ошибки
            return None

        player_rooms = self.get_rooms_with_players()
        if not player_rooms: #защита от ошибки
            return None

        room_scores = [] #оценка комнаты
        for target_room, player_count in player_rooms.items():
            path = Game.find_shortest_path(current_room, target_room)
            if path:
                distance = len(path) - 1
                room_scores.append((target_room, distance, player_count))

        if not room_scores:
            return None

        room_scores.sort(key=lambda x: (x[1], -x[2])) #сортировка по возрастанию дистанции и убыванию игроков
        closest_rooms = [room for room, dist, _ in room_scores if dist == room_scores[0][1]]
        best_target = max(closest_rooms, key=lambda r: player_rooms[r])

        path = Game.find_shortest_path(current_room, best_target)
        if path and len(path) > 1:
            return path[1]

        return None

    def get_rooms_with_players(self):
        player_rooms = {}
        for room_name, positions in Game.pos_in_rooms.items():
            player_count = sum(1 for _, occupant in positions if occupant != -1 and occupant != self.id)
            if player_count > 0:
                player_rooms[room_name] = player_count
        return player_rooms

    def get_position(self):
        for room_name, positions in Game.pos_in_rooms.items():
            for pos, occupant in positions:
                if occupant == self.id:
                    return room_name
        return None

    def check_combat(self):
        killer_rooms = []
        for room_name, positions in Game.pos_in_rooms.items():
            if any(occupant == self.id for (pos, occupant) in positions):
                killer_rooms.append(room_name)

        for room in killer_rooms:
            players_in_room = []
            for pos, occupant in Game.pos_in_rooms[room]:
                if occupant != -1 and occupant != self.id:
                    players_in_room.append(occupant)

            if players_in_room:
                Game.journal.add_entry(f"Убийца в комнате {room} с игроками: {players_in_room}")

                killer_roll = random.randint(1, 10)
                Game.journal.add_entry(f"Убийца бросает кубик: {killer_roll}")

                player_rolls = {}
                for player_id in players_in_room:
                    player = Game.players[player_id]
                    roll = random.randint(1, 10)
                    bonus = player.defense_bonus()
                    player_rolls[player_id] = roll + bonus
                    Game.journal.add_entry(f"Игрок {player_id} бросает кубик: {roll} и получает бонус за предметы {bonus}")

                damaged_players = []
                for player_id, roll in player_rolls.items():
                    if killer_roll > roll:
                        damaged_players.append(player_id)

                if damaged_players:
                    Game.journal.add_entry(f"Убийца наносит урон игрокам: {damaged_players}")
                    for player_id in damaged_players:
                        Game.players[player_id].health -= 1
                        Game.journal.add_entry(
                            f"Персонаж {player_id} получает урон! Осталось HP: {Game.players[player_id].health}")
                else:
                    Game.journal.add_entry("Убийце не удалось никого ранить!")


class Journal:
    def __init__(self):
        self.entries = []
        self.font = None
        self.surface = pygame.Surface((600, 340))
        self.rect = self.surface.get_rect(center=(330, 720))
        self.scroll_offset = 0
        self.line_height = 30
        self.active = False

    def to_dict(self):
        return {
            'entries': self.entries,
            'scroll_offset': self.scroll_offset,
            'active': self.active
        }

    @classmethod #метод чтобы создать объект класса журнал во время загрузки игры
    def from_dict(cls, data):
        journal = cls()
        journal.entries = data['entries']
        journal.scroll_offset = data['scroll_offset']
        journal.active = data['active']
        return journal

    def init_font(self): #инициализация шрифта
        self.font = pygame.font.SysFont("Arial", 24)

    def add_entry(self, text):
        self.entries.append(text)

    def render(self, screen): #отображение
        if not self.active:
            return

        self.surface.fill((200, 200, 200))
        y_offset = 10 - self.scroll_offset

        for line in self.entries:
            text_surface = self.font.render(line, True, (0, 0, 0))
            if y_offset + self.line_height > 0 and y_offset < self.surface.get_height():
                self.surface.blit(text_surface, (10, y_offset))
            y_offset += self.line_height

        if len(self.entries) * self.line_height > self.surface.get_height():
            scroll_ratio = self.scroll_offset / (len(self.entries) * self.line_height - self.surface.get_height())
            scrollbar_height = self.surface.get_height() * 0.2
            scrollbar_y = scroll_ratio * (self.surface.get_height() - scrollbar_height)
            pygame.draw.rect(self.surface, (100, 100, 100),
                             (self.surface.get_width() - 10, scrollbar_y, 8, scrollbar_height))

        screen.blit(self.surface, self.rect)

    def handle_scroll(self, key):
        if key == pygame.K_UP:
            self.scroll_offset -= self.line_height * 3
        elif key == pygame.K_DOWN:
            self.scroll_offset += self.line_height * 3
        elif key == pygame.K_PAGEUP:
            self.scroll_offset -= self.surface.get_height() * 0.8
        elif key == pygame.K_PAGEDOWN:
            self.scroll_offset += self.surface.get_height() * 0.8

        content_height = len(self.entries) * self.line_height
        visible_height = self.surface.get_height()
        max_scroll = max(0, content_height - visible_height + self.line_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))


class GUI: #интерфейс
    def __init__(self):
        self.width, self.height = 1800, 900
        self.screen = None
        self.background_image = None
        self.skull_image = None
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
        self.scare_pos = [10, 80, 150]
        self.items_pos = [(36, 370), (36, 590), (186, 590)]
        self.character_selected_pos = [(1474, 166), (1474, 383), (1474, 602)]
        self.character_selected_bool = [False, False, False] #какой персонаж активен
        self.rect_size = (285, 210)
        self.radius = 30

        self.font = None
        self.big_font = None
        self.PLAYER_COLOR = (0, 200, 0)
        self.COMPUTER_COLOR = (200, 0, 0)
        self.message_duration = 1.5

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Terrorscape")

        self.font = pygame.font.SysFont('Arial', 40)
        self.big_font = pygame.font.SysFont('Arial', 100, bold=True)

        self.background_image = pygame.transform.scale(
            pygame.image.load('assets/background.png'),
            (self.width, self.height)
        )
        self.skull_image = pygame.transform.scale(
            pygame.image.load('assets/scare.png'),
            (30, 50)
        )

    def show_turn_message(self, turn):
        if turn == "player":
            text = "ВАШ ХОД"
            color = self.PLAYER_COLOR
        elif turn == 'computer':
            text = "ХОД КОМПЬЮТЕРА"
            color = self.COMPUTER_COLOR
        elif turn == 'player_end':
            text = "ВЫ ПРОИГРАЛИ"
            color = self.COMPUTER_COLOR
        else:
            text = "ВЫ ПОБЕДИЛИ"
            color = self.PLAYER_COLOR

        text_surface = self.big_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

        time.sleep(self.message_duration)

    def render(self):
        self.screen.blit(self.background_image, (0, 0))

        status_text = f"Ключи: {Game.keys}"
        status_surface = self.font.render(status_text, True, (255, 255, 255))
        self.screen.blit(status_surface, (20, 60))

        for room in Game.pos_in_rooms.values():
            for pos, occupant in room:
                if occupant != -1:
                    if occupant != Game.killer.id:
                        if Game.players[occupant].is_alive():
                            pygame.draw.circle(self.screen, self.colors[occupant], pos, self.radius)
                    else:
                        pygame.draw.circle(self.screen, self.colors[occupant], pos, self.radius)

        for i in range(Game.repairs):
            pygame.draw.rect(self.screen, (0, 255, 0), ((65 + (i * 50), 160), (50, 53)))

        for i, pos in enumerate(self.character_selected_pos):
            if self.character_selected_bool[i]:
                pygame.draw.rect(self.screen, (0, 255, 0), (pos, self.rect_size), width=2)
                if Game.players[i].scare > 0:
                    for j in range(Game.players[i].scare):
                        skull_pos = (pos[0] - 50, pos[1] + self.scare_pos[j])
                        self.screen.blit(self.skull_image, skull_pos)

                for j, item in enumerate(Game.players[i].inventory):
                    item_pos = self.items_pos[j]
                    self.screen.blit(item.item_image, item_pos)

                health_text = f"Здоровье: {Game.players[i].health}"
                health_surface = self.font.render(health_text, True, (255, 0, 0))
                self.screen.blit(health_surface, (1500, 60))
            else:
                if not Game.players[i].is_alive():
                    pygame.draw.rect(self.screen, (255, 0, 0), (pos, self.rect_size), width=6)

        if Game.repairs == 5:
            repairs_text = f"Осталось раундов до приезда полиции: {Game.count_round}"
            repairs_surface = self.font.render(repairs_text, True, (255, 255, 255))
            self.screen.blit(repairs_surface, (600, 30))

        Game.journal.render(self.screen)

        pygame.display.flip()

    def check_click_in_zones(self, mouse_pos):
        for zone_name, zone in Game.zones.items():
            if self.point_inside_zone(mouse_pos, zone):
                return zone_name
        return None

    def point_inside_zone(self, point, zone):
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

    def check_item_click(self, mouse_pos, inventory):
        for i, pos in enumerate(self.items_pos):
            item_rect = pygame.Rect(pos[0], pos[1], 140, 200)
            if item_rect.collidepoint(mouse_pos) and i < len(inventory):
                return i
        return None

    def check_character_click(self, mouse_pos):
        for i, pos in enumerate(self.character_selected_pos):
            char_rect = pygame.Rect(pos[0], pos[1], self.rect_size[0], self.rect_size[1])
            if char_rect.collidepoint(mouse_pos):
                return i
        return None


class Game:
    keys = 0
    repairs = 0
    count_round = 6
    already_repaired = False
    current_turn = "player"
    computer_do = False

    players = [Player(0), Player(1), Player(2)]
    killer = Killer()
    gui = GUI()
    journal = Journal()

    heal_item = Item(None, 'Целебные травы', 'heal.png')
    key_item = Item(None, 'Ключ', 'key.png')
    gun_item = Item(None, 'Револьвер', 'gun.png')
    ammo_item = Item(None, 'Патроны', 'ammo.png')
    sword_item = Item(None, 'Меч', 'sword.png')
    def1_item = Item(None, 'Мешок цемента', 'def1.png')

    zone_items = {
        "R2": [],
        "G4": [],
        "B4": []
    }

    # -1 комната пустая просто потому что;
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
        "B2": [(598, 107), (602, 230), (545, 288), (609, 349), (636, 323), (879, 321), (879, 244), (826, 236),
               (818, 111), (598, 105)],
        "B3": [(845, 109), (847, 208), (1083, 210), (1087, 110), (845, 108)],
        "B4": [(1112, 108), (1115, 216), (1173, 268), (1282, 267), (1285, 166), (1232, 111), (1112, 105)],
        "B5": [(912, 238), (916, 559), (1093, 560), (1143, 502), (1145, 298), (1093, 241), (914, 236)],
        "R1": [(305, 344), (307, 494), (347, 529), (515, 526), (581, 460), (583, 376), (513, 311), (353, 308),
               (306, 343)],
        "R2": [(353, 560), (354, 669), (411, 727), (578, 721), (580, 631), (515, 569), (354, 560)],
        "R3": [(552, 544), (609, 601), (719, 492), (720, 456), (881, 451), (878, 356), (647, 355), (622, 378),
               (617, 469), (554, 543)],
        "R4": [(697, 564), (743, 609), (880, 608), (880, 483), (745, 480), (743, 511), (698, 563)],
        "R5": [(667, 601), (625, 639), (626, 717), (882, 721), (881, 648), (728, 642), (669, 601)],
        "G1": [(486, 756), (493, 835), (527, 853), (762, 856), (758, 750), (486, 757)],
        "G2": [(774, 754), (775, 854), (1008, 858), (1005, 753), (774, 751)],
        "G3": [(1026, 750), (1032, 853), (1312, 850), (1342, 818), (1346, 620), (1248, 603), (1225, 550), (1168, 531),
               (1117, 581), (1119, 680), (1107, 708), (1075, 737), (1027, 750)],
        "G4": [(910, 593), (913, 722), (1029, 724), (1064, 704), (1088, 676), (1087, 595), (910, 593)],
        "G5": [(1176, 301), (1176, 511), (1235, 535), (1254, 581), (1336, 599), (1341, 199), (1311, 178), (1312, 290),
               (1175, 301)],
    }

    connected_zones = {
        "B1": ["R1", "B2", "G1"],
        "B2": ["R1", "B1", "B3", "B5"],
        "B3": ["B2", "B4"],
        "B4": ["B3", "G5"],
        "B5": ["B2", "R3", "R4", "G5"],
        "R1": ["R2", "R3", "B1", "B2"],
        "R2": ["R1", "R3", "R5", "G1"],
        "R3": ["R1", "R2", "B5"],
        "R4": ["R5", "B5"],
        "R5": ["R4", "R2", "G4"],
        "G1": ["R2", "G2"],
        "G2": ["G1", "G3", "B1"],
        "G3": ["G2", "G4", "G5"],
        "G4": ["G3", "R5"],
        "G5": ["G3", "B4", "B5"],
    }

    @staticmethod
    def save_game():
        save_data = {
            'keys': Game.keys,
            'repairs': Game.repairs,
            'count_round': Game.count_round,
            'already_repaired': Game.already_repaired,
            'current_turn': Game.current_turn,
            'computer_do': Game.computer_do,
            'players': [player.to_dict() for player in Game.players],
            'killer': Game.killer.to_dict(),
            'journal': Game.journal.to_dict(),
            'zone_items': {zone: [item.to_dict() for item in items] for zone, items in Game.zone_items.items()},
            'pos_in_rooms': Game.pos_in_rooms,
            'gui': {
                'character_selected_bool': Game.gui.character_selected_bool
            }
        }

        with open('savegame.json', 'w') as f:
            json.dump(save_data, f, indent=2)

        Game.journal.add_entry("Игра сохранена")

    @staticmethod
    def load_game():
        try:
            with open('savegame.json', 'r') as f:
                save_data = json.load(f)

            Game.keys = save_data['keys']
            Game.repairs = save_data['repairs']
            Game.count_round = save_data['count_round']
            Game.already_repaired = save_data['already_repaired']
            Game.current_turn = save_data['current_turn']
            Game.computer_do = save_data['computer_do']

            Game.players = [Player.from_dict(player_data) for player_data in save_data['players']]
            Game.killer = Killer.from_dict(save_data['killer'])
            Game.journal = Journal.from_dict(save_data['journal'])
            Game.journal.init_font()

            Game.zone_items = {
                zone: [Item.from_dict(item_data) for item_data in items_data]
                for zone, items_data in save_data['zone_items'].items()
            }

            Game.pos_in_rooms = save_data['pos_in_rooms']
            Game.gui.character_selected_bool = save_data['gui']['character_selected_bool']

            Game.journal.add_entry("Игра загружена")
            return True

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False

    @staticmethod #метод можно использовать из класса без привязки к объекту
    def find_shortest_path(start_room, target_room):
        if start_room == target_room:
            return [start_room]

        visited = {start_room}
        queue = deque([(start_room, [])]) #я не помню что это и как работает

        while queue:
            current_room, path = queue.popleft()

            for neighbor in Game.connected_zones.get(current_room, []):
                if neighbor == target_room:
                    return path + [current_room, neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [current_room]))

        return None

    @staticmethod
    def can_reach_in_1_or_2_steps(start_zone, target_zone):
        if start_zone not in Game.connected_zones or target_zone not in Game.connected_zones:
            return False

        if target_zone in Game.connected_zones[start_zone]:
            return True

        for intermediate_zone in Game.connected_zones[start_zone]:
            if intermediate_zone in Game.connected_zones and target_zone in Game.connected_zones[intermediate_zone]:
                return True

        return False

    @staticmethod
    def find_character_positions(character_id):
        for zone_name, positions in Game.pos_in_rooms.items():
            for pos_idx, (coords, occupant) in enumerate(positions):
                if occupant == character_id:
                    return zone_name
        return None

    @staticmethod
    def check_death():
        for j, player in enumerate(Game.players):
            char_zone = Game.find_character_positions(player.id)
            if char_zone and player.health <= 0:
                for i, (pos, occupant) in enumerate(Game.pos_in_rooms[char_zone]):
                    if occupant == player.id:
                        Game.pos_in_rooms[char_zone][i] = (pos, -1)
                        break

    @staticmethod
    def distribute_items():
        items_to_distribute = []
        items_to_distribute.extend([Game.key_item] * 5)
        items_to_distribute.extend([Game.heal_item] * 4)
        items_to_distribute.extend([Game.gun_item] * 1)
        items_to_distribute.extend([Game.ammo_item] * 3)
        items_to_distribute.extend([Game.sword_item] * 2)
        items_to_distribute.extend([Game.def1_item] * 3)

        random.shuffle(items_to_distribute)
        zones = list(Game.zone_items.keys())

        for item in items_to_distribute:
            zone = random.choice(zones)
            Game.zone_items[zone].append(item)
        for zone, items in Game.zone_items.items():
            print(f"Зона {zone} получила {len(items)} предметов:")
            for item in items:
                if item == Game.key_item:
                    print("  - Ключ")
                elif item == Game.heal_item:
                    print("  - Аптечка")
                elif item == Game.gun_item:
                    print("  - Пистолет")
                elif item == Game.ammo_item:
                    print("  - Патроны")
                elif item == Game.sword_item:
                    print("  - Меч")
                elif item == Game.def1_item:
                    print("  - Цемент")


    @staticmethod
    def initialize_items():
        Game.heal_item.item_image = pygame.transform.scale(pygame.image.load('assets/heal.png'), (140, 200))
        Game.key_item.item_image = pygame.transform.scale(pygame.image.load('assets/key.png'), (140, 200))
        Game.gun_item.item_image = pygame.transform.scale(pygame.image.load('assets/gun.png'), (140, 200))
        Game.ammo_item.item_image = pygame.transform.scale(pygame.image.load('assets/ammo.png'), (140, 200))
        Game.sword_item.item_image = pygame.transform.scale(pygame.image.load('assets/sword.png'), (140, 200))
        Game.def1_item.item_image = pygame.transform.scale(pygame.image.load('assets/def1.png'), (140, 200))

    @staticmethod
    def handle_computer_turn():
        move = random.randint(1, 2)
        for _ in range(move):
            Game.killer.move()
        Game.killer.check_combat()

        current_zone = Game.find_character_positions(Game.killer.id)
        if current_zone:
            connected = Game.connected_zones[current_zone]
            if connected:
                for player in Game.players:
                    char_zone = Game.find_character_positions(player.id)
                    for zone in connected:
                        if zone == char_zone:
                            player.scare += 1
                            Game.journal.add_entry(f"Игрок {player.id} ИСПУГАН")

        for player in Game.players:
            if player.scare == 3:
                player.scare = 0
                player.health -= 1
                Game.journal.add_entry(f"Игрок {player.id} впадает в панику и получает урон! Осталось HP: {player.health}")


        Game.current_turn = "player"
        Game.computer_do = True

    @staticmethod
    def check_victory():
        if Game.keys == 5:
            players_in_room = []
            healthy_players = sum([1 if player.health > 0 else 0 for player in Game.players])
            for pos, occupant in Game.pos_in_rooms['R1']:
                if occupant != -1 and occupant != Game.killer.id:
                    players_in_room.append(occupant)
            if len(players_in_room) == healthy_players:
                Game.gui.show_turn_message('end')
                return True

        if sum(player.health for player in Game.players) == 0:
            Game.gui.show_turn_message('player_end')
            return True

        if Game.repairs == 5 and Game.count_round == 0:
            Game.gui.show_turn_message('end')
            return True

        return False

    @staticmethod
    def run():
        Game.gui.init_pygame()
        Game.journal.init_font()
        Game.initialize_items()
        Game.distribute_items()
        Game.journal.add_entry("---НОВЫЙ РАУНД---")
        running = True
        while running:
            if Game.check_victory():
                break

            if Game.current_turn == "player":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_s:  # Сохраняем игру при нажатии S
                            Game.save_game()
                        elif event.key == pygame.K_l:  # Загружаем игру при нажатии L
                            Game.load_game()

                    if Game.journal.active:
                        if event.type == pygame.KEYDOWN:
                            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                                Game.journal.handle_scroll(event.key)
                            elif event.key == pygame.K_j:
                                Game.journal.active = False
                    else:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_j:
                                Game.journal.active = True
                            elif event.key == pygame.K_r:
                                if any(Game.gui.character_selected_bool):
                                    selected_character = Game.gui.character_selected_bool.index(True)
                                    clicked_items = Game.gui.check_item_click(
                                        pygame.mouse.get_pos(),
                                        Game.players[selected_character].inventory
                                    )
                                    if clicked_items is not None:
                                        selected_item = Game.players[selected_character].inventory[clicked_items]
                                        Game.players[selected_character].inventory.remove(selected_item)
                                        Game.journal.add_entry(
                                            f"Персонаж {selected_character} выкинул {selected_item.item_name}")

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            clicked_zone = Game.gui.check_click_in_zones(mouse_pos)
                            clicked_char = Game.gui.check_character_click(mouse_pos)

                            if clicked_char is not None:
                                if not Game.players[clicked_char].is_alive():
                                    Game.journal.add_entry(f"Персонаж {clicked_char} умер")
                                elif Game.players[clicked_char].has_acted:
                                    Game.journal.add_entry(f"Персонаж {clicked_char} уже ходил")
                                else:
                                    Game.gui.character_selected_bool = [False, False, False]
                                    Game.gui.character_selected_bool[clicked_char] = True
                                    Game.journal.add_entry(f"Выбрали персонажа {clicked_char}")

                            if any(Game.gui.character_selected_bool):
                                selected_character = Game.gui.character_selected_bool.index(True)
                                clicked_items = Game.gui.check_item_click(
                                    mouse_pos,
                                    Game.players[selected_character].inventory
                                )
                                if clicked_items is not None:
                                    selected_item = Game.players[selected_character].inventory[clicked_items]
                                    Game.players[selected_character].use_item(selected_item)

                                if clicked_zone:
                                    if Game.players[selected_character].has_acted:
                                        Game.journal.add_entry(f"Персонаж {selected_character} уже ходил")
                                    else:
                                        current_zone = Game.find_character_positions(selected_character)

                                        if clicked_zone == current_zone:
                                            Game.journal.add_entry(f"Персонаж {selected_character} остаётся в зоне {clicked_zone}")
                                            if clicked_zone in Game.zone_items.keys():
                                                if len(Game.players[selected_character].inventory) < 3:
                                                    if not Game.zone_items[clicked_zone]:
                                                        Game.journal.add_entry(f"В зоне {clicked_zone} закончились предметы")
                                                        break
                                                    else:
                                                        chance = random.randint(0, 1000)
                                                        if chance >= 200:
                                                            item = Game.zone_items[clicked_zone].pop()
                                                            if item == Game.key_item:
                                                                Game.players[selected_character].use_item(item)
                                                            else:
                                                                Game.players[selected_character].inventory.append(item)
                                                                Game.journal.add_entry(
                                                                    f"Персонаж {selected_character} получил {item.item_name}")
                                                        else:
                                                            Game.journal.add_entry(f"Персонаж {selected_character} не нашёл предмет в зоне {clicked_zone}")
                                                else:
                                                    Game.journal.add_entry(f"У персонажа {selected_character} переполнен инвентарь")
                                                    break
                                            elif clicked_zone == 'B1':
                                                killer_room = Game.killer.get_position()
                                                if killer_room == 'B1' or Game.already_repaired:
                                                    Game.journal.add_entry(f"Нельзя чинить")
                                                    break
                                                else:
                                                    Game.already_repaired = True
                                                    Game.repairs += 1
                                                    Game.journal.add_entry("Починили немного")
                                            Game.players[selected_character].has_acted = True
                                        else:
                                            if Game.can_reach_in_1_or_2_steps(clicked_zone, current_zone):
                                                for zone_name, positions in Game.pos_in_rooms.items():
                                                    for i, (pos, occupant) in enumerate(positions):
                                                        if occupant == selected_character:
                                                            Game.pos_in_rooms[zone_name][i] = (pos, -1)

                                                for i, (pos, occupant) in enumerate(Game.pos_in_rooms[clicked_zone]):
                                                    if occupant == -1:
                                                        Game.pos_in_rooms[clicked_zone][i] = (pos, selected_character)
                                                        Game.journal.add_entry(
                                                            f"Персонаж {selected_character} перемещен в {clicked_zone}")
                                                        Game.players[selected_character].has_acted = True
                                                        break
                                                else:
                                                    Game.journal.add_entry("В выбранной зоне нет свободных мест")
                                            else:
                                                Game.journal.add_entry("Туда нельзя перейти")
                                                break



            if all(player.has_acted or not player.is_alive() for player in Game.players):
                Game.gui.character_selected_bool = [False, False, False]
                for player in Game.players:
                    player.has_acted = False
                Game.already_repaired = False
                Game.gui.show_turn_message("computer")
                Game.current_turn = "computer"


            if Game.current_turn == "computer":
                Game.handle_computer_turn()
                Game.check_death()
                if Game.computer_do:
                    if Game.repairs == 5:
                        if Game.count_round == 0:
                            Game.gui.show_turn_message('player_end')
                            break
                        else:
                            Game.count_round -= 1
                    Game.journal.add_entry("---НОВЫЙ РАУНД---")
                    # Game.gui.show_turn_message("player")
                    Game.current_turn = "player"
                    Game.computer_do = False

            Game.gui.render()



        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game.run()