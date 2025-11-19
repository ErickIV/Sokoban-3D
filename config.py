"""
config.py
=========
Configurações globais e constantes do jogo BoxPush 3D.
Centraliza todos os parâmetros ajustáveis para fácil manutenção.
"""

# -----------------------------
# Configurações de Janela/Câmera
# -----------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "BOXPUSH 3D - Sokoban Pygame + PyOpenGL"

# Configurações de câmera
FOV = 70.0              # Field of View (graus)
NEAR_PLANE = 0.1        # Plano próximo de renderização
FAR_PLANE = 200.0       # Plano distante de renderização

# -----------------------------
# Parâmetros de Jogabilidade
# -----------------------------
PLAYER_EYE_HEIGHT = 0.8     # Altura dos olhos do jogador
PLAYER_RADIUS = 0.35        # Raio de colisão no plano XZ
MOVE_SPEED = 3.0            # Velocidade de movimento (m/s)
RUN_MULTIPLIER = 1.65       # Multiplicador ao segurar SHIFT
MOUSE_SENSITIVITY = 0.12    # Sensibilidade do mouse (deg/pixel)
PUSH_COOLDOWN = 0.18        # Intervalo entre empurrões (segundos)
GRID_SIZE = 1.0             # Tamanho da grade do mundo

# -----------------------------
# Estados do Jogo
# -----------------------------
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_WIN = 2
GAME_STATE_FINAL_VICTORY = 3

# -----------------------------
# Configurações de Renderização
# -----------------------------
TARGET_FPS = 120            # FPS alvo
MAX_FRAME_TIME = 0.033      # Tempo máximo de frame (cap)

# Configurações de grama
GRASS_DENSITY = 8           # Folhas por unidade quadrada
GRASS_AREA = 20             # Área de cobertura da grama
GRASS_MIN_HEIGHT = 0.05     # Altura mínima das folhas
GRASS_MAX_HEIGHT = 0.15     # Altura máxima das folhas
GRASS_BLADE_WIDTH = 0.02    # Largura das folhas

# -----------------------------
# Cores do Céu
# -----------------------------
SKY_COLOR = (0.52, 0.75, 0.92, 1.0)  # Azul céu realista

# -----------------------------
# Sistema de Partículas
# -----------------------------
PARTICLE_LIFETIME = 2.0     # Tempo de vida das partículas (segundos)
PARTICLE_COUNT = 8          # Número de partículas por efeito

# -----------------------------
# Constantes de Física e Interação
# -----------------------------
BOX_INTERACTION_DISTANCE = 2.5   # Distância máxima para interagir com caixas
WORLD_BOUNDARY_LIMIT = 100       # Limite de coordenadas do mundo
SPAWN_ADJUSTMENT_OFFSET = 2.0    # Offset para ajustar spawn bloqueado
SLIDING_FRICTION_FACTOR = 0.7    # Fator de atrito ao deslizar em paredes

# -----------------------------
# Cores dos Estados das Caixas
# -----------------------------
# Cor da caixa quando está em um objetivo
BOX_COLOR_ON_TARGET = (1.0, 0.84, 0.0, 1.0)  # Dourado
BOX_SHININESS_ON_TARGET = 64.0

# Cor da caixa quando pode ser empurrada
BOX_COLOR_PUSHABLE = (0.2, 0.9, 0.2, 1.0)  # Verde
BOX_SHININESS_PUSHABLE = 32.0

# Cor da caixa quando está bloqueada
BOX_COLOR_BLOCKED = (0.9, 0.2, 0.2, 1.0)  # Vermelho
BOX_SHININESS_BLOCKED = 32.0

# Cor da caixa em estado normal
BOX_COLOR_NORMAL = (0.72, 0.48, 0.16, 1.0)  # Marrom
BOX_SHININESS_NORMAL = 32.0

# -----------------------------
# Configurações de Performance
# -----------------------------
# Número máximo de frames para cálculo de FPS médio
FPS_AVERAGE_WINDOW = 60

# Distância máxima de renderização para otimização
MAX_RENDER_DISTANCE = FAR_PLANE
