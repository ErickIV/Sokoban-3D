"""
graphics/visual_effects.py
===========================
Efeitos visuais avançados para melhorar realismo gráfico.

Este módulo implementa:
- Sistema de névoa atmosférica (fog)
- Skybox com gradiente de cores
- Sombras suaves e dinâmicas
- Efeitos de partículas aprimorados
- Simulação de ambient occlusion

TÉCNICAS GRÁFICAS:
-----------------
- Fog (GL_FOG) - Névoa exponencial para profundidade
- Vertex coloring - Gradientes no skybox
- Alpha blending - Sombras suaves
- Procedural shading - Variações de cor

USO:
----
```python
from graphics.visual_effects import VisualEffects

# Inicialização
VisualEffects.init()

# No loop de renderização
VisualEffects.render_skybox(player_pos)
```
"""

import math
import random
from typing import Tuple
from OpenGL.GL import (
    glEnable, glDisable, glFogi, glFogf, glFogfv,
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef, glScalef,
    glBegin, glEnd, glVertex3f, glColor3f, glColor4f,
    glBlendFunc, glDepthMask,
    GL_FOG, GL_FOG_MODE, GL_FOG_COLOR, GL_FOG_DENSITY,
    GL_FOG_START, GL_FOG_END, GL_EXP2, GL_LINEAR,
    GL_QUADS, GL_TRIANGLE_FAN, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE,
    GL_TRUE, GL_FALSE
)
from config import (
    FOG_ENABLED, FOG_COLOR, FOG_DENSITY, FOG_START, FOG_END,
    SKY_TOP_COLOR, SKY_HORIZON_COLOR, SKYBOX_ENABLED,
    SHADOW_SOFTNESS, SHADOW_INTENSITY, SHADOW_OFFSET_Y
)


class VisualEffects:
    """Gerenciador de efeitos visuais avançados"""

    @staticmethod
    def init() -> None:
        """
        Inicializa sistema de efeitos visuais.
        Configura névoa e outros efeitos globais.
        """
        if FOG_ENABLED:
            VisualEffects.setup_fog()

    @staticmethod
    def setup_fog() -> None:
        """
        Configura sistema de névoa atmosférica.

        Usa névoa exponencial quadrática (EXP2) para efeito mais realista
        de distância e profundidade.
        """
        glEnable(GL_FOG)

        # Modo de névoa (EXP2 = mais realista)
        glFogi(GL_FOG_MODE, GL_EXP2)

        # Cor da névoa (deve combinar com cor do céu)
        glFogfv(GL_FOG_COLOR, FOG_COLOR)

        # Densidade da névoa (quanto maior, mais densa)
        glFogf(GL_FOG_DENSITY, FOG_DENSITY)

        # Hint para melhor qualidade
        from OpenGL.GL import glHint, GL_FOG_HINT, GL_NICEST
        glHint(GL_FOG_HINT, GL_NICEST)

    @staticmethod
    def render_skybox(camera_x: float, camera_y: float, camera_z: float) -> None:
        """
        Renderiza skybox com gradiente de cores.

        Cria uma esfera de céu ao redor do jogador com gradiente
        do azul escuro (topo) para azul claro (horizonte).

        Args:
            camera_x: Posição X da câmera
            camera_y: Posição Y da câmera
            camera_z: Posição Z da câmera
        """
        if not SKYBOX_ENABLED:
            return

        # Desabilita escrita no depth buffer (skybox está "infinitamente" longe)
        glDepthMask(GL_FALSE)

        # Desabilita iluminação para cores puras
        from OpenGL.GL import glDisable, glEnable, GL_LIGHTING
        glDisable(GL_LIGHTING)

        glPushMatrix()

        # Skybox segue a câmera (sempre centralizado no jogador)
        glTranslatef(camera_x, camera_y, camera_z)

        # Renderiza cúpula do céu (hemisfério superior)
        VisualEffects._render_sky_dome()

        glPopMatrix()

        # Re-habilita iluminação e depth buffer
        from OpenGL.GL import glEnable, GL_LIGHTING
        glEnable(GL_LIGHTING)
        glDepthMask(GL_TRUE)

    @staticmethod
    def _render_sky_dome() -> None:
        """
        Renderiza cúpula do céu com gradiente vertical.

        Usa quads com vertex coloring para criar gradiente suave
        do topo (azul escuro) para o horizonte (azul claro).
        """
        radius = 100.0  # Raio da cúpula
        segments = 16   # Segmentos horizontais
        rings = 8       # Anéis verticais

        # Para cada anel vertical
        for ring in range(rings):
            # Ângulos vertical (de 0° no topo a 90° no horizonte)
            angle1 = (ring / rings) * (math.pi / 2)
            angle2 = ((ring + 1) / rings) * (math.pi / 2)

            y1 = radius * math.cos(angle1)
            y2 = radius * math.cos(angle2)
            r1 = radius * math.sin(angle1)
            r2 = radius * math.sin(angle2)

            # Interpola cor entre topo e horizonte
            t1 = ring / rings
            t2 = (ring + 1) / rings

            color1 = VisualEffects._lerp_color(SKY_TOP_COLOR, SKY_HORIZON_COLOR, t1)
            color2 = VisualEffects._lerp_color(SKY_TOP_COLOR, SKY_HORIZON_COLOR, t2)

            glBegin(GL_QUADS)

            # Para cada segmento horizontal
            for seg in range(segments):
                theta1 = (seg / segments) * 2 * math.pi
                theta2 = ((seg + 1) / segments) * 2 * math.pi

                # Vértice 1 (anel superior, segmento atual)
                x1 = r1 * math.cos(theta1)
                z1 = r1 * math.sin(theta1)
                glColor3f(*color1[:3])
                glVertex3f(x1, y1, z1)

                # Vértice 2 (anel inferior, segmento atual)
                x2 = r2 * math.cos(theta1)
                z2 = r2 * math.sin(theta1)
                glColor3f(*color2[:3])
                glVertex3f(x2, y2, z2)

                # Vértice 3 (anel inferior, próximo segmento)
                x3 = r2 * math.cos(theta2)
                z3 = r2 * math.sin(theta2)
                glColor3f(*color2[:3])
                glVertex3f(x3, y2, z3)

                # Vértice 4 (anel superior, próximo segmento)
                x4 = r1 * math.cos(theta2)
                z4 = r1 * math.sin(theta2)
                glColor3f(*color1[:3])
                glVertex3f(x4, y1, z4)

            glEnd()

    @staticmethod
    def _lerp_color(color1: Tuple[float, float, float, float],
                   color2: Tuple[float, float, float, float],
                   t: float) -> Tuple[float, float, float, float]:
        """
        Interpola linearmente entre duas cores.

        Args:
            color1: Cor inicial (RGBA)
            color2: Cor final (RGBA)
            t: Fator de interpolação (0.0 a 1.0)

        Returns:
            Cor interpolada (RGBA)
        """
        return (
            color1[0] + (color2[0] - color1[0]) * t,
            color1[1] + (color2[1] - color1[1]) * t,
            color1[2] + (color2[2] - color1[2]) * t,
            color1[3] + (color2[3] - color1[3]) * t
        )

    @staticmethod
    def draw_soft_shadow(x: float, y: float, z: float, size: float = 0.4) -> None:
        """
        Desenha sombra suave com gradiente radial.

        Cria sombra mais realista com borda suave (soft edge) usando
        alpha blending e múltiplos quads sobrepostos.

        Args:
            x: Posição X do objeto
            y: Posição Y do objeto (base)
            z: Posição Z do objeto
            size: Tamanho da sombra
        """
        # Desabilita iluminação para sombra
        from OpenGL.GL import glDisable, glEnable, GL_LIGHTING
        glDisable(GL_LIGHTING)

        glPushMatrix()
        glTranslatef(x, y + SHADOW_OFFSET_Y, z)

        # Rotaciona para ficar paralelo ao chão
        glRotatef(-90, 1, 0, 0)

        # Desenha sombra com gradiente (centro mais escuro, bordas transparentes)
        layers = 3  # Camadas para suavização

        for layer in range(layers, 0, -1):
            scale = (layer / layers) * size
            alpha = SHADOW_INTENSITY * (layer / layers) * SHADOW_SOFTNESS

            glBegin(GL_QUADS)
            glColor4f(0.0, 0.0, 0.0, alpha)
            glVertex3f(-scale, -scale, 0)
            glVertex3f(scale, -scale, 0)

            # Bordas mais transparentes
            glColor4f(0.0, 0.0, 0.0, alpha * 0.3)
            glVertex3f(scale, scale, 0)
            glVertex3f(-scale, scale, 0)
            glEnd()

        glPopMatrix()

        # Re-habilita iluminação
        glEnable(GL_LIGHTING)

    @staticmethod
    def draw_enhanced_particle(x: float, y: float, z: float,
                               size: float, color: Tuple[float, float, float],
                               alpha: float = 1.0) -> None:
        """
        Desenha partícula como ESFERA 3D com MULTI-LAYER GLOW EFFECT.

        Esferas 3D com brilho especular para efeito ultra realista!

        Args:
            x, y, z: Posição da partícula
            size: Tamanho da partícula (raio da esfera)
            color: Cor RGB (0.0-1.0)
            alpha: Opacidade (0.0-1.0)
        """
        from OpenGL.GL import glEnable, glMaterialfv, glMaterialf, GL_FRONT_AND_BACK, GL_SHININESS
        from OpenGL.GLUT import glutSolidSphere

        glPushMatrix()
        glTranslatef(x, y, z)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)

        # === ESFERA GLOW EXTERNA (grande e translúcida) ===
        # Material emissivo para glow
        glow_size = size * 2.0
        glow_color = [color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, alpha * 0.3]

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, glow_color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, glow_color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.8, 0.8, 0.8, alpha * 0.3])
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, alpha * 0.2])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 100.0)

        glutSolidSphere(glow_size, 8, 8)  # Baixa resolução para glow

        # === ESFERA PRINCIPAL (brilhante e opaca) ===
        # Cor vibrante com alto specular
        core_color = [
            min(1.0, color[0] + 0.2),
            min(1.0, color[1] + 0.2),
            min(1.0, color[2] + 0.2),
            alpha
        ]

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [c * 0.4 for c in core_color[:3]] + [alpha])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, core_color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, alpha])
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [color[0] * 0.6, color[1] * 0.6, color[2] * 0.6, alpha * 0.4])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 128.0)

        glutSolidSphere(size, 12, 12)  # Alta resolução para esfera principal

        # Limpa material emissivo
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

        glDisable(GL_BLEND)

        glPopMatrix()

    @staticmethod
    def apply_ambient_occlusion(x: float, y: float, z: float,
                                walls: list, radius: float = 1.5) -> float:
        """
        Simula ambient occlusion calculando proximidade de paredes.

        Escurece áreas próximas a cantos e paredes para melhor percepção
        de profundidade (AO simulado, não ray-traced real).

        Args:
            x, y, z: Posição para calcular AO
            walls: Lista de posições de paredes
            radius: Raio de influência

        Returns:
            Fator de escurecimento (0.0 = muito escuro, 1.0 = sem AO)
        """
        from config import AMBIENT_OCCLUSION_STRENGTH

        if AMBIENT_OCCLUSION_STRENGTH <= 0:
            return 1.0

        # Conta paredes próximas
        nearby_walls = 0
        max_checks = 8  # Limita checks por performance

        for wall in walls[:max_checks]:
            dist = math.sqrt(
                (wall[0] - x) ** 2 +
                (wall[1] - y) ** 2 +
                (wall[2] - z) ** 2
            )

            if dist < radius:
                # Quanto mais perto, mais influência
                influence = 1.0 - (dist / radius)
                nearby_walls += influence

        # Calcula fator de AO
        ao_factor = 1.0 - (nearby_walls * AMBIENT_OCCLUSION_STRENGTH * 0.1)
        return max(0.3, min(1.0, ao_factor))  # Clamp entre 0.3 e 1.0

    @staticmethod
    def draw_sun(camera_yaw: float, camera_pitch: float) -> None:
        """
        Desenha sol no céu.

        Renderiza um "sol" brilhante no skybox para adicionar mais
        realismo ao ambiente.

        Args:
            camera_yaw: Rotação horizontal da câmera
            camera_pitch: Rotação vertical da câmera
        """
        from OpenGL.GL import glDisable, glEnable, GL_LIGHTING, glPointSize
        glDisable(GL_LIGHTING)

        # Posição fixa do sol no céu
        sun_angle_h = 45  # graus horizontal
        sun_angle_v = 60  # graus vertical (alto no céu)
        distance = 80

        sun_x = distance * math.cos(math.radians(sun_angle_v)) * math.cos(math.radians(sun_angle_h))
        sun_y = distance * math.sin(math.radians(sun_angle_v))
        sun_z = distance * math.cos(math.radians(sun_angle_v)) * math.sin(math.radians(sun_angle_h))

        glPushMatrix()

        # Sol com glow
        glPointSize(50.0)
        glBegin(GL_TRIANGLE_FAN)

        # Centro brilhante (branco)
        glColor4f(1.0, 1.0, 0.9, 1.0)
        glVertex3f(sun_x, sun_y, sun_z)

        # Glow amarelo ao redor
        for i in range(17):
            angle = (i / 16.0) * 2 * math.pi
            offset = 3.0
            ox = offset * math.cos(angle)
            oz = offset * math.sin(angle)

            glColor4f(1.0, 0.9, 0.6, 0.0)
            glVertex3f(sun_x + ox, sun_y, sun_z + oz)

        glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)
