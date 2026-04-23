import pygame
import sys
import math 
# Инициализация Pygame
pygame.init()

# Настройки экрана
CELL_SIZE = 32

# Создаем окно в полноэкранном режиме
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

# Создаем полноэкранное окно
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Цвета и тольшина линий
GRID_LINE_COLOR = (50, 50, 50,)

# Функция для выравнивания позиции к центру клетки
def align_to_grid(x, y, cell_size):
#    center_x = x // cell_size 
#    center_y = y // cell_size
    center_x = x // cell_size * cell_size
    center_y = y // cell_size * cell_size
    return center_x, center_y

# Игрок
player_size = CELL_SIZE 
initial_player_screen_center_x = WIDTH // 2
initial_player_screen_center_y = HEIGHT // 2
player_x, player_y = align_to_grid(initial_player_screen_center_x, initial_player_screen_center_y, CELL_SIZE)
speed = 500

# Статичный объект (в заданной позиции в игровом мире)
static_object_world_x = 100
static_object_world_y = 100
static_object_x, static_object_y = align_to_grid(static_object_world_x, static_object_world_y, CELL_SIZE)

# Камера
#camera_pos = [5, 5]
camera_x, camera_y = WIDTH , HEIGHT 


#тодщина линий
LINE_WIDTH = 1

try:
    original_img = pygame.image.load('unknowngame\sprite\Sprite-0001.png').convert_alpha()
except pygame.error:
    # Если файла нет, создаём тестовый спрайт (красный круг)
    original_img = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(original_img, (255, 80, 80), (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 3)

sprite = pygame.transform.smoothscale(original_img, (CELL_SIZE, CELL_SIZE))

# Координаты клетки, куда поместим спрайт (столбец, строка)
target_col, target_row = 3, 2
x = target_col * CELL_SIZE
y = target_row * CELL_SIZE

# Переменные управления движением
direction = None
move_timer = 0
move_interval = 200  # Интервал в 200 миллисекунд (0,2 секунды)

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
    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx += 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx -= 1
    if keys[pygame.K_UP] or keys[pygame.K_w]: dy += 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy -= 1

    if dx != 0 and dy != 0:
        length = math.sqrt(dx**2 + dy**2)
        dx /= length
        dy /= length

    player_x += dx * speed * dt
    player_y += dy * speed * dt


    # Ограничение позиции игрока, чтобы он не выходил за пределы экрана
    should_move = True

    # Обновление смещения камеры
    camera_x = player_x - WIDTH // 2 + player_size // 2
    camera_y = player_y - HEIGHT // 2 + player_size // 2
    
    #цвта заднего экрана 
    BACKGROUND_COLOR = (0, 0, 0)
    
    # Отрисовка
    screen.fill(BACKGROUND_COLOR)

    # Рисуем статичный объект (на позиции в карте, с учетом смещения камеры)
    
    obiekt_sprite = pygame.image.load('unknowngame\sprite\Sprite-0001.png')
    screen.blit(obiekt_sprite, (static_object_x - camera_x, static_object_y - camera_y))

    # Отрисовка игрока
    
    player_sprite = pygame.image.load('unknowngame\sprite\skeleton_parad.png')
    screen.blit(player_sprite, (player_x - camera_x, player_y - camera_y))

    # Рисуем сетку
    
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_LINE_COLOR, (x + CELL_SIZE/2, 0), (x + CELL_SIZE/2, HEIGHT),LINE_WIDTH)  # Вертикальные линии
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, y + CELL_SIZE/2.5), (WIDTH, y + CELL_SIZE/2.5), LINE_WIDTH)  # Горизонтальные линии
        
        
        '''x = math.floor(world_left / CELL_SIZE) * CELL_SIZE
    while x <= world_right:
        screen_x = x * zoom + camera_x   # ← zoom используется здесь!
        pygame.draw.line(screen, GRID_LINE_COLOR, (screen_x, 0), (screen_x, HEIGHT), 1)
        x += CELL_SIZE
    y = math.floor(world_top / CELL_SIZE) * CELL_SIZE
    while y <= world_bottom:
        screen_y = y * zoom + camera_y
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, screen_y), (WIDTH, screen_y), 1)
        y += CELL_SIZE'''
    
    # Ограничение движения камеры по границам карты
    map_width = 1
    map_height = 1

    camera_x = max(0, min(camera_x, map_width - WIDTH))
    camera_y = max(0, min(camera_y, map_height - HEIGHT))

    # Обновление экрана
    pygame.display.flip()
    
    # Контроль FPS
    clock.tick(120)

# Завершение игры
pygame.quit()
sys.exit()

