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
CHUNK_SIZE = 64  # Размер чанка в тайлах
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
pl_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0001.png")  # Замените на путь к вашему файлу
pl_sprite = pg.transform.scale(pl_sprite, (pl_si, pl_si))
player_size = pg.Rect(5 * pl_si, 5 * pl_si , pl_si, pl_si)
speed = 700  # Увеличил скорость для большого экрана

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
        # Создаем поверхность для всей карты
        rows, cols = settings.Rows, settings.Columns
        self.map_surface = pg.Surface((cols * CELL_SIZE, rows * CELL_SIZE))
        self.render_full_map()

    def render_full_map(self):
        """Отрисовывает всю карту на поверхность"""
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                self.paint_pixel_element(self.matrix[x][y], x, y, draw_on_surface=True)
    
    def main_render_biomes(self):
        start = time.time()
        self.set_layout_lands_and_sea()
        self.set_layout_sands()
        self.set_layout_sea_shore()
        self.set_layout_woods()
        self.render_full_map()  # Перерисовываем карту после изменений
        print(f'Render Time is {time.time() - start:.2f}s')

    # -------------------- LAND & SEA --------------------
    def set_layout_lands_and_sea(self):
        self.matrix = self.create_start_matrix()
        for _ in range(settings.COUNTS_ALGORITHMS):
            self.next_generation(BiomesType.LAND, BiomesType.SEA, [3,6,7,8])
            self.next_generation(BiomesType.SEA, BiomesType.LAND, [3,6,7,8])

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
        new_matrix = [row[:] for row in self.matrix]  # Создаем копию
        
        for x in range(rows):
            for y in range(cols):
                neighbors = self.count_neighbors(x, y, new_biome)
                if self.matrix[x][y] == target_biome and neighbors in rules:
                    new_matrix[x][y] = new_biome
                    self.paint_pixel_element(new_biome, x, y)
        
        self.matrix = new_matrix
        self.pg.display.update()

    # -------------------- SAND --------------------
    def set_layout_sands(self):
        self.start_border(BiomesType.LAND, BiomesType.SEA, BiomesType.SAND, 1)
        for _ in range(settings.COUNTS_ALGORITHMS_SANDS):
            self.next_sand_gen()

    def start_border(self, target, neighbor, new_biome, min_neighbors=1):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == target:
                    if self.count_neighbors(x, y, neighbor) >= min_neighbors:
                        new_matrix[x][y] = new_biome
                        self.paint_pixel_element(new_biome, x, y)
        
        self.matrix = new_matrix
        self.pg.display.update()

    def next_sand_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.SAND) >= 5 and random.randint(1,50)==1:
                        new_matrix[x][y] = BiomesType.SAND
                        self.paint_pixel_element(BiomesType.SAND, x, y)
        
        self.matrix = new_matrix
        self.pg.display.update()

    # -------------------- SEA SHORE --------------------
    def set_layout_sea_shore(self):
        self.start_border(BiomesType.SEA, BiomesType.SAND, BiomesType.SEA_SHORE, 1)
        for _ in range(50):
            self.next_sea_shore_gen()

    def next_sea_shore_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.SEA_SHORE) >= 4 and random.randint(1,30)==1:
                        new_matrix[x][y] = BiomesType.SEA_SHORE
                        self.paint_pixel_element(BiomesType.SEA_SHORE, x, y)
        
        self.matrix = new_matrix
        self.pg.display.update()

    # -------------------- WOODS --------------------
    def set_layout_woods(self):
        self.start_random_woods()
        for _ in range(20):
            self.next_generation(BiomesType.LAND, BiomesType.WOODS, [3,6,7,8])
            self.next_generation(BiomesType.WOODS, BiomesType.LAND, [3,6,7,8])

    def start_random_woods(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        new_matrix = [row[:] for row in self.matrix]
        
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND and random.randint(1,2)==1:
                    new_matrix[x][y] = BiomesType.WOODS
                    self.paint_pixel_element(BiomesType.WOODS, x, y)
        
        self.matrix = new_matrix

    # -------------------- UTILS --------------------
    def create_start_matrix(self):
        rows, cols = settings.Rows, settings.Columns
        matrix = [[BiomesType.SEA if random.randint(1,2)==1 else BiomesType.LAND
                   for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                self.paint_pixel_element(matrix[i][j], i, j)
        self.pg.display.update()
        return matrix

    def paint_pixel_element(self, biome, x, y, draw_on_surface=False):
        color = {
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SEA: settings.COLOR_SEA,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
            BiomesType.WOODS: settings.COLOR_WOODS
        }[biome]
        
        # Рисуем на поверхности карты
        pg.draw.rect(self.screen,color,
                    (y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Если нужно сразу на экран (для отладки)
        if not draw_on_surface:
            pg.draw.rect(self.screen, color,
                        (y * CELL_SIZE - camera_x0, x * CELL_SIZE - camera_y0, CELL_SIZE, CELL_SIZE))

    def draw(self, screen, camera_x, camera_y):
        """Отрисовывает видимую часть карты"""
        # Определяем видимую область
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

wall_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0002.jpg")  # Замените на путь к вашему файлу
wall_sprite = pg.transform.scale(wall_sprite, (CELL_SIZE, CELL_SIZE))


# Создаем несколько тестовых стен
wall1 = pg.Rect(5 * CELL_SIZE, 5 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
wall2 = pg.Rect(10 * CELL_SIZE, 10 * CELL_SIZE, CELL_SIZE, CELL_SIZE)


# Игровой цикл
clock = pg.time.Clock()
running = True

while running:
    dt = clock.tick(120) / 1000.0
    
    # Обработка событий
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            # Нажатие пробела для регенерации карты
            if event.key == pg.K_SPACE:
                biomes.main_render_biomes()
    
    # Сохраняем предыдущую позицию на случай коллизии
    old_x, old_y = player_size.x, player_size.y
    
    # Движение игрока
    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT] or keys[pg.K_a]: 
        player_size.x -= speed * dt
    if keys[pg.K_RIGHT] or keys[pg.K_d]: 
        player_size.x += speed * dt 
    if keys[pg.K_UP] or keys[pg.K_w]: 
        player_size.y -= speed * dt
    if keys[pg.K_DOWN] or keys[pg.K_s]: 
        player_size.y += speed * dt
    
    # Проверка коллизии со стенами
    if player_size.colliderect(wall1) or player_size.colliderect(wall2):
        # Откатываем позицию, чтобы игрок не "заходил" внутрь стены
        player_size.x, player_size.y = old_x, old_y
    
    # Обновление камеры (следим за игроком)
    camera_x0 = player_size.x - WIDTH // 2
    camera_y0 = player_size.y - HEIGHT // 2
    
    # Ограничиваем камеру границами карты
    max_camera_x = max(0, settings.Columns * CELL_SIZE - WIDTH)
    max_camera_y = max(0, settings.Rows * CELL_SIZE - HEIGHT)
    camera_x0 = max(0, min(camera_x0, max_camera_x))
    camera_y0 = max(0, min(camera_y0, max_camera_y))
    
    # Отрисовка
    screen.fill(BLACK)  # Заполняем черным фоном
    
    # Отрисовка биомов с учетом камеры
    biomes.draw(screen, camera_x0, camera_y0)
    
    # Отрисовка стен
    screen.blit(wall_sprite, wall1)
    screen.blit(wall_sprite, wall2)
    
    # Отрисовка игрока
    screen.blit(pl_sprite, player_size)
    
    # Обновление экрана
    pg.display.flip()
    
    # Контроль FPS
    clock.tick(120)

# Завершение игры
pg.quit()
sys.exit()