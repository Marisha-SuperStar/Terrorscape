import pygame
import sys
import random

class GraphGenerator:
    def __init__(self, num_nodes_with_2_edges, num_nodes_with_3_edges, num_nodes_with_4_edges):
        self.num_nodes_with_2_edges = num_nodes_with_2_edges
        self.num_nodes_with_3_edges = num_nodes_with_3_edges
        self.num_nodes_with_4_edges = num_nodes_with_4_edges
        self.num_nodes = num_nodes_with_2_edges + num_nodes_with_3_edges + num_nodes_with_4_edges
        self.graph = {i: [] for i in range(self.num_nodes)}

    def generate_graph(self):
        degrees = (
            [2] * self.num_nodes_with_2_edges +
            [3] * self.num_nodes_with_3_edges +
            [4] * self.num_nodes_with_4_edges
        )
        random.shuffle(degrees)

        if not self.is_graphical(degrees):
            raise ValueError("Невозможно построить граф с заданными параметрами.")

        while sum(degrees) > 0:
            nodes = sorted(range(self.num_nodes), key=lambda x: degrees[x], reverse=True)
            node = nodes[0]
            for i in range(1, degrees[node] + 1):
                if i >= len(nodes):
                    raise ValueError("Невозможно построить граф: недостаточно вершин для соединения.")
                target = nodes[i]
                self.graph[node].append(target)
                self.graph[target].append(node)
                degrees[node] -= 1
                degrees[target] -= 1

        return self.graph

    def is_graphical(self, degrees):
        while True:
            degrees = [d for d in degrees if d != 0]
            if not degrees:
                return True

            degrees.sort(reverse=True)
            d = degrees.pop(0)

            if d > len(degrees):
                return False
            for i in range(d):
                degrees[i] -= 1

    def print_graph(self):
        for node, edges in self.graph.items():
            print(f"{node} -> {edges}")

class LocationNode:
    def __init__(self, name, region, x, y, width, height):
        self.name = name
        self.region = region
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen, font):
        region_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        color = region_colors[self.region]

        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 2)

        text = font.render(self.name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

def assign_regions(nodes):
    num_nodes = len(nodes)
    for i, node in enumerate(nodes):
        if i < num_nodes // 3:
            node.region = 0
        elif i < 2 * num_nodes // 3:
            node.region = 1
        else:
            node.region = 2

if __name__ == "__main__":
    num_nodes_with_2_edges = 4
    num_nodes_with_3_edges = 2
    num_nodes_with_4_edges = 2

    graph_generator = GraphGenerator(num_nodes_with_2_edges, num_nodes_with_3_edges, num_nodes_with_4_edges)
    graph = graph_generator.generate_graph()

    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Игровая карта")

    font = pygame.font.Font(None, 24)

    location_names = ["Кухня", "Гостиная", "Спальня", "Ванная", "Коридор", "Балкон", "Кабинет", "Кладовая", "Терраса"]

    # GRID_ROWS = 3
    GRID_COLS = 3
    NODE_WIDTH = 100
    NODE_HEIGHT = 60
    HORIZONTAL_SPACING = 50
    VERTICAL_SPACING = 50

    nodes = []
    for i in range(graph_generator.num_nodes):
        row = i // GRID_COLS
        col = i % GRID_COLS
        x = col * (NODE_WIDTH + HORIZONTAL_SPACING) + 50
        y = row * (NODE_HEIGHT + VERTICAL_SPACING) + 50
        name = location_names[i % len(location_names)]
        nodes.append(LocationNode(name, 0, x, y, NODE_WIDTH, NODE_HEIGHT))

    assign_regions(nodes)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        for node, edges in graph.items():
            start_node = nodes[node]
            for target in edges:
                end_node = nodes[target]
                pygame.draw.line(screen, (255, 255, 255),
                                 (start_node.x + start_node.width // 2, start_node.y + start_node.height // 2),
                                 (end_node.x + end_node.width // 2, end_node.y + end_node.height // 2), 2)

        for node in nodes:
            node.draw(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()