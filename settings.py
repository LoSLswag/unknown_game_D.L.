# settings.py
# Настройки экрана
FULLSCREEN = True
FPS = 120

# Настройки генерации биомов
Rows = 200 # Количество строк в карте (увеличено для большого экрана)
Columns = 200  # Количество столбцов в карте (увеличено для большого экрана)
COUNTS_ALGORITHMS = 5
COUNTS_ALGORITHMS_SANDS = 3

# Размеры ячеек (basicX и basicY теперь равны CELL_SIZE)
basicX = 64
basicY = 64

# Цвета биомов
COLOR_LAND = (34, 139, 34)        # Зеленый
COLOR_SEA = (64, 164, 223)        # Голубой  
COLOR_SAND = (238, 214, 175)      # Песочный
COLOR_SEA_SHORE = (173, 216, 230) # Светло-голубой
COLOR_WOODS = (0, 100, 0)         # Темно-зеленый