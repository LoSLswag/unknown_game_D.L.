import pygame as pg
import sys
import math 
import random
import settings
from enum import Enum
import time

# Инициализация Pygame
pg.init()

# Настройки экрана
CELL_SIZE = 256
CHUNK_SIZE = 32
map_test = {}
sprites = {}

# Создаем полноэкранное окно
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pg.display.set_caption("Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# Игрок
pl_si = 64
try:
    pl_sprite = pg.image.load("unknown_game_DL/sprite/player.jpg")
    pl_sprite = pg.transform.scale(pl_sprite, (pl_si, pl_si))
except:
    pl_sprite = pg.Surface((pl_si, pl_si))
    pl_sprite.fill(RED)

player_size = pg.Rect(5 * pl_si, 5 * pl_si, pl_si, pl_si)
speed = 750

# Камера
camera_x0, camera_y0 = 0, 0

class BiomesType(Enum):
    SEA = 0
    LAND = 1
    SAND = 2
    SEA_SHORE = 3
    WOODS = 4

class Biomes:
    def __init__(self, screen, pg):
        self.screen = screen
        self.pg = pg
        self.matrix = self.create_start_matrix()
        self.trees = []  # Список деревьев
        
    def main_render_biomes(self):
        start = time.time()
        self.set_layout_lands_and_sea()
        self.set_layout_beaches()
        self.set_layout_woods()
        print(f'Render Time is {time.time() - start:.2f}s')
        self.print_stats()

    def print_stats(self):
        stats = {
            BiomesType.SEA: 0,
            BiomesType.LAND: 0,
            BiomesType.SAND: 0,
            BiomesType.SEA_SHORE: 0,
            BiomesType.WOODS: 0
        }
        
        for row in self.matrix:
            for cell in row:
                stats[cell] += 1
        
        total = sum(stats.values())
        print(f"\n=== СТАТИСТИКА БИОМОВ ===")
        print(f"Море: {stats[BiomesType.SEA]} ({stats[BiomesType.SEA]/total*100:.1f}%)")
        print(f"Земля: {stats[BiomesType.LAND]} ({stats[BiomesType.LAND]/total*100:.1f}%)")
        print(f"Песок: {stats[BiomesType.SAND]} ({stats[BiomesType.SAND]/total*100:.1f}%)")
        print(f"Лес: {stats[BiomesType.WOODS]} ({stats[BiomesType.WOODS]/total*100:.1f}%)")
        print(f"Деревьев: {len(self.trees)}")

    def set_layout_lands_and_sea(self):
        for _ in range(settings.COUNTS_ALGORITHMS):
            self.next_generation(BiomesType.SEA, BiomesType.LAND, [5,6,7,8])
            self.next_generation(BiomesType.LAND, BiomesType.SEA, [4,6,7,8])
    
    def count_neighbors(self, x, y, biome_type):
        count = 0
        rows, cols = len(self.matrix), len(self.matrix[0])
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if self.matrix[nx][ny] == biome_type:
                        count += 1
        return count

    def next_generation(self, target_biome, new_biome, rules):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == target_biome:
                    neighbors = self.count_neighbors(x, y, new_biome)
                    if neighbors in rules:
                        new_matrix[x][y] = new_biome
        
        self.matrix = new_matrix

    def set_layout_beaches(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.LAND) >= 1:
                        self.matrix[x][y] = BiomesType.SEA_SHORE
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND:
                    if self.count_neighbors(x, y, BiomesType.SEA) >= 1 or \
                       self.count_neighbors(x, y, BiomesType.SEA_SHORE) >= 1:
                        self.matrix[x][y] = BiomesType.SAND

    def set_layout_woods(self):
        """Создание маленьких деревьев на земле"""
        rows, cols = len(self.matrix), len(self.matrix[0])
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND:
                    # 25% шанс что здесь будет дерево
                    if random.randint(1, 100) <= 25:
                        # Размер дерева - МАЛЕНЬКИЙ (20-40 пикселей, а не 256)
                        tree_size = random.randint(20, 40)
                        # Смещение внутри тайла
                        offset_x = random.randint(0, CELL_SIZE - tree_size)
                        offset_y = random.randint(0, CELL_SIZE - tree_size)
                        self.trees.append((x, y, tree_size, offset_x, offset_y))
                    
                elif self.matrix[x][y] == BiomesType.WOODS:
                    # В лесу больше деревьев (3-6 штук)
                    num_trees = random.randint(3, 6)
                    for _ in range(num_trees):
                        tree_size = random.randint(20, 40)
                        offset_x = random.randint(0, CELL_SIZE - tree_size)
                        offset_y = random.randint(0, CELL_SIZE - tree_size)
                        self.trees.append((x, y, tree_size, offset_x, offset_y))

    def draw_trees(self, screen, camera_x, camera_y):
        """Рисует все маленькие деревья"""
        for x, y, size, offset_x, offset_y in self.trees:
            # Позиция на экране
            screen_x = y * CELL_SIZE - camera_x + offset_x
            screen_y = x * CELL_SIZE - camera_y + offset_y
            
            # Рисуем только если видно на экране
            if -size < screen_x < WIDTH + size and -size < screen_y < HEIGHT + size:
                # Ствол
                trunk_w = max(3, size // 5)
                trunk_h = size // 3
                trunk_x = screen_x + (size - trunk_w) // 2
                trunk_y = screen_y + size - trunk_h
                pg.draw.rect(screen, (101, 67, 33), (trunk_x, trunk_y, trunk_w, trunk_h))
                
                # Крона (круг)
                pg.draw.circle(screen, (34, 139, 34), 
                             (screen_x + size//2, screen_y + size//2), 
                             size//2)

    def create_start_matrix(self):
        rows, cols = settings.Rows, settings.Columns
        matrix = []
        for x in range(rows):
            row = []
            for y in range(cols):
                if random.randint(1, 100) <= 50:
                    row.append(BiomesType.LAND)
                else:
                    row.append(BiomesType.SEA)
            matrix.append(row)
        return matrix

    def get_color(self, biome):
        colors = {
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SEA: settings.COLOR_SEA,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
            BiomesType.WOODS: settings.COLOR_WOODS
        }
        return colors.get(biome, BLACK)

    def draw(self, screen, camera_x, camera_y):
        rows, cols = len(self.matrix), len(self.matrix[0])
        
        start_x = max(0, camera_x // CELL_SIZE)
        start_y = max(0, camera_y // CELL_SIZE)
        end_x = min(cols, (camera_x + WIDTH) // CELL_SIZE + 2)
        end_y = min(rows, (camera_y + HEIGHT) // CELL_SIZE + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * CELL_SIZE - camera_x
                screen_y = y * CELL_SIZE - camera_y
                
                if -CELL_SIZE <= screen_x < WIDTH and -CELL_SIZE <= screen_y < HEIGHT:
                    color = self.get_color(self.matrix[y][x])
                    pg.draw.rect(screen, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        
        # Рисуем деревья поверх земли
        self.draw_trees(screen, camera_x, camera_y)

# Создаем экземпляр биомов
print("Создание карты...")
biomes = Biomes(screen, pg)
biomes.main_render_biomes()

# Загрузка спрайта стены
try:
    wall_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0002.jpg")
    wall_sprite = pg.transform.scale(wall_sprite, (CELL_SIZE, CELL_SIZE))
except:
    wall_sprite = pg.Surface((CELL_SIZE, CELL_SIZE))
    wall_sprite.fill(GRAY)

# Стены
wall1 = pg.Rect(5 * CELL_SIZE, 5 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
wall2 = pg.Rect(10 * CELL_SIZE, 10 * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# Игровой цикл
clock = pg.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
    
    old_x, old_y = player_size.x, player_size.y
    
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT] or keys[pg.K_a]: 
        player_size.x -= speed * dt
    if keys[pg.K_RIGHT] or keys[pg.K_d]: 
        player_size.x += speed * dt 
    if keys[pg.K_UP] or keys[pg.K_w]: 
        player_size.y -= speed * dt
    if keys[pg.K_DOWN] or keys[pg.K_s]: 
        player_size.y += speed * dt
    
    # Коллизии
    if player_size.colliderect(wall1) or player_size.colliderect(wall2):
        player_size.x, player_size.y = old_x, old_y
    
    # Камера
    camera_x0 = player_size.x - WIDTH // 2
    camera_y0 = player_size.y - HEIGHT // 2
    
    max_camera_x = max(0, len(biomes.matrix[0]) * CELL_SIZE - WIDTH)
    max_camera_y = max(0, len(biomes.matrix) * CELL_SIZE - HEIGHT)
    camera_x0 = max(0, min(camera_x0, max_camera_x))
    camera_y0 = max(0, min(camera_y0, max_camera_y))
    
    # Отрисовка
    screen.fill(BLACK)
    biomes.draw(screen, camera_x0, camera_y0)
    
    # Стены
    screen.blit(wall_sprite, (wall1.x - camera_x0, wall1.y - camera_y0))
    screen.blit(wall_sprite, (wall2.x - camera_x0, wall2.y - camera_y0))
    
    # Игрок
    screen.blit(pl_sprite, (player_size.x - camera_x0, player_size.y - camera_y0))
    
    pg.display.flip()

pg.quit()
sys.exit()