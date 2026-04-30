import pygame
import sys
import math 
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
CELL_SIZE = 64
CHUNK_SIZE = 64  # Размер чанка в тайлах
map_test = {}

# Создаем полноэкранное окно
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Цвета для разных типов тайлов
WATER_COLOR = (64, 164, 223)      # Вода - голубой
SAND_COLOR = (238, 214, 175)      # Песок/пляж
EARTH_COLOR = (101, 67, 33)       # Земля - коричневый
GRASS_COLOR = (34, 139, 34)       # Трава - зеленый
ROCK_COLOR = (128, 128, 128)      # Скала - серый
TREE_TRUNK_COLOR = (101, 67, 33)  # Ствол дерева
TREE_LEAVES_COLOR = (0, 100, 0)   # Листва дерева

GRID_LINE_COLOR = (50, 50, 50)

# Игрок
player_size = pygame.Rect(WIDTH // 2, HEIGHT // 2, CELL_SIZE, CELL_SIZE)
speed = 500

# Камера
camera_x0, camera_y0 = 0, 0

# Типы тайлов (для удобства)
TILE_WATER = 0
TILE_SAND = 1
TILE_GRASS = 2
TILE_ROCK = 3
TILE_TREE = 4

def generate_chunk(chunk_x, chunk_y):
    """Генерирует чанк по его координатам"""
    chunk = []
    for y in range(CHUNK_SIZE):
        row = []
        for x in range(CHUNK_SIZE):
            # Используем seed на основе координат чанка для стабильности
            seed = chunk_x * 99991 + chunk_y * 997
            random.seed(seed + x * 31 + y * 73)
            
            # Генерация с биомами
            # Создаем эффект больших областей
            noise_value = random.randint(0, 100)
            
            if noise_value < 30:  # 30% воды
                tile_type = TILE_WATER
            elif noise_value < 40:  # 10% песок (пляжи)
                tile_type = TILE_SAND
            elif noise_value < 110:  # 35% трава/земля
                tile_type = TILE_GRASS
                # На траве могут быть деревья (20% шанс)
                if random.randint(0, 100) < 20 and y > 2 and y < CHUNK_SIZE - 2:
                    # Убеждаемся, что дерево не слишком близко к другому
                    if x > 1 and x < CHUNK_SIZE - 1:
                        # Проверяем, нет ли уже дерева рядом
                        has_neighbor_tree = False
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if y + dy >= 0 and y + dy < CHUNK_SIZE and x + dx >= 0 and x + dx < CHUNK_SIZE:
                                    pass  # Пока просто добавляем дерево
                        if random.randint(0, 100) < 30:  # 30% шанс дерева на траве
                            tile_type = TILE_TREE
            else:  # 25% скалы
                tile_type = TILE_ROCK
                
            row.append(tile_type)
        chunk.append(row)
    return chunk

def get_chunk(chunk_x, chunk_y):
    """Получает чанк — генерирует если не существует, иначе возвращает существующий"""
    if (chunk_x, chunk_y) not in map_test:
        map_test[(chunk_x, chunk_y)] = generate_chunk(chunk_x, chunk_y)
    return map_test[(chunk_x, chunk_y)]

def draw_tree(screen, x, y, tile_size):
    """Отрисовывает дерево"""
    # Ствол дерева (коричневый прямоугольник)
    trunk_width = tile_size // 3
    trunk_height = tile_size // 2
    trunk_x = x + (tile_size - trunk_width) // 2
    trunk_y = y + tile_size - trunk_height
    pygame.draw.rect(screen, TREE_TRUNK_COLOR, (trunk_x, trunk_y, trunk_width, trunk_height))
    
    # Листва (зеленые круги/треугольники)
    leaf_size = tile_size // 2
    # Нижний ярус листвы
    pygame.draw.circle(screen, TREE_LEAVES_COLOR, (x + tile_size // 2, y + tile_size // 2), leaf_size)
    # Верхний ярус листвы
    pygame.draw.circle(screen, (0, 130, 0), (x + tile_size // 2, y + tile_size // 3), leaf_size - 4)
    # Макушка
    pygame.draw.circle(screen, (0, 160, 0), (x + tile_size // 2, y + tile_size // 6), leaf_size - 8)

def draw_rock(screen, x, y, tile_size):
    """Отрисовывает скалу"""
    # Основной камень
    pygame.draw.rect(screen, ROCK_COLOR, (x + 4, y + 8, tile_size - 8, tile_size - 12))
    # Детали скалы
    pygame.draw.rect(screen, (100, 100, 100), (x + 8, y + 12, 5, 8))
    pygame.draw.rect(screen, (100, 100, 100), (x + 18, y + 10, 5, 10))
    # Текстура
    pygame.draw.line(screen, (90, 90, 90), (x + 6, y + 16), (x + 26, y + 20), 2)

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
                    
                    # Выбираем цвет в зависимости от типа тайла
                    if tile_type == TILE_WATER:
                        color = WATER_COLOR
                        # Добавляем эффект глубины
                        pygame.draw.rect(screen, color, (world_x, world_y, tile_size, tile_size))
                        # Рисуем блики на воде
                        pygame.draw.line(screen, (100, 200, 240), 
                                       (world_x + 5, world_y + 8), 
                                       (world_x + 15, world_y + 8), 1)
                        
                    elif tile_type == TILE_SAND:
                        color = SAND_COLOR
                        pygame.draw.rect(screen, color, (world_x, world_y, tile_size, tile_size))
                        # Добавляем текстуру песка
                        pygame.draw.circle(screen, (210, 190, 155), 
                                         (world_x + 8, world_y + 16), 2)
                        pygame.draw.circle(screen, (210, 190, 155), 
                                         (world_x + 20, world_y + 24), 2)
                        
                    elif tile_type == TILE_GRASS:
                        color = GRASS_COLOR
                        pygame.draw.rect(screen, color, (world_x, world_y, tile_size, tile_size))
                        # Добавляем траву (маленькие точки)
                        for i in range(3):
                            pygame.draw.line(screen, (50, 200, 50),
                                           (world_x + 5 + i*8, world_y + 28),
                                           (world_x + 4 + i*8, world_y + 24), 2)
                        
                    elif tile_type == TILE_ROCK:
                        pygame.draw.rect(screen, EARTH_COLOR, (world_x, world_y, tile_size, tile_size))
                        draw_rock(screen, world_x, world_y, tile_size)
                        
                    elif tile_type == TILE_TREE:
                        pygame.draw.rect(screen, GRASS_COLOR, (world_x, world_y, tile_size, tile_size))
                        draw_tree(screen, world_x, world_y, tile_size)

# Загрузка спрайтов
try:
    original_img = pygame.image.load('unknown_game_DL/sprite/Sprite-0001.png').convert_alpha()
except pygame.error:
    # Если файла нет, создаём тестовый спрайт (игрок)
    original_img = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(original_img, (255, 80, 80), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 3)
    pygame.draw.rect(original_img, (255, 255, 255), (0, 0, CELL_SIZE, CELL_SIZE), 2)

sprite = pygame.transform.smoothscale(original_img, (CELL_SIZE, CELL_SIZE))

# Создаем несколько тестовых стен
wall1 = pygame.Rect(5 * CELL_SIZE, 5 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
wall2 = pygame.Rect(10 * CELL_SIZE, 10 * CELL_SIZE, CELL_SIZE, CELL_SIZE)

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(120) / 500.0
    
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
