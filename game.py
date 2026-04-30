import pygame
import sys
import math 
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
CELL_SIZE = 64
CHUNK_SIZE = 16  # Размер чанка в тайлах
map_test = {}

# Создаем полноэкранное окно
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Game")

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
player_size = pygame.Rect(WIDTH // 2, HEIGHT // 2, CELL_SIZE, CELL_SIZE)
speed = 200

# Камера
camera_x0, camera_y0 = 0, 0

def generate_chunk(chunk_x, chunk_y):
    """Генерирует чанк по его координатам"""
    chunk = []
    for y in range(CHUNK_SIZE):
        row = []
        for x in range(CHUNK_SIZE):
            # Используем seed на основе координат чанка для стабильности
            seed = chunk_x * 99991 + chunk_y * 997
            random.seed(seed + x * 31 + y * 73)
            
            # Случайный тип тайла (0 - земля, 1 - вода, 2 - гора, 3 - дерево/трава)
            tile_type = random.randint(0, 3)
            row.append(tile_type)
        chunk.append(row)
    return chunk

def get_chunk(chunk_x, chunk_y):
    """Получает чанк — генерирует если не существует, иначе возвращает существующий"""
    if (chunk_x, chunk_y) not in map_test:
        map_test[(chunk_x, chunk_y)] = generate_chunk(chunk_x, chunk_y)
    return map_test[(chunk_x, chunk_y)]

def get_tile_color(tile_type):
    """Возвращает цвет для типа тайла"""
    colors = {
        0: BROWN,      # земля
        1: WATER_BLUE, # вода
        2: GRAY,       # гора
        3: GREEN       # трава/дерево
    }
    return colors.get(tile_type, BROWN)

def render_visible_area(screen, camera_x, camera_y, screen_width, screen_height, tile_size):
    """Отрисовывает видимую часть карты"""
    # Вычисляем границы видимости в тайлах
    start_tile_x = camera_x // tile_size
    start_tile_y = camera_y // tile_size
    end_tile_x = (camera_x + screen_width) // tile_size + 1
    end_tile_y = (camera_y + screen_height) // tile_size + 1
    
    # Вычисляем границы видимости в чанках
    start_chunk_x = start_tile_x // CHUNK_SIZE
    start_chunk_y = start_tile_y // CHUNK_SIZE
    end_chunk_x = end_tile_x // CHUNK_SIZE + 1
    end_chunk_y = end_tile_y // CHUNK_SIZE + 1
    
    # Отрисовываем все видимые чанки
    for chunk_x in range(start_chunk_x, end_chunk_x):
        for chunk_y in range(start_chunk_y, end_chunk_y):
            chunk = get_chunk(chunk_x, chunk_y)
            
            # Отрисовываем каждый тайл в чанке
            for y, row in enumerate(chunk):
                for x, tile_type in enumerate(row):
                    # Координаты тайла в мировых координатах
                    world_x = chunk_x * CHUNK_SIZE * tile_size + x * tile_size - camera_x
                    world_y = chunk_y * CHUNK_SIZE * tile_size + y * tile_size - camera_y
                    
                    # Отрисовка тайла
                    color = get_tile_color(tile_type)
                    pygame.draw.rect(screen, color, (world_x, world_y, tile_size, tile_size))

# Загрузка спрайтов
try:
    original_img = pygame.image.load('unknown_game_DL/sprite/Sprite-0001.png').convert_alpha()
except pygame.error:
    # Если файла нет, создаём тестовый спрайт (красный круг)
    original_img = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(original_img, (255, 80, 80), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 3)
    pygame.draw.rect(original_img, (200, 200, 200), (0, 0, CELL_SIZE, CELL_SIZE), 2)

sprite = pygame.transform.smoothscale(original_img, (CELL_SIZE, CELL_SIZE))

# Создаем несколько тестовых стен
wall1 = pygame.Rect(5 * CELL_SIZE, 5 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
wall2 = pygame.Rect(10 * CELL_SIZE, 10 * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(120) / 1000.0
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Сохраняем предыдущую позицию на случай коллизии
    old_x, old_y = player_size.x, player_size.y
    
    # Движение игрока
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
        player_size.x -= speed * dt
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
        player_size.x += speed * dt 
    if keys[pygame.K_UP] or keys[pygame.K_w]: 
        player_size.y -= speed * dt
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
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
    
    # Отрисовка видимой области карты
    render_visible_area(screen, camera_x0, camera_y0, WIDTH, HEIGHT, CELL_SIZE)
    
    # Отрисовка стен
    screen.blit(sprite, (wall1.x - camera_x0, wall1.y - camera_y0))
    screen.blit(sprite, (wall2.x - camera_x0, wall2.y - camera_y0))
    
    # Отрисовка игрока
    screen.blit(sprite, (player_size.x - camera_x0, player_size.y - camera_y0))
    
    # Обновление экрана
    pygame.display.flip()
    
    # Контроль FPS
    clock.tick(120)

# Завершение игры
pygame.quit()
sys.exit()