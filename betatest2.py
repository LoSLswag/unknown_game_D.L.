# main.py
import pygame as pg
import sys
import random
import time
from enum import Enum

# ==================== НАСТРОЙКИ (вместо settings.py) ====================
class Settings:
    # Экран
    RES = (1280, 720)  # Ширина, Высота (если FULLSCREEN не нужен)
    FPS = 60
    FULLSCREEN = True
    
    # Карта
    Rows = 100
    Columns = 100
    basicX = 8
    basicY = 8
    COUNTS_ALGORITHMS = 5
    COUNTS_ALGORITHMS_SANDS = 3
    
    # Цвета
    COLOR_LAND = (34, 139, 34)
    COLOR_SEA = (64, 164, 223)
    COLOR_SAND = (237, 201, 175)
    COLOR_SEA_SHORE = (189, 154, 122)
    COLOR_WOODS = (0, 100, 0)
    COLOR_PLAYER = (255, 50, 50)
    COLOR_WALL = (128, 128, 128)

settings = Settings()

# ==================== ИНИЦИАЛИЗАЦИЯ PYGAME ====================
pg.init()

if settings.FULLSCREEN:
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
else:
    screen = pg.display.set_mode(settings.RES)

WIDTH, HEIGHT = screen.get_size()
pg.display.set_caption("Biome Game")

# ==================== ENUMS ====================
class BiomesType(Enum):
    SEA = 0
    LAND = 1
    SAND = 2
    SEA_SHORE = 3
    WOODS = 4

# ==================== КЛАСС БИОМОВ ====================
class Biomes:
    def __init__(self, screen, pg_module):
        self.screen = screen
        self.pg = pg_module
        self.matrix = None

    def generate(self):
        """Полная генерация карты"""
        start = time.time()
        self.matrix = self._create_start_matrix()
        self._generate_lands_and_sea()
        self._generate_sands()
        self._generate_sea_shore()
        self._generate_woods()
        print(f'✅ Карта сгенерирована за {time.time() - start:.2f}s')

    def _create_start_matrix(self):
        return [[BiomesType.SEA if random.randint(1,2)==1 else BiomesType.LAND
                 for _ in range(settings.Columns)] for _ in range(settings.Rows)]

    def _count_neighbors(self, x, y, biome_type):
        count = 0
        rows, cols = len(self.matrix), len(self.matrix[0])
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx == 0 and dy == 0: continue
                nx, ny = x+dx, y+dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if self.matrix[nx][ny] == biome_type:
                        count += 1
        return count

    def _next_generation(self, target_biome, new_biome, rules):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                neighbors = self._count_neighbors(x, y, new_biome)
                if self.matrix[x][y] == target_biome and neighbors in rules:
                    self.matrix[x][y] = new_biome

    def _generate_lands_and_sea(self):
        for _ in range(settings.COUNTS_ALGORITHMS):
            self._next_generation(BiomesType.LAND, BiomesType.SEA, [3,6,7,8])
            self._next_generation(BiomesType.SEA, BiomesType.LAND, [3,6,7,8])

    def _generate_sands(self):
        self._start_border(BiomesType.LAND, BiomesType.SEA, BiomesType.SAND, 1)
        for _ in range(settings.COUNTS_ALGORITHMS_SANDS):
            self._next_sand_gen()

    def _start_border(self, target, neighbor, new_biome, min_neighbors=1):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == target:
                    if self._count_neighbors(x, y, neighbor) >= min_neighbors:
                        self.matrix[x][y] = new_biome

    def _next_sand_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self._count_neighbors(x, y, BiomesType.SAND) >= 5 and random.randint(1,50)==1:
                        self.matrix[x][y] = BiomesType.SAND

    def _generate_sea_shore(self):
        self._start_border(BiomesType.SEA, BiomesType.SAND, BiomesType.SEA_SHORE, 1)
        for _ in range(50):
            self._next_sea_shore_gen()

    def _next_sea_shore_gen(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.SEA:
                    if self._count_neighbors(x, y, BiomesType.SEA_SHORE) >= 4 and random.randint(1,30)==1:
                        self.matrix[x][y] = BiomesType.SEA_SHORE

    def _generate_woods(self):
        self._start_random_woods()
        for _ in range(20):
            self._next_generation(BiomesType.LAND, BiomesType.WOODS, [3,6,7,8])
            self._next_generation(BiomesType.WOODS, BiomesType.LAND, [3,6,7,8])

    def _start_random_woods(self):
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                if self.matrix[x][y] == BiomesType.LAND and random.randint(1,2)==1:
                    self.matrix[x][y] = BiomesType.WOODS

    def draw(self, camera_x, camera_y):
        """Отрисовка видимой части карты"""
        color_map = {
            BiomesType.LAND: settings.COLOR_LAND,
            BiomesType.SEA: settings.COLOR_SEA,
            BiomesType.SAND: settings.COLOR_SAND,
            BiomesType.SEA_SHORE: settings.COLOR_SEA_SHORE,
            BiomesType.WOODS: settings.COLOR_WOODS
        }
        rows, cols = len(self.matrix), len(self.matrix[0])
        for x in range(rows):
            for y in range(cols):
                draw_x = y * settings.basicX - camera_x
                draw_y = x * settings.basicY - camera_y
                # Оптимизация: рисуем только если в пределах экрана
                if (-settings.basicX < draw_x < WIDTH and -settings.basicY < draw_y < HEIGHT):
                    color = color_map.get(self.matrix[x][y], (0,0,0))
                    self.pg.draw.rect(self.screen, color,
                                      (draw_x, draw_y, settings.basicX, settings.basicY))

# ==================== ЗАГРУЗКА СПРАЙТА ====================
def load_sprite():
    """Загружает спрайт или создаёт заглушку"""
    paths = [
        'unknown_game_DL/sprite/sprite1.png',  # Исправлено: sprite (не sptite)
        'sprite/sprite1.png',
        'sprite1.png'
    ]
    for path in paths:
        try:
            img = pg.image.load(path).convert_alpha()
            return pg.transform.smoothscale(img, (settings.basicX * 2, settings.basicY * 2))
        except (pg.error, FileNotFoundError):
            continue
    # Заглушка, если файл не найден
    surf = pg.Surface((settings.basicX * 2, settings.basicY * 2), pg.SRCALPHA)
    pg.draw.circle(surf, (255, 80, 80), (settings.basicX, settings.basicY), settings.basicX)
    pg.draw.rect(surf, (200, 200, 200), (0, 0, settings.basicX * 2, settings.basicY * 2), 2)
    return surf

# ==================== ОСНОВНОЙ КЛАСС ИГРЫ ====================
class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pg.time.Clock()
        self.biomes = Biomes(self.screen, pg)
        self.sprite = load_sprite()
        
        # Игрок
        self.player = pg.Rect(WIDTH // 2, HEIGHT // 2, settings.basicX * 2, settings.basicY * 2)
        self.speed = 300
        
        # Стены (в координатах тайлов → пиксели)
        self.walls = [
            pg.Rect(20 * settings.basicX, 20 * settings.basicY, settings.basicX * 4, settings.basicY * 4),
            pg.Rect(40 * settings.basicX, 30 * settings.basicY, settings.basicX * 4, settings.basicY * 4),
        ]
        
        # Камера
        self.camera_x = 0
        self.camera_y = 0
        
        # Генерируем карту при старте
        self.biomes.generate()

    def handle_input(self, dt):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.biomes.generate()  # Перегенерировать карту по R
        
        keys = pg.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y
        
        if keys[pg.K_LEFT] or keys[pg.K_a]: self.player.x -= self.speed * dt
        if keys[pg.K_RIGHT] or keys[pg.K_d]: self.player.x += self.speed * dt
        if keys[pg.K_UP] or keys[pg.K_w]: self.player.y -= self.speed * dt
        if keys[pg.K_DOWN] or keys[pg.K_s]: self.player.y += self.speed * dt
        
        # Коллизии со стенами
        for wall in self.walls:
            if self.player.colliderect(wall):
                self.player.x, self.player.y = old_x, old_y
                break
        
        return True

    def update_camera(self):
        """Камера следует за игроком"""
        self.camera_x = self.player.centerx - WIDTH // 2
        self.camera_y = self.player.centery - HEIGHT // 2

    def draw(self):
        self.screen.fill((0, 0, 0))  # Чёрный фон
        
        # 1. Биомы
        self.biomes.draw(self.camera_x, self.camera_y)
        
        # 2. Стены
        for wall in self.walls:
            rect = (wall.x - self.camera_x, wall.y - self.camera_y, wall.width, wall.height)
            pg.draw.rect(self.screen, settings.COLOR_WALL, rect)
            # Опционально: спрайт на стене
            # self.screen.blit(self.sprite, (wall.x - self.camera_x, wall.y - self.camera_y))
        
        # 3. Игрок (в центре экрана, камера следит за ним)
        player_draw_x = WIDTH // 2 - self.player.width // 2
        player_draw_y = HEIGHT // 2 - self.player.height // 2
        pg.draw.rect(self.screen, settings.COLOR_PLAYER, (player_draw_x, player_draw_y, 
                                                           self.player.width, self.player.height))
        
        # 4. FPS
        pg.display.set_caption(f'Biome Game — FPS: {self.clock.get_fps():.0f}')
        pg.display.flip()

    def run(self):
        """Главный цикл игры"""
        running = True
        while running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            running = self.handle_input(dt)
            self.update_camera()
            self.draw()
        
        pg.quit()
        sys.exit()

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    game = Game()
    game.run()