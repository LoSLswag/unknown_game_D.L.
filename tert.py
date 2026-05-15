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
CELL_SIZE = 128
CHUNK_SIZE = 32
map_test = {}
sprites = {}

# Создаем полноэкранное окно
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pg.display.set_caption("Game")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
WATER_BLUE = (64, 164, 223)
GRAY = (128, 128, 128)
GRID_LINE_COLOR = (50, 50, 50)

# Игрок
pl_si = 64
try:
    pl_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0001.png")
    pl_sprite = pg.transform.scale(pl_sprite, (pl_si, pl_si))
except:
    pl_sprite = pg.Surface((pl_si, pl_si))
    pl_sprite.fill(RED)

player_size = pg.Rect(5 * pl_si, 5 * pl_si, pl_si, pl_si)
speed = 8000

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

    def main_render_biomes(self):
        start = time.time()
        self.set_layout_lands_and_sea()
        self.set_layout_sands()
        self.set_layout_sea_shore()
        self.set_layout_woods()
        print(f'Render Time is {time.time() - start:.2f}s')

    # -------------------- LAND & SEA --------------------
    def set_layout_lands_and_sea(self):
        """Генерация земли и моря с правильными правилами"""
        self.matrix = self.create_start_matrix()
        for _ in range(settings.COUNTS_ALGORITHMS):
            # Исправленные правила: земля появляется у земли, море у моря
            self.next_generation(BiomesType.SEA, BiomesType.LAND, [4,5,6,7,8])  # Море -> Земля
            self.next_generation(BiomesType.LAND, BiomesType.SEA, [3,4,5])       # Земля -> Море

    # -------------------- GENERIC --------------------
    def count_neighbors(self, x, y, biome_type):
        count = 0
        rows, cols = len(self.matrix), len(self.matrix[0])
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x+dx, y+dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if self.matrix[nx][ny] == biome_type:
                        count += 1
        return count

    def next_generation(self, target_biome, new_biome, rules):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                neighbors = self.count_neighbors(x, y, new_biome)
                if self.matrix[x][y] == target_biome and neighbors in rules:
                    new_matrix[x][y] = new_biome
        
        self.matrix = new_matrix

    # -------------------- SAND --------------------
    def set_layout_sands(self):
        """Более мягкая генерация песка - только у границ воды"""
        # Песок только на границе земли и моря
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[0])):
                if self.matrix[x][y] == BiomesType.LAND:
                    # Проверяем соседей на наличие моря
                    if self.count_neighbors(x, y, BiomesType.SEA) >= 1:
                        self.matrix[x][y] = BiomesType.SAND
                        self.paint_pixel_element(BiomesType.SAND, x, y)
        
        # Несколько проходов для сглаживания песка (уменьшено количество)
        for _ in range(min(settings.COUNTS_ALGORITHMS_SANDS, 3)):
            self.next_sand_gen()

    def start_border(self, target, neighbor, new_biome, min_neighbors=1):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == target:
                    if self.count_neighbors(x, y, neighbor) >= min_neighbors:
                        new_matrix[x][y] = new_biome
        
        self.matrix = new_matrix

    def next_sand_gen(self):
        """Мягкое распространение песка"""
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND:
                    if self.count_neighbors(x, y, BiomesType.SAND) >= 3 and random.randint(1,100) <= 20:
                        new_matrix[x][y] = BiomesType.SAND
        
        self.matrix = new_matrix

    # -------------------- SEA SHORE --------------------
    def set_layout_sea_shore(self):
        """Мелководье у берегов"""
        self.start_border(BiomesType.SEA, BiomesType.SAND, BiomesType.SEA_SHORE, 1)
        for _ in range(20):  # Уменьшено количество итераций
            self.next_sea_shore_gen()

    def next_sea_shore_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.SEA_SHORE) >= 3 and random.randint(1,100) <= 25:
                        new_matrix[x][y] = BiomesType.SEA_SHORE
        
        self.matrix = new_matrix

    # -------------------- WOODS --------------------
    def set_layout_woods(self):
        """Леса только на земле, не на песке"""
        # Леса только на земле (не на песке и не на мелководье)
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[0])):
                if self.matrix[x][y] == BiomesType.LAND and random.randint(1,3) == 1:
                    self.matrix[x][y] = BiomesType.WOODS
                    self.paint_pixel_element(BiomesType.WOODS, x, y)
        
        # Уменьшено количество итераций для лесов
        for _ in range(10):
            self.next_generation(BiomesType.LAND, BiomesType.WOODS, [4,5,6,7,8])
            self.next_generation(BiomesType.WOODS, BiomesType.LAND, [1,2,3])

    def start_random_woods(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND and random.randint(1,3) == 1:
                    new_matrix[x][y] = BiomesType.WOODS
        
        self.matrix = new_matrix

    # -------------------- UTILS --------------------
    def create_start_matrix(self):
        """Создание начальной матрицы с большим количеством земли"""
        rows, cols = settings.Rows, settings.Columns
        # 60% земли, 40% моря (вместо 50/50)
        matrix = [[BiomesType.SEA if random.randint(1,100) <= 40 else BiomesType.LAND
                   for _ in range(cols)] for _ in range(rows)]
        
        # Рисуем начальную карту
        for i in range(rows):
            for j in range(cols):
                self.paint_pixel_element(matrix[i][j], i, j)
        
        self.pg.display.update()
        return matrix

    def paint_pixel_element(self, biome, x, y):
        color = {
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SEA: settings.COLOR_SEA,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
            BiomesType.WOODS: settings.COLOR_WOODS
        }[biome]
        
        pg.draw.rect(self.screen, color,
                    (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw(self, screen, camera_x, camera_y):
        """Отрисовывает видимую часть карты"""
        start_x = max(0, camera_x // CELL_SIZE)
        start_y = max(0, camera_y // CELL_SIZE)
        end_x = min(len(self.matrix[0]), (camera_x + WIDTH) // CELL_SIZE + 2)
        end_y = min(len(self.matrix), (camera_y + HEIGHT) // CELL_SIZE + 2)
        
        for x in range(start_y, end_y):
            for y in range(start_x, end_x):
                if 0 <= x < len(self.matrix) and 0 <= y < len(self.matrix[0]):
                    screen_x = y * CELL_SIZE - camera_x
                    screen_y = x * CELL_SIZE - camera_y
                    if -CELL_SIZE <= screen_x < WIDTH and -CELL_SIZE <= screen_y < HEIGHT:
                        color = {
                            BiomesType.LAND: settings.COLOR_LAND,
                            BiomesType.SEA: settings.COLOR_SEA,
                            BiomesType.SAND: settings.COLOR_SAND,
                            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
                            BiomesType.WOODS: settings.COLOR_WOODS
                        }[self.matrix[x][y]]
                        pg.draw.rect(screen, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))

# Создаем экземпляр биомов
biomes = Biomes(screen, pg)
biomes.main_render_biomes()

# Загрузка спрайта стены
try:
    wall_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0002.jpg")
    wall_sprite = pg.transform.scale(wall_sprite, (CELL_SIZE, CELL_SIZE))
except:
    wall_sprite = pg.Surface((CELL_SIZE, CELL_SIZE))
    wall_sprite.fill(GRAY)

# Создаем стены
wall1 = pg.Rect(5 * CELL_SIZE, 5 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
wall2 = pg.Rect(10 * CELL_SIZE, 10 * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# Игровой цикл
clock = pg.time.Clock()
running = True

while running:
    dt = clock.tick(120) / 1000.0
    
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
    
    max_camera_x = max(0, settings.Columns * CELL_SIZE - WIDTH)
    max_camera_y = max(0, settings.Rows * CELL_SIZE - HEIGHT)
    camera_x0 = max(0, min(camera_x0, max_camera_x))
    camera_y0 = max(0, min(camera_y0, max_camera_y))
    
    # Отрисовка
    screen.fill(BLACK)
    biomes.draw(screen, camera_x0, camera_y0)
    
    # Отрисовка стен с учетом камеры
    screen.blit(wall_sprite, (wall1.x - camera_x0, wall1.y - camera_y0))
    screen.blit(wall_sprite, (wall2.x - camera_x0, wall2.y - camera_y0))
    
    # Отрисовка игрока (уже с учетом камеры через player_size)
    screen.blit(pl_sprite, (player_size.x - camera_x0, player_size.y - camera_y0))
    
    pg.display.flip()
    clock.tick(120)

pg.quit()
sys.exit()