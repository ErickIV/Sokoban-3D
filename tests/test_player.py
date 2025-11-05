"""
tests/test_player.py
====================
Testes unitários para o módulo game/player.py

Para executar os testes:
    pytest tests/test_player.py -v
"""

import pytest
import sys
from pathlib import Path
import math

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.player import Player


class TestPlayerInitialization:
    """Testes de inicialização do Player"""

    def test_player_starts_at_origin(self):
        """Testa que jogador inicia na origem"""
        player = Player()
        assert player.x == 0.0
        assert player.y == 0.0
        assert player.z == 0.0

    def test_player_camera_starts_at_zero(self):
        """Testa que câmera inicia sem rotação"""
        player = Player()
        assert player.camera_pitch == 0.0
        assert player.camera_yaw == 0.0


class TestPlayerPosition:
    """Testes de posicionamento do Player"""

    def test_set_position(self):
        """Testa definir posição do jogador"""
        player = Player()
        player.set_position(5.0, 2.0, -3.0)
        assert player.x == 5.0
        assert player.y == 2.0
        assert player.z == -3.0

    def test_get_position(self):
        """Testa obter posição do jogador"""
        player = Player()
        player.set_position(1.0, 2.0, 3.0)
        pos = player.get_position()
        assert pos == (1.0, 2.0, 3.0)

    def test_get_grid_position(self):
        """Testa conversão para posição de grid"""
        player = Player()
        player.set_position(1.4, 0.0, 2.6)
        grid_pos = player.get_grid_position()
        assert grid_pos == (1, 0, 3)


class TestCameraRotation:
    """Testes de rotação da câmera"""

    def test_update_camera_yaw(self):
        """Testa atualização do yaw (horizontal)"""
        player = Player()
        initial_yaw = player.camera_yaw
        player.update_camera_rotation(100, 0)  # Move mouse para direita
        assert player.camera_yaw != initial_yaw

    def test_update_camera_pitch(self):
        """Testa atualização do pitch (vertical)"""
        player = Player()
        initial_pitch = player.camera_pitch
        player.update_camera_rotation(0, 100)  # Move mouse para baixo
        assert player.camera_pitch != initial_pitch

    def test_pitch_clamped_at_89_degrees(self):
        """Testa que pitch é limitado a ±89 graus"""
        player = Player()
        # Tenta rotacionar muito para cima
        player.update_camera_rotation(0, -10000)
        assert player.camera_pitch >= -89.0
        assert player.camera_pitch <= 89.0

        # Tenta rotacionar muito para baixo
        player.update_camera_rotation(0, 10000)
        assert player.camera_pitch >= -89.0
        assert player.camera_pitch <= 89.0

    def test_reset_camera(self):
        """Testa reset da câmera"""
        player = Player()
        player.update_camera_rotation(100, 50)
        player.reset_camera()
        assert player.camera_pitch == 0.0
        assert player.camera_yaw == 0.0


class TestCameraVectors:
    """Testes de vetores da câmera"""

    def test_get_camera_vectors_north(self):
        """Testa vetores quando olhando para norte (yaw=0)"""
        player = Player()
        player.camera_yaw = 0.0
        forward_x, forward_z, right_x, right_z = player.get_camera_vectors()

        # Olhando para norte: forward deve ser (0, -1) aproximadamente
        assert abs(forward_x) < 0.01
        assert forward_z < 0

    def test_get_camera_vectors_east(self):
        """Testa vetores quando olhando para leste (yaw=90)"""
        player = Player()
        player.camera_yaw = 90.0
        forward_x, forward_z, right_x, right_z = player.get_camera_vectors()

        # Olhando para leste: forward deve ser (1, 0) aproximadamente
        assert forward_x > 0
        assert abs(forward_z) < 0.01

    def test_get_facing_direction_north(self):
        """Testa direção cardinal quando olhando norte"""
        player = Player()
        player.camera_yaw = 0.0
        dir_x, dir_z = player.get_facing_direction()
        assert dir_x == 0 and dir_z == -1

    def test_get_facing_direction_east(self):
        """Testa direção cardinal quando olhando leste"""
        player = Player()
        player.camera_yaw = 90.0
        dir_x, dir_z = player.get_facing_direction()
        assert dir_x == 1 and dir_z == 0


class TestPlayerMovement:
    """Testes de movimento do jogador"""

    def test_move_forward_in_open_space(self):
        """Testa movimento para frente em espaço aberto"""
        player = Player()
        walls = []
        boxes = []

        # Move para frente
        moved = player.move(1.0, 0.0, 0.1, walls, boxes)

        assert moved
        # Posição deve ter mudado
        assert player.z != 0.0 or player.x != 0.0

    def test_no_move_with_zero_input(self):
        """Testa que não move com input zero"""
        player = Player()
        walls = []
        boxes = []
        initial_x, initial_z = player.x, player.z

        moved = player.move(0.0, 0.0, 0.1, walls, boxes)

        assert not moved
        assert player.x == initial_x
        assert player.z == initial_z

    def test_move_blocked_by_wall(self):
        """Testa que movimento é bloqueado por parede"""
        player = Player()
        player.set_position(0.0, 0.0, 0.0)

        # Parede logo na frente
        walls = [(0.0, 0.0, -1.0)]
        boxes = []

        # Tenta mover para frente (em direção à parede)
        player.move(1.0, 0.0, 0.1, walls, boxes)

        # Não deve ter atravessado a parede
        assert player.z > -1.5  # Não chegou muito perto da parede


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
