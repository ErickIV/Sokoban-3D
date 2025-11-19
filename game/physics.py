"""
game/physics.py
===============
Sistema de física e detecção de colisões do jogo.

SISTEMA DE GRID:
---------------
- Mundo discreto para lógica (inteiros)
- Movimentação suave (floats) com conversão
- Grid de 1x1 unidade por célula

DETECÇÃO DE COLISÕES:
--------------------
1. AABB (Axis-Aligned Bounding Box) simplificado
2. Colisão circular jogador-obstáculos
3. Sliding collision (deslizar ao tocar paredes)
4. Verificação de múltiplos obstáculos

DIREÇÕES CARDINAIS:
------------------
Converte ângulo da câmera (yaw) em direções discretas:
- Norte (0°), Sul (180°), Leste (90°), Oeste (270°)
- Usado para empurrar caixas em direções precisas

FÍSICA DE MOVIMENTO:
-------------------
- Movimento suave com interpolação
- Resposta a colisões sem travamento
- Raio de colisão do jogador configurável
"""

import math
from typing import Tuple, List
from config import PLAYER_RADIUS, SLIDING_FRICTION_FACTOR


class Physics:
    """Gerenciador de física e colisões do jogo"""

    @staticmethod
    def grid_round(value: float) -> int:
        """
        Arredonda valor para o grid mais próximo.

        Args:
            value (float): Valor a ser arredondado

        Returns:
            int: Valor arredondado
        """
        return int(round(value))
    
    @staticmethod
    def aabb_collides_point(px: float, pz: float, cx: float, cz: float,
                           half: float = 0.5, radius: float = PLAYER_RADIUS) -> bool:
        """
        Detecta colisão entre um ponto circular e uma AABB.
        Usa técnica de "closest point" para precisão.

        Args:
            px, pz: Posição do jogador
            cx, cz: Centro da AABB
            half: Metade do tamanho da AABB
            radius: Raio de colisão do jogador

        Returns:
            bool: True se houver colisão
        """
        # Calcula limites da AABB
        minx = cx - half
        maxx = cx + half
        minz = cz - half
        maxz = cz + half
        
        # Encontra ponto mais próximo da AABB ao jogador
        closest_x = max(minx, min(px, maxx))
        closest_z = max(minz, min(pz, maxz))
        
        # Calcula distância do jogador ao ponto mais próximo
        dx = px - closest_x
        dz = pz - closest_z
        
        # Colisão se distância < raio
        return (dx*dx + dz*dz) < (radius*radius)
    
    @staticmethod
    def check_collision_with_list(px: float, pz: float,
                                  object_list: List[Tuple[float, float, float]]) -> bool:
        """
        Verifica colisão do jogador com uma lista de objetos.

        Args:
            px, pz: Posição do jogador
            object_list: Lista de tuplas (x, y, z)

        Returns:
            bool: True se houver colisão com algum objeto
        """
        for (x, y, z) in object_list:
            if Physics.aabb_collides_point(px, pz, x, z):
                return True
        return False
    
    @staticmethod
    def can_move_to(px: float, pz: float,
                   walls: List[Tuple[float, float, float]],
                   boxes: List[Tuple[float, float, float]]) -> bool:
        """
        Verifica se jogador pode mover para determinada posição.

        Args:
            px, pz: Posição desejada
            walls: Lista de paredes
            boxes: Lista de caixas

        Returns:
            bool: True se pode mover
        """
        # Verifica colisão com paredes
        if Physics.check_collision_with_list(px, pz, walls):
            return False
        
        # Verifica colisão com caixas
        if Physics.check_collision_with_list(px, pz, boxes):
            return False
        
        return True
    
    @staticmethod
    def get_cardinal_direction(yaw_degrees: float) -> Tuple[int, int]:
        """
        Converte ângulo de visão em direção cardinal (N, S, L, O).

        Args:
            yaw_degrees: Ângulo de rotação horizontal em graus

        Returns:
            tuple: (dir_x, dir_z) em valores -1, 0 ou 1
        """
        yaw = math.radians(yaw_degrees)
        forward_x = math.sin(yaw)
        forward_z = -math.cos(yaw)
        
        # Converte para direção cardinal
        if abs(forward_x) > abs(forward_z):
            dir_x = 1 if forward_x > 0 else -1
            dir_z = 0
        else:
            dir_x = 0
            dir_z = 1 if forward_z > 0 else -1
        
        return dir_x, dir_z
    
    @staticmethod
    def smooth_move(current_x: float, current_z: float,
                   target_x: float, target_z: float,
                   walls: List[Tuple[float, float, float]],
                   boxes: List[Tuple[float, float, float]],
                   dt: float, speed: float) -> Tuple[float, float, bool]:
        """
        Move jogador suavemente com sliding em paredes.
        MELHORADO: Previne travamento em cantos.

        Args:
            current_x, current_z: Posição atual
            target_x, target_z: Posição desejada
            walls, boxes: Listas de obstáculos
            dt: Delta time
            speed: Velocidade de movimento

        Returns:
            tuple: (new_x, new_z, moved)
        """
        # Calcula nova posição
        dx = target_x - current_x
        dz = target_z - current_z
        
        # Normaliza direção
        distance = math.hypot(dx, dz)
        if distance > 0:
            dx = (dx / distance) * speed
            dz = (dz / distance) * speed
        else:
            return current_x, current_z, False
        
        # Aplica movimento
        new_x = current_x + dx * dt
        new_z = current_z + dz * dt
        
        moved = False
        
        # Tenta mover para posição desejada (movimento completo)
        if Physics.can_move_to(new_x, new_z, walls, boxes):
            current_x = new_x
            current_z = new_z
            moved = True
        else:
            # SLIDING MELHORADO: tenta com redução de velocidade (fator de fricção)
            # Isso previne travamento em cantos apertados e permite deslizar em paredes

            # Tenta mover só em X com velocidade reduzida
            test_x = current_x + (dx * dt * SLIDING_FRICTION_FACTOR)
            if Physics.can_move_to(test_x, current_z, walls, boxes):
                current_x = test_x
                moved = True

            # Tenta mover só em Z com velocidade reduzida
            test_z = current_z + (dz * dt * SLIDING_FRICTION_FACTOR)
            if Physics.can_move_to(current_x, test_z, walls, boxes):
                current_z = test_z
                moved = True
        
        return current_x, current_z, moved
