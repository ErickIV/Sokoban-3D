"""
game/level.py
=============
Gerenciamento de níveis do jogo.
Carrega, valida e manipula dados dos níveis.

RESPONSABILIDADES:
-----------------
1. Carregamento de dados de níveis (levels_data.py)
2. Validação de spawn points e geometria
3. Lógica de empurrar caixas (push mechanics)
4. Detecção de colisões caixa-parede e caixa-caixa
5. Verificação de condições de vitória
6. Sistema de partículas para feedback visual
7. Estatísticas (movimentos, caixas no objetivo)

MECÂNICA DE EMPURRAR:
--------------------
- Verifica posição do jogador e direção olhada
- Calcula posição da caixa na frente
- Valida se destino está livre (sem paredes/caixas)
- Verifica limites do mundo
- Atualiza estado e dispara efeitos sonoros/visuais

SISTEMA DE GRID:
---------------
- Posições discretas (inteiros) para lógica
- Posições contínuas (floats) para renderização
- Conversão através de Physics.grid_round()
"""

import math
from .levels_data import LEVELS, get_level, get_level_count
from .physics import Physics
from utils.sound import get_sound_manager
from graphics.clouds import CloudSystem
from config import WORLD_BOUNDARY_LIMIT, SPAWN_ADJUSTMENT_OFFSET
from utils.logger import get_logger


class Level:
    """Gerenciador de um nível do jogo"""
    
    def __init__(self):
        """Inicializa gerenciador de nível vazio"""
        self.current_level_index = 0
        self.walls = []
        self.boxes = []
        self.objectives = []
        self.spawn_position = (0.0, 0.0, 0.0)
        self.move_count = 0
        self.particles = []  # Lista de (x, y, z, start_time)
        self.clouds = None  # Sistema de nuvens

        # Dados do nível atual
        self.level_name = ""
        self.level_difficulty = ""

        # Logger para reportar problemas
        self.logger = get_logger()

    def _validate_level_data(self, level_data):
        """
        Valida dados de um nível antes de carregar.

        Args:
            level_data (dict): Dados do nível a validar

        Returns:
            tuple: (valido: bool, mensagem_erro: str ou None)
        """
        # Verifica se dados existem
        if level_data is None:
            return False, "Dados do nível são None"

        # Verifica se é um dicionário
        if not isinstance(level_data, dict):
            return False, f"Dados do nível devem ser dict, recebido {type(level_data)}"

        # Verifica chaves obrigatórias
        required_keys = ['paredes', 'caixas', 'objetivos', 'spawn']
        for key in required_keys:
            if key not in level_data:
                return False, f"Chave obrigatória '{key}' não encontrada nos dados do nível"

        # Valida paredes
        if not isinstance(level_data['paredes'], list):
            return False, f"'paredes' deve ser uma lista, recebido {type(level_data['paredes'])}"

        for i, wall in enumerate(level_data['paredes']):
            if not isinstance(wall, tuple) or len(wall) != 3:
                return False, f"Parede {i} inválida: deve ser tupla (x, y, z), recebido {wall}"
            if not all(isinstance(coord, (int, float)) for coord in wall):
                return False, f"Parede {i} tem coordenadas não-numéricas: {wall}"
            # Verifica se está dentro dos limites do mundo
            if abs(wall[0]) >= WORLD_BOUNDARY_LIMIT or abs(wall[2]) >= WORLD_BOUNDARY_LIMIT:
                return False, f"Parede {i} fora dos limites do mundo: {wall}"

        # Valida caixas
        if not isinstance(level_data['caixas'], list):
            return False, f"'caixas' deve ser uma lista, recebido {type(level_data['caixas'])}"

        if len(level_data['caixas']) == 0:
            return False, "Nível deve ter pelo menos uma caixa"

        for i, box in enumerate(level_data['caixas']):
            if not isinstance(box, tuple) or len(box) != 3:
                return False, f"Caixa {i} inválida: deve ser tupla (x, y, z), recebido {box}"
            if not all(isinstance(coord, (int, float)) for coord in box):
                return False, f"Caixa {i} tem coordenadas não-numéricas: {box}"
            if abs(box[0]) >= WORLD_BOUNDARY_LIMIT or abs(box[2]) >= WORLD_BOUNDARY_LIMIT:
                return False, f"Caixa {i} fora dos limites do mundo: {box}"
            # Verifica se caixa não está dentro de parede
            if box in level_data['paredes']:
                return False, f"Caixa {i} está dentro de uma parede: {box}"

        # Valida objetivos
        if not isinstance(level_data['objetivos'], list):
            return False, f"'objetivos' deve ser uma lista, recebido {type(level_data['objetivos'])}"

        if len(level_data['objetivos']) == 0:
            return False, "Nível deve ter pelo menos um objetivo"

        # Verifica correspondência entre número de caixas e objetivos
        if len(level_data['caixas']) != len(level_data['objetivos']):
            self.logger.warning(
                f"Número de caixas ({len(level_data['caixas'])}) "
                f"difere do número de objetivos ({len(level_data['objetivos'])})"
            )

        for i, obj in enumerate(level_data['objetivos']):
            if not isinstance(obj, tuple) or len(obj) != 3:
                return False, f"Objetivo {i} inválido: deve ser tupla (x, y, z), recebido {obj}"
            if not all(isinstance(coord, (int, float)) for coord in obj):
                return False, f"Objetivo {i} tem coordenadas não-numéricas: {obj}"
            if abs(obj[0]) >= WORLD_BOUNDARY_LIMIT or abs(obj[2]) >= WORLD_BOUNDARY_LIMIT:
                return False, f"Objetivo {i} fora dos limites do mundo: {obj}"
            if obj in level_data['paredes']:
                return False, f"Objetivo {i} está dentro de uma parede: {obj}"

        # Valida spawn
        spawn = level_data['spawn']
        if not isinstance(spawn, tuple) or len(spawn) != 3:
            return False, f"'spawn' deve ser tupla (x, y, z), recebido {spawn}"
        if not all(isinstance(coord, (int, float)) for coord in spawn):
            return False, f"'spawn' tem coordenadas não-numéricas: {spawn}"
        if abs(spawn[0]) >= WORLD_BOUNDARY_LIMIT or abs(spawn[2]) >= WORLD_BOUNDARY_LIMIT:
            return False, f"'spawn' fora dos limites do mundo: {spawn}"

        # Todas as validações passaram
        return True, None
    
    def load_level(self, level_index):
        """
        Carrega um nível específico.

        Args:
            level_index (int): Índice do nível (0-based)

        Returns:
            bool: True se carregou com sucesso
        """
        # Valida índice do nível
        if not isinstance(level_index, int):
            self.logger.error(f"Índice de nível inválido: {level_index} (tipo: {type(level_index)})")
            return False

        if level_index < 0 or level_index >= get_level_count():
            self.logger.error(f"Índice de nível fora do intervalo: {level_index} (máx: {get_level_count() - 1})")
            return False

        level_data = get_level(level_index)

        # Valida dados do nível
        valid, error_msg = self._validate_level_data(level_data)
        if not valid:
            self.logger.error(f"Dados de nível {level_index} inválidos: {error_msg}")
            return False
        
        self.current_level_index = level_index
        
        # Copia dados do nível
        self.walls = level_data['paredes'][:]
        self.boxes = level_data['caixas'][:]
        self.objectives = level_data['objetivos'][:]
        self.spawn_position = level_data['spawn']
        
        # Validação: Verifica se spawn não está dentro de parede
        spawn_grid = (
            int(round(self.spawn_position[0])),
            int(round(self.spawn_position[1])),
            int(round(self.spawn_position[2]))
        )
        if spawn_grid in self.walls:
            # Ajusta spawn automaticamente movendo unidades para frente
            self.spawn_position = (
                self.spawn_position[0],
                self.spawn_position[1],
                self.spawn_position[2] + SPAWN_ADJUSTMENT_OFFSET
            )
        
        # Metadados
        self.level_name = level_data.get('name', f'Nível {level_index + 1}')
        self.level_difficulty = level_data.get('difficulty', 'Normal')
        
        # Reseta estado
        self.move_count = 0
        self.particles = []
        
        # Inicializa sistema de nuvens melhorado
        from config import CLOUD_COUNT, CLOUD_WIND_SPEED
        if self.clouds:
            self.clouds.cleanup()  # Limpa nuvens antigas
        self.clouds = CloudSystem(num_clouds=CLOUD_COUNT, wind_speed=CLOUD_WIND_SPEED)
        
        return True
    
    def reload_current_level(self):
        """Recarrega o nível atual (reset)"""
        return self.load_level(self.current_level_index)
    
    def get_next_level_index(self):
        """Retorna índice do próximo nível ou None se é o último"""
        next_index = self.current_level_index + 1
        if next_index < get_level_count():
            return next_index
        return None
    
    def is_last_level(self):
        """Verifica se é o último nível"""
        return self.current_level_index >= get_level_count() - 1
    
    def check_victory(self):
        """
        Verifica se o jogador completou o nível.
        
        Returns:
            bool: True se todas as caixas estão nos objetivos
        """
        if len(self.boxes) != len(self.objectives):
            return False
        
        # Conta caixas nos objetivos corretos
        boxes_on_targets = sum(1 for box in self.boxes if box in self.objectives)
        
        return boxes_on_targets == len(self.objectives)
    
    def can_push_box(self, player_x, player_z, direction_x, direction_z):
        """
        Verifica se pode empurrar uma caixa.
        
        Args:
            player_x, player_z: Posição do jogador
            direction_x, direction_z: Direção do empurrão
            
        Returns:
            tuple: (pode_empurrar, box_position, destination) ou (False, None, None)
        """
        px = Physics.grid_round(player_x)
        pz = Physics.grid_round(player_z)
        
        # Posição da caixa na frente do jogador
        box_pos = (px + direction_x, 0, pz + direction_z)
        
        # Verifica se há uma caixa
        if box_pos not in self.boxes:
            return False, None, None
        
        # Posição de destino da caixa
        dest_pos = (box_pos[0] + direction_x, 0, box_pos[2] + direction_z)
        
        # Verifica se destino está livre
        if dest_pos in self.boxes or dest_pos in self.walls:
            return False, box_pos, dest_pos
        
        # Verifica limites do mundo para evitar caixas fora do mapa
        if abs(dest_pos[0]) >= WORLD_BOUNDARY_LIMIT or abs(dest_pos[2]) >= WORLD_BOUNDARY_LIMIT:
            return False, box_pos, dest_pos
        
        return True, box_pos, dest_pos
    
    def push_box(self, player_x, player_z, direction_x, direction_z, current_time):
        """
        Empurra uma caixa se possível.
        
        Args:
            player_x, player_z: Posição do jogador
            direction_x, direction_z: Direção do empurrão
            current_time: Tempo atual para partículas
            
        Returns:
            bool: True se empurrou com sucesso
        """
        can_push, box_pos, dest_pos = self.can_push_box(
            player_x, player_z, direction_x, direction_z
        )
        
        if not can_push:
            # Som de bloqueio
            get_sound_manager().play('blocked')
            return False
        
        # Move a caixa
        idx = self.boxes.index(box_pos)
        self.boxes[idx] = dest_pos
        self.move_count += 1
        
        # Som de empurrar
        get_sound_manager().play('push')
        # Cria partículas espetaculares e som se atingiu objetivo
        if dest_pos in self.objectives:
            # Explosão de partículas coloridas e variadas!
            import random
            num_particles = 50  # Aumentado para efeito mais denso
            
            for i in range(num_particles):
                # Posição inicial (centro da caixa)
                px = dest_pos[0]
                py = 0.5
                pz = dest_pos[2]
                
                # Velocidade aleatória (explosão esférica) - reduzida para animação mais lenta
                speed = random.uniform(0.5, 3.0)
                angle_y = random.uniform(0, math.pi * 2)
                angle_v = random.uniform(0, math.pi / 2) # Apenas para cima
                
                vx = math.cos(angle_y) * math.cos(angle_v) * speed
                vy = math.sin(angle_v) * speed
                vz = math.sin(angle_y) * math.cos(angle_v) * speed
                
                # Cores mais brilhantes e saturadas
                colors = [
                    (1.0, 0.9, 0.2),  # Dourado brilhante
                    (0.2, 1.0, 1.0),  # Cyan elétrico
                    (1.0, 0.2, 1.0),  # Magenta neon
                    (1.0, 1.0, 0.5),  # Amarelo
                    (1.0, 0.6, 0.2),  # Laranja
                ]
                color = random.choice(colors)
                
                # Tamanho aleatório para variedade (0.3 a 0.8)
                particle_size = random.uniform(0.3, 0.8)
                
                # [x, y, z, vx, vy, vz, r, g, b, start_time, size]
                self.particles.append([
                    px, py, pz, 
                    vx, vy, vz,
                    color[0], color[1], color[2],
                    current_time,
                    particle_size
                ])

            get_sound_manager().play('box_on_target')
        
        return True

    def update_particles(self, current_time, dt):
        """
        Atualiza física das partículas.
        
        Args:
            current_time: Tempo atual
            dt: Delta time
        """
        gravity = -5.0  # Reduzido para efeito mais "mágico"
        
        # Atualiza e filtra partículas vivas
        alive_particles = []
        for p in self.particles:
            # p = [x, y, z, vx, vy, vz, r, g, b, start_time, size]
            start_time = p[9]
            age = current_time - start_time
            
            if age < 4.0: # Tempo de vida (aumentado para melhor visibilidade)
                # Física
                p[0] += p[3] * dt # x += vx * dt
                p[1] += p[4] * dt # y += vy * dt
                p[2] += p[5] * dt # z += vz * dt
                
                p[4] += gravity * dt # vy += g * dt
                
                # Colisão com chão - mais bounce
                if p[1] < 0.1:
                    p[1] = 0.1
                    p[4] *= -0.7 # Mais bounce (antes 0.5)
                    p[3] *= 0.8 # Atrito
                    p[5] *= 0.8
                
                alive_particles.append(p)
                
        self.particles = alive_particles

    def get_progress_stats(self):
        """
        Retorna estatísticas de progresso do nível.
        
        Returns:
            dict: {'boxes_on_target', 'total_boxes', 'move_count', 'completion_percent'}
        """
        boxes_on_target = sum(1 for box in self.boxes if box in self.objectives)
        total_boxes = len(self.objectives)
        completion = (boxes_on_target / total_boxes * 100) if total_boxes > 0 else 0
        
        return {
            'boxes_on_target': boxes_on_target,
            'total_boxes': total_boxes,
            'move_count': self.move_count,
            'completion_percent': completion
        }
