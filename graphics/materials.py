"""
graphics/materials.py
=====================
Definições de materiais e sistema de iluminação profissional.
Implementa materiais PBR-like para paredes, chão, caixas e objetivos.
"""

from typing import Tuple
from OpenGL.GL import (
    glEnable, glLightfv, glLightModelfv, glLightModeli, glMaterialfv, glMaterialf, glLightf,
    GL_LIGHTING, GL_LIGHT0, GL_LIGHT1, GL_LIGHT2,
    GL_POSITION, GL_DIFFUSE, GL_SPECULAR, GL_AMBIENT,
    GL_LIGHT_MODEL_AMBIENT, GL_LIGHT_MODEL_TWO_SIDE, GL_SHININESS,
    GL_FRONT, GL_FRONT_AND_BACK, GL_TRUE,
    GL_CONSTANT_ATTENUATION, GL_LINEAR_ATTENUATION, GL_QUADRATIC_ATTENUATION
)


class Materials:
    """Gerenciador de materiais do jogo"""
    
    @staticmethod
    def apply_wall_material_varied(x: float, z: float) -> None:
        """
        Material de parede com variações procedurais baseadas na posição.
        Simula concreto com irregularidades naturais.

        Args:
            x: Posição X da parede (usada para seed de variação)
            z: Posição Z da parede (usada para seed de variação)
        """
        variation = (abs(x * 0.1) + abs(z * 0.1)) % 0.3 - 0.15
        base_color = 0.6 + variation * 0.1
        
        # Cores com variação sutil
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, 
                    (0.15, 0.15, 0.16 + variation * 0.02, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, 
                    (base_color, base_color, base_color + variation * 0.02, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, 
                    (0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 
                   4.0 + variation * 2.0)
    
    @staticmethod
    def apply_wall_material() -> None:
        """Material padrão para paredes (concreto sem variação)"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.15, 0.15, 0.16, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.62, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0)
    
    @staticmethod
    def apply_floor_material() -> None:
        """Material para o chão (grama realista com propriedades especulares)"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.4, 0.1, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.2, 0.8, 0.2, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.3, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 16.0)
    
    @staticmethod
    def apply_box_material(color: Tuple[float, float, float, float],
                          shininess: float = 32.0) -> None:
        """
        Material para caixas com cor personalizável.

        Args:
            color: Cor RGBA da caixa (valores 0.0-1.0)
            shininess: Brilho especular (0.0-128.0, padrão 32.0)
        """
        # Ambient mais escuro para melhor contraste
        ambient = [c * 0.5 for c in color[:3]] + [1.0]
        
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)


class Lighting:
    """Sistema de iluminação profissional com 3 luzes"""
    
    @staticmethod
    def setup() -> None:
        """
        Configura sistema de iluminação de 3 pontos profissional:
        - Key Light (Luz Principal): Sol amarelo quente
        - Fill Light (Luz de Preenchimento): Azul suave para sombras
        - Rim Light (Luz de Contorno): Adiciona profundidade e separação
        """
        # Habilita iluminação
        glEnable(GL_LIGHTING)
        
        # Configuração global de iluminação
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.25, 0.25, 0.30, 1.0))
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        
        # === LUZ PRINCIPAL (Sol) - LIGHT0 ===
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (15.0, 20.0, 10.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.22, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.85, 1.0))  # Amarelo suave
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.8, 0.8, 0.7, 1.0))
        
        # Atenuação realista
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.5)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.01)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.001)
        
        # === LUZ DE PREENCHIMENTO - LIGHT1 ===
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (-10.0, 12.0, -8.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.15, 0.15, 0.18, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.45, 0.55, 1.0))  # Azul suave
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.2, 0.2, 0.3, 1.0))
        
        # === LUZ DE CONTORNO - LIGHT2 ===
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, (0.0, 8.0, -15.0, 1.0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (0.1, 0.1, 0.12, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.3, 0.35, 0.4, 1.0))
        glLightfv(GL_LIGHT2, GL_SPECULAR, (0.4, 0.4, 0.5, 1.0))
