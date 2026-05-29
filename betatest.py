import pygame as pg
import sys
import math 
import random
import settings
from enum import Enum
import time
from collections import defaultdict

# Инициализация Pygame
pg.init()

# Настройки экрана
CELL_SIZE = 32  # Размер тайла
CHUNK_SIZE = 16  # Размер чанка в тайлах (16x16 тайлов)
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
    pl_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0001.png")
    pl_sprite = pg.transform.scale(pl_sprite, (pl_si, pl_si))
except:
    pl_sprite = pg.Surface((pl_si, pl_si))
    pl_sprite.fill(RED)

player_size = pg.Rect(5 * pl_si, 5 * pl_si, pl_si, pl_si)
speed = 700

# Камера
camera_x0, camera_y0 = 0, 0

class BiomesType(Enum):
    OCEAN = 0
    SEA = 1
    LAND = 2
    SAND = 3
    WOODS = 4

class Chunk:
    """Класс чанка - содержит тайлы и спрайты"""
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.tiles = {}  # Словарь {(x, y): biome_type}
        self.sprites = {}  # Словарь {(x, y): sprite} для объектов
        self.is_loaded = False
        
    def add_sprite(self, x, y, sprite):
        """Добавить спрайт в чанк"""
        self.sprites[(x, y)] = sprite
        
    def remove_sprite(self, x, y):
        """Удалить спрайт из чанка"""
        if (x, y) in self.sprites:
            del self.sprites[(x, y)]
    
    def get_sprite(self, x, y):
        """Получить спрайт из чанка"""
        return self.sprites.get((x, y))
    
    def set_tile(self, x, y, biome):
        """Установить тайл в чанке"""
        self.tiles[(x, y)] = biome
        
    def get_tile(self, x, y):
        """Получить тайл из чанка"""
        return self.tiles.get((x, y))

class World:
    """Мир, состоящий из чанков"""
    def __init__(self):
        self.chunks = {}  # Словарь {(chunk_x, chunk_y): Chunk}
        self.loaded_chunks = set()  # Загруженные чанки
        
    def get_chunk_coords(self, x, y):
        """Получить координаты чанка для тайла"""
        chunk_x = x // CHUNK_SIZE
        chunk_y = y // CHUNK_SIZE
        return chunk_x, chunk_y
    
    def get_chunk(self, chunk_x, chunk_y):
        """Получить чанк, создать если не существует"""
        key = (chunk_x, chunk_y)
        if key not in self.chunks:
            self.chunks[key] = Chunk(chunk_x, chunk_y)
        return self.chunks[key]
    
    def set_tile(self, x, y, biome):
        """Установить тип тайла"""
        chunk_x, chunk_y = self.get_chunk_coords(x, y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        local_x = x % CHUNK_SIZE
        local_y = y % CHUNK_SIZE
        chunk.set_tile(local_x, local_y, biome)
    
    def get_tile(self, x, y):
        """Получить тип тайла"""
        chunk_x, chunk_y = self.get_chunk_coords(x, y)
        key = (chunk_x, chunk_y)
        if key in self.chunks:
            chunk = self.chunks[key]
            local_x = x % CHUNK_SIZE
            local_y = y % CHUNK_SIZE
            return chunk.get_tile(local_x, local_y)
        return None
    
    def add_sprite_to_chunk(self, x, y, sprite):
        """Добавить спрайт в чанк"""
        chunk_x, chunk_y = self.get_chunk_coords(x, y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        local_x = x % CHUNK_SIZE
        local_y = y % CHUNK_SIZE
        chunk.add_sprite(local_x, local_y, sprite)
    
    def get_sprite_from_chunk(self, x, y):
        """Получить спрайт из чанка"""
        chunk_x, chunk_y = self.get_chunk_coords(x, y)
        key = (chunk_x, chunk_y)
        if key in self.chunks:
            chunk = self.chunks[key]
            local_x = x % CHUNK_SIZE
            local_y = y % CHUNK_SIZE
            return chunk.get_sprite(local_x, local_y)
        return None
    
    def update_loaded_chunks(self, center_x, center_y, radius=3):
        """Обновить загруженные чанки вокруг игрока"""
        chunk_x, chunk_y = self.get_chunk_coords(center_x, center_y)
        new_loaded = set()
        
        # Загружаем чанки в радиусе
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cx, cy = chunk_x + dx, chunk_y + dy
                new_loaded.add((cx, cy))
                # Создаем чанк если его нет
                self.get_chunk(cx, cy)
        
        # Выгружаем дальние чанки
        for chunk_key in self.loaded_chunks - new_loaded:
            if chunk_key in self.chunks:
                self.chunks[chunk_key].is_loaded = False
                # Опционально: очищаем спрайты для экономии памяти
                self.chunks[chunk_key].sprites.clear()
        
        self.loaded_chunks = new_loaded
        for chunk_key in self.loaded_chunks:
            self.chunks[chunk_key].is_loaded = True
    
    def draw(self, screen, camera_x, camera_y):
        """Отрисовка только загруженных чанков"""
        rows, cols = settings.Rows, settings.Columns
        
        # Определяем видимые границы в тайлах
        start_x = max(0, camera_x // CELL_SIZE)
        start_y = max(0, camera_y // CELL_SIZE)
        end_x = min(cols, (camera_x + WIDTH) // CELL_SIZE + 2)
        end_y = min(rows, (camera_y + HEIGHT) // CELL_SIZE + 2)
        
        # Отрисовываем только видимые тайлы
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                biome = self.get_tile(x, y)
                if biome is not None:
                    screen_x = x * CELL_SIZE - camera_x
                    screen_y = y * CELL_SIZE - camera_y
                    
                    if -CELL_SIZE <= screen_x < WIDTH and -CELL_SIZE <= screen_y < HEIGHT:
                        # Отрисовка тайла
                        color = self.get_biome_color(biome)
                        pg.draw.rect(screen, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
                        
                        # Отрисовка спрайта на тайле (если есть)
                        sprite = self.get_sprite_from_chunk(x, y)
                        if sprite:
                            screen.blit(sprite, (screen_x, screen_y))
    
    def get_biome_color(self, biome):
        """Получить цвет биома"""
        colors = {
            BiomesType.OCEAN: (0, 50, 150),
            BiomesType.SEA: (64, 164, 223),
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.WOODS: settings.COLOR_WOODS
        }
        return colors.get(biome, BLACK)

class BiomesGenerator:
    """Генератор биомов для мира"""
    def __init__(self, world):
        self.world = world
    
    def generate_ocean_and_land(self):
        """Создание океана и континентов"""
        rows, cols = settings.Rows, settings.Columns
        
        # Шаг 1: Создаем базовую карту с океаном
        matrix = [[BiomesType.OCEAN for _ in range(cols)] for _ in range(rows)]
        
        # Создаем континенты
        num_continents = random.randint(3, 6)
        continent_centers = []
        
        for _ in range(num_continents):
            center_x = random.randint(cols // 4, 3 * cols // 4)
            center_y = random.randint(rows // 4, 3 * rows // 4)
            radius = random.randint(min(rows, cols) // 8, min(rows, cols) // 4)
            continent_centers.append((center_y, center_x, radius))
        
        # Заполняем континенты
        for x in range(rows):
            for y in range(cols):
                for cx, cy, radius in continent_centers:
                    distance = math.sqrt((x - cx)**2 + (y - cy)**2)
                    if distance < radius:
                        matrix[x][y] = BiomesType.LAND
                        break
        
        # Добавляем острова
        for x in range(rows):
            for y in range(cols):
                if matrix[x][y] == BiomesType.OCEAN and random.randint(1, 100) <= 5:
                    matrix[x][y] = BiomesType.LAND
        
        # Шаг 2: Сохраняем в мир
        for x in range(rows):
            for y in range(cols):
                self.world.set_tile(x, y, matrix[x][y])
        
        # Шаг 3: Создаем моря и пляжи
        self.create_seas_and_beaches()
        
        # Шаг 4: Создаем леса
        self.create_forests()
    
    def create_seas_and_beaches(self):
        """Создание морей и пляжей"""
        rows, cols = settings.Rows, settings.Columns
        
        # Копируем текущую карту
        matrix = [[self.world.get_tile(x, y) for y in range(cols)] for x in range(rows)]
        
        # Создаем моря (мелководье) и пляжи
        for x in range(rows):
            for y in range(cols):
                if matrix[x][y] == BiomesType.OCEAN:
                    # Проверяем соседей на наличие суши
                    has_land_nearby = False
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < rows and 0 <= ny < cols:
                                if matrix[nx][ny] == BiomesType.LAND:
                                    has_land_nearby = True
                                    break
                        if has_land_nearby:
                            break
                    
                    if has_land_nearby:
                        self.world.set_tile(x, y, BiomesType.SEA)
                
                elif matrix[x][y] == BiomesType.LAND:
                    # Проверяем соседей на наличие воды
                    has_water_nearby = False
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < rows and 0 <= ny < cols:
                                if matrix[nx][ny] in [BiomesType.OCEAN, BiomesType.SEA]:
                                    has_water_nearby = True
                                    break
                        if has_water_nearby:
                            break
                    
                    if has_water_nearby:
                        self.world.set_tile(x, y, BiomesType.SAND)
    
    def create_forests(self):
        """Создание лесов"""
        rows, cols = settings.Rows, settings.Columns
        
        for x in range(rows):
            for y in range(cols):
                if self.world.get_tile(x, y) == BiomesType.LAND:
                    if random.randint(1, 3) == 1:
                        self.world.set_tile(x, y, BiomesType.WOODS)

# Создаем мир и генератор
world = World()
generator = BiomesGenerator(world)
generator.generate_ocean_and_land()

# Загрузка спрайтов объектов
try:
    # Спрайты для разных объектов
    tree_sprite = pg.image.load("unknown_game_DL/sprite/tree.png")
    tree_sprite = pg.transform.scale(tree_sprite, (CELL_SIZE, CELL_SIZE))
    
    rock_sprite = pg.image.load("unknown_game_DL/sprite/rock.png")
    rock_sprite = pg.transform.scale(rock_sprite, (CELL_SIZE, CELL_SIZE))
    
    wall_sprite = pg.image.load("unknown_game_DL/sprite/Sprite-0002.jpg")
    wall_sprite = pg.transform.scale(wall_sprite, (CELL_SIZE, CELL_SIZE))
except:
    # Создаем простые спрайты если нет файлов
    tree_sprite = pg.Surface((CELL_SIZE, CELL_SIZE))
    tree_sprite.fill((0, 150, 0))
    
    rock_sprite = pg.Surface((CELL_SIZE, CELL_SIZE))
    rock_sprite.fill((100, 100, 100))
    
    wall_sprite = pg.Surface((CELL_SIZE, CELL_SIZE))
    wall_sprite.fill(GRAY)

# Добавляем спрайты на карту (деревья на лесах)
rows, cols = settings.Rows, settings.Columns
for x in range(rows):
    for y in range(cols):
        if world.get_tile(x, y) == BiomesType.WOODS:
            # Добавляем дерево с 30% шансом
            if random.randint(1, 100) <= 30:
                world.add_sprite_to_chunk(x, y, tree_sprite)
        elif world.get_tile(x, y) == BiomesType.SAND and random.randint(1, 100) <= 10:
            # Добавляем камни на пляж
            world.add_sprite_to_chunk(x, y, rock_sprite)

# Стены как отдельные объекты со спрайтами
wall1_x, wall1_y = 5, 5
wall2_x, wall2_y = 10, 10
world.add_sprite_to_chunk(wall1_x, wall1_y, wall_sprite)
world.add_sprite_to_chunk(wall2_x, wall2_y, wall_sprite)

# Позиция игрока в тайлах
player_tile_x = 5 * pl_si // CELL_SIZE
player_tile_y = 5 * pl_si // CELL_SIZE

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
    
    # Сохраняем позицию
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
    
    # Обновляем загруженные чанки вокруг игрока
    player_tile_x = player_size.x // CELL_SIZE
    player_tile_y = player_size.y // CELL_SIZE
    world.update_loaded_chunks(player_tile_x, player_tile_y, radius=3)
    
    # Камера
    camera_x0 = player_size.x - WIDTH // 2
    camera_y0 = player_size.y - HEIGHT // 2
    
    max_camera_x = max(0, settings.Columns * CELL_SIZE - WIDTH)
    max_camera_y = max(0, settings.Rows * CELL_SIZE - HEIGHT)
    camera_x0 = max(0, min(camera_x0, max_camera_x))
    camera_y0 = max(0, min(camera_y0, max_camera_y))
    
    # Отрисовка
    screen.fill(BLACK)
    world.draw(screen, camera_x0, camera_y0)
    
    # Отрисовка игрока
    screen.blit(pl_sprite, (player_size.x - camera_x0, player_size.y - camera_y0))
    
    # Отладочная информация
    font = pg.font.Font(None, 24)
    debug_text = font.render(f"Loaded chunks: {len(world.loaded_chunks)}", True, WHITE)
    screen.blit(debug_text, (10, 10))
    
    pg.display.flip()

pg.quit()
sys.exit()