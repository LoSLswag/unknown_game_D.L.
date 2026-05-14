import pygame as pg 
import biome as bm
import sys 
import math  
import random 
import time 
from enum import Enum 
import settings 
# Инициализация Pg 
pg.init() 
 
# Настройки экрана 

CELL_SIZE = 64 
CHUNK_SIZE = 16  # Размер чанка в тайлах 
map_test = {} 

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
player_size = pg.Rect(WIDTH // 2, HEIGHT // 2, CELL_SIZE, CELL_SIZE) 
speed = 500 

# Камера 
camera_x0, camera_y0 = 0, 0 

class App:
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.biomes = bm.Biomes(app=self.screen, pg=pg)

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.biomes.main_render_biomes()

            self.clock.tick(settings.FPS)
            pg.display.set_caption(f'FPS: {self.clock.get_fps()}')




class BiomesType(Enum):
    SEA = 0
    LAND = 1
    SAND = 2
    SEA_SHORE = 3
    WOODS = 4

class Biomes:
    def __init__(self, app, pg):
        self.app = app
        self.pg = pg
        self.matrix = self.create_start_matrix()

    def main_render_biomes(self):
        start = time.time()
        self.set_layout_lands_and_sea()
        self.set_layout_sea_shore()
        self.set_layout_woods()
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
        for x in range(rows):
            for y in range(cols):
                neighbors = self.count_neighbors(x, y, new_biome)
                if self.matrix[x][y] == target_biome and neighbors in rules:
                    self.matrix[x][y] = new_biome
                    self.paint_pixel_element(new_biome, x, y)
        self.pg.display.update()

    def next_sand_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.SAND) >= 5 and random.randint(1,50)==1:
                        self.matrix[x][y] = BiomesType.SAND
                        self.paint_pixel_element(BiomesType.SAND, x, y)
        self.pg.display.update()

    # -------------------- SEA SHORE --------------------
    def set_layout_sea_shore(self):
        self.start_border(BiomesType.SEA, BiomesType.SAND, BiomesType.SEA_SHORE, 1)
        for _ in range(50):
            self.next_sea_shore_gen()

    def next_sea_shore_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self.count_neighbors(x, y, BiomesType.SEA_SHORE) >= 4 and random.randint(1,30)==1:
                        self.matrix[x][y] = BiomesType.SEA_SHORE
                        self.paint_pixel_element(BiomesType.SEA_SHORE, x, y)
        self.pg.display.update()

    # -------------------- WOODS --------------------
    def set_layout_woods(self):
        self.start_random_woods()
        for _ in range(20):
            self.next_generation(BiomesType.LAND, BiomesType.WOODS, [3,6,7,8])
            self.next_generation(BiomesType.WOODS, BiomesType.LAND, [3,6,7,8])

    def start_random_woods(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND and random.randint(1,2)==1:
                    self.matrix[x][y] = BiomesType.WOODS
                    self.paint_pixel_element(BiomesType.WOODS, x, y)

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

    def paint_pixel_element(self, biome, x, y):
        color = {
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SEA: settings.COLOR_SEA,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
            BiomesType.WOODS: settings.COLOR_WOODS
        }[biome]
        self.pg.draw.rect(self.app.screen, color,
                          (x*settings.basicX, y*settings.basicY, settings.basicX, settings.basicY))



# Загрузка спрайтов 
try: 
    original_img = pg.image.load('unknown_game_DL/sprite/sptite1.png').convert_alpha() 
except pg.error: 
    # Если файла нет, создаём тестовый спрайт (красный круг) 
    original_img = pg.Surface((CELL_SIZE, CELL_SIZE), pg.SRCALPHA) 

    pg.draw.circle(original_img, (255, 80, 80), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 3) 
    pg.draw.rect(original_img, (200, 200, 200), (0, 0, CELL_SIZE, CELL_SIZE), 2) 
sprite = pg.transform.smoothscale(original_img, (CELL_SIZE, CELL_SIZE)) 

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
     
    # Отрисовка 
    screen.fill(BLACK)  # Заполняем черным фоном 
     
    # Отрисовка стен 
    screen.blit(sprite, (wall1.x - camera_x0, wall1.y - camera_y0)) 
    screen.blit(sprite, (wall2.x - camera_x0, wall2.y - camera_y0)) 
     
    # Отрисовка игрока 
    screen.blit(sprite, (player_size.x - camera_x0, player_size.y - camera_y0)) 
     
    # Обновление экрана 
    pg.display.flip() 
     
    # Контроль FPS 
    clock.tick(120) 
app = App()
app.run() 
# Завершение игры 
pg.quit() 
sys.exit() 