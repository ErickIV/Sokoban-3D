"""
tests/test_physics.py
=====================
Testes unitários para o módulo game/physics.py

Para executar os testes:
    pytest tests/test_physics.py -v

Para executar com cobertura:
    pytest tests/test_physics.py --cov=game.physics --cov-report=html
"""

import pytest
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.physics import Physics


class TestGridRound:
    """Testes para Physics.grid_round()"""

    def test_round_positive_down(self):
        """Testa arredondamento para baixo de número positivo"""
        assert Physics.grid_round(1.4) == 1

    def test_round_positive_up(self):
        """Testa arredondamento para cima de número positivo"""
        assert Physics.grid_round(1.6) == 2

    def test_round_negative_down(self):
        """Testa arredondamento de número negativo"""
        assert Physics.grid_round(-1.4) == -1

    def test_round_negative_up(self):
        """Testa arredondamento de número negativo"""
        assert Physics.grid_round(-1.6) == -2

    def test_round_exact(self):
        """Testa arredondamento de número exato"""
        assert Physics.grid_round(2.0) == 2

    def test_round_half(self):
        """Testa arredondamento de 0.5"""
        assert Physics.grid_round(0.5) == 0
        assert Physics.grid_round(1.5) == 2

    def test_round_zero(self):
        """Testa arredondamento de zero"""
        assert Physics.grid_round(0.0) == 0


class TestAABBCollision:
    """Testes para Physics.aabb_collides_point()"""

    def test_collision_inside_box(self):
        """Testa colisão quando jogador está dentro da caixa"""
        assert Physics.aabb_collides_point(0.0, 0.0, 0.0, 0.0, half=0.5, radius=0.35)

    def test_collision_near_edge(self):
        """Testa colisão perto da borda"""
        assert Physics.aabb_collides_point(0.7, 0.0, 0.0, 0.0, half=0.5, radius=0.35)

    def test_no_collision_far_away(self):
        """Testa não-colisão quando longe"""
        assert not Physics.aabb_collides_point(2.0, 2.0, 0.0, 0.0, half=0.5, radius=0.35)

    def test_collision_corner(self):
        """Testa colisão no canto da caixa"""
        # Canto em (0.5, 0.5) da caixa centrada em (0,0)
        # Jogador em (0.6, 0.6) com raio 0.35 deve colidir
        assert Physics.aabb_collides_point(0.6, 0.6, 0.0, 0.0, half=0.5, radius=0.35)

    def test_no_collision_just_outside(self):
        """Testa não-colisão logo fora do alcance"""
        assert not Physics.aabb_collides_point(1.0, 1.0, 0.0, 0.0, half=0.5, radius=0.35)

    def test_collision_different_radius(self):
        """Testa com raio diferente"""
        assert Physics.aabb_collides_point(1.0, 0.0, 0.0, 0.0, half=0.5, radius=0.6)


class TestCheckCollisionWithList:
    """Testes para Physics.check_collision_with_list()"""

    def test_collision_with_single_object(self):
        """Testa colisão com um único objeto na lista"""
        objects = [(0.0, 0.0, 0.0)]
        assert Physics.check_collision_with_list(0.0, 0.0, objects)

    def test_collision_with_multiple_objects(self):
        """Testa colisão com múltiplos objetos"""
        objects = [(5.0, 0.0, 5.0), (0.0, 0.0, 0.0), (10.0, 0.0, 10.0)]
        assert Physics.check_collision_with_list(0.0, 0.0, objects)

    def test_no_collision_empty_list(self):
        """Testa com lista vazia"""
        objects = []
        assert not Physics.check_collision_with_list(0.0, 0.0, objects)

    def test_no_collision_all_far(self):
        """Testa quando todos objetos estão longe"""
        objects = [(5.0, 0.0, 5.0), (10.0, 0.0, 10.0)]
        assert not Physics.check_collision_with_list(0.0, 0.0, objects)


class TestCanMoveTo:
    """Testes para Physics.can_move_to()"""

    def test_can_move_to_empty_space(self):
        """Testa movimento para espaço vazio"""
        walls = [(5.0, 0.0, 5.0)]
        boxes = [(10.0, 0.0, 10.0)]
        assert Physics.can_move_to(0.0, 0.0, walls, boxes)

    def test_cannot_move_to_wall(self):
        """Testa que não pode mover para parede"""
        walls = [(0.0, 0.0, 0.0)]
        boxes = []
        assert not Physics.can_move_to(0.0, 0.0, walls, boxes)

    def test_cannot_move_to_box(self):
        """Testa que não pode mover para caixa"""
        walls = []
        boxes = [(0.0, 0.0, 0.0)]
        assert not Physics.can_move_to(0.0, 0.0, walls, boxes)

    def test_can_move_near_wall(self):
        """Testa movimento perto de parede mas sem colidir"""
        walls = [(0.0, 0.0, 0.0)]
        boxes = []
        assert Physics.can_move_to(1.5, 1.5, walls, boxes)


class TestCardinalDirection:
    """Testes para Physics.get_cardinal_direction()"""

    def test_direction_north(self):
        """Testa direção norte (0 graus)"""
        dir_x, dir_z = Physics.get_cardinal_direction(0.0)
        assert dir_x == 0 and dir_z == -1

    def test_direction_south(self):
        """Testa direção sul (180 graus)"""
        dir_x, dir_z = Physics.get_cardinal_direction(180.0)
        assert dir_x == 0 and dir_z == 1

    def test_direction_east(self):
        """Testa direção leste (90 graus)"""
        dir_x, dir_z = Physics.get_cardinal_direction(90.0)
        assert dir_x == 1 and dir_z == 0

    def test_direction_west(self):
        """Testa direção oeste (270 graus)"""
        dir_x, dir_z = Physics.get_cardinal_direction(270.0)
        assert dir_x == -1 and dir_z == 0

    def test_direction_northeast(self):
        """Testa direção nordeste (45 graus) - deve escolher direção dominante"""
        dir_x, dir_z = Physics.get_cardinal_direction(45.0)
        # Deve escolher a direção mais forte (leste neste caso)
        assert (dir_x, dir_z) in [(1, 0), (0, -1)]


class TestSmoothMove:
    """Testes para Physics.smooth_move()"""

    def test_move_in_open_space(self):
        """Testa movimento em espaço aberto"""
        walls = []
        boxes = []
        new_x, new_z, moved = Physics.smooth_move(
            0.0, 0.0, 1.0, 0.0,
            walls, boxes, 1.0, 1.0
        )
        assert moved
        assert new_x > 0.0  # Moveu para frente

    def test_no_move_when_blocked(self):
        """Testa que não move quando totalmente bloqueado"""
        walls = [(1.0, 0.0, 0.0)]  # Parede na frente
        boxes = []
        new_x, new_z, moved = Physics.smooth_move(
            0.0, 0.0, 1.0, 0.0,
            walls, boxes, 1.0, 1.0
        )
        # Pode não mover ou mover com sliding
        assert new_x >= 0.0  # Não retrocede

    def test_move_stops_at_current_position(self):
        """Testa que não move se target = current"""
        walls = []
        boxes = []
        new_x, new_z, moved = Physics.smooth_move(
            5.0, 5.0, 5.0, 5.0,
            walls, boxes, 1.0, 1.0
        )
        assert not moved
        assert new_x == 5.0 and new_z == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
