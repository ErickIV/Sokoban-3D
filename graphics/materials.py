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
        Material de parede com variações procedurais APRIMORADAS.
        Simula concreto/pedra com irregularidades naturais realistas.

        Melhorias:
        - Variação de cor mais pronunciada
        - Tom ligeiramente mais quente (bege)
        - Especular mais realista para pedra
        - Variação de rugosidade (shininess)

        Args:
            x: Posição X da parede (usada para seed de variação)
            z: Posição Z da parede (usada para seed de variação)
        """
        import math

        # Variação procedural com múltiplas frequências (mais natural)
        variation1 = (abs(x * 0.1) + abs(z * 0.1)) % 0.3 - 0.15
        variation2 = math.sin(x * 0.3) * math.cos(z * 0.3) * 0.1

        # Combina variações para efeito mais orgânico
        variation = variation1 + variation2

        # Base color com tom bege/cinza quente
        base_r = 0.65 + variation * 0.12
        base_g = 0.62 + variation * 0.10
        base_b = 0.58 + variation * 0.08

        # Ambient com tom quente
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,
                    (base_r * 0.3, base_g * 0.3, base_b * 0.3, 1.0))

        # Diffuse mais colorido
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,
                    (base_r, base_g, base_b, 1.0))

        # Specular sutil (pedra tem leve brilho)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,
                    (0.15, 0.15, 0.14, 1.0))

        # Shininess variável (simula rugosidade diferente)
        shininess = 6.0 + abs(variation) * 8.0
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)
    
    @staticmethod
    def apply_wall_material() -> None:
        """Material padrão para paredes (concreto sem variação)"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.15, 0.15, 0.16, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 0.62, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0)
    
    @staticmethod
    def apply_floor_material() -> None:
        """
        Material para o chão (grama realista melhorada).

        Simula grama com:
        - Verde vibrante mais saturado
        - Specular sutil para simular orvalho
        - Shininess baixo (grama é mate, não brilhante)
        """
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.12, 0.45, 0.12, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.25, 0.85, 0.25, 1.0))  # Verde mais vibrante
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.15, 0.35, 0.15, 1.0))  # Leve brilho de orvalho
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 20.0)  # Shininess maior para orvalho
    
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
        Configura sistema de iluminação de 3 pontos APRIMORADO:
        - Key Light (Sol): Luz quente e intensa simulando sol do dia
        - Fill Light (Sky): Luz azul suave vinda do céu
        - Rim Light (Bounce): Luz de reflexão para contornos

        Características melhoradas:
        - Cores mais vivas e saturadas
        - Iluminação ambiente mais realista
        - Atenuação física correta
        - Specular highlights mais pronunciados
        """
        # Habilita iluminação
        glEnable(GL_LIGHTING)

        # Iluminação ambiente global melhorada (simula luz indireta)
        # Tom azulado suave vindo do céu
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.35, 0.38, 0.45, 1.0))
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        # Habilita cálculo de cores especulares separado
        from OpenGL.GL import GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR
        try:
            glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR)
        except:
            pass  # Se não disponível, ignora

        # === LUZ PRINCIPAL (Sol) - LIGHT0 ===
        # Simula luz solar direta - quente, brilhante, amarela
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (20.0, 30.0, 15.0, 1.0))  # Posição elevada
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.25, 0.24, 0.22, 1.0))   # Ambient quente
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 0.95, 0.8, 1.0))     # Amarelo sol intenso
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 0.9, 1.0))     # Specular brilhante

        # Atenuação suave (sol é distante, atenua pouco)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.8)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.005)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0001)

        # === LUZ DE PREENCHIMENTO (Céu) - LIGHT1 ===
        # Simula luz difusa vinda do céu azul - fria, suave
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (-15.0, 18.0, -12.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.18, 0.20, 0.25, 1.0))   # Ambient azulado
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.5, 0.6, 0.75, 1.0))     # Azul céu
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.3, 0.35, 0.45, 1.0))   # Specular frio

        # Atenuação média
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.015)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.0005)

        # === LUZ DE CONTORNO (Bounce Light) - LIGHT2 ===
        # Simula luz refletida do chão - adiciona profundidade
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, (5.0, 10.0, -20.0, 1.0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (0.12, 0.14, 0.16, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (0.4, 0.45, 0.5, 1.0))     # Cinza-azulado
        glLightfv(GL_LIGHT2, GL_SPECULAR, (0.5, 0.55, 0.6, 1.0))    # Specular médio

        # Atenuação moderada
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION, 0.02)
        glLightf(GL_LIGHT2, GL_QUADRATIC_ATTENUATION, 0.001)
