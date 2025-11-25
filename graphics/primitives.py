"""
graphics/primitives.py
======================
Formas geométricas primitivas e otimizadas para renderização.
Inclui cubos, grama 3D com Display Lists, e outras formas básicas.
"""

import random
import math
from OpenGL.GL import (
    glBegin, glEnd, glVertex3f, glNormal3f, glColor3f, glColor4f,
    glGenLists, glNewList, glEndList, glCallList, glDeleteLists,
    glEnable, glDisable, glBlendFunc,
    glPushMatrix, glPopMatrix, glTranslatef, glRotatef, glScalef, glLineWidth,
    GL_QUADS, GL_COMPILE, GL_LINES, GL_TRIANGLES, GL_TRIANGLE_FAN,
    GL_LIGHTING, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE,
    glTexCoord2f
)
from config import (
    GRASS_DENSITY, GRASS_AREA, GRASS_MIN_HEIGHT, GRASS_MAX_HEIGHT,
    GRASS_BLADE_WIDTH, PARTICLE_COUNT
)


class Primitives:
    """Gerenciador de formas geométricas primitivas"""
    
    # Display Lists para otimização
    _grass_display_list = None
    _cube_display_list = None
    
    @staticmethod
    def draw_unit_cube():
        """Desenha um cubo unitário centrado na origem"""
        hs = 0.5
        glBegin(GL_QUADS)
        
        # Frente
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0); glVertex3f(-hs, -hs, hs)
        glTexCoord2f(1, 0); glVertex3f(hs, -hs, hs)
        glTexCoord2f(1, 1); glVertex3f(hs, hs, hs)
        glTexCoord2f(0, 1); glVertex3f(-hs, hs, hs)
        
        # Trás
        glNormal3f(0, 0, -1)
        glTexCoord2f(1, 0); glVertex3f(-hs, -hs, -hs)
        glTexCoord2f(1, 1); glVertex3f(-hs, hs, -hs)
        glTexCoord2f(0, 1); glVertex3f(hs, hs, -hs)
        glTexCoord2f(0, 0); glVertex3f(hs, -hs, -hs)
        
        # Esquerda
        glNormal3f(-1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(-hs, -hs, -hs)
        glTexCoord2f(1, 0); glVertex3f(-hs, -hs, hs)
        glTexCoord2f(1, 1); glVertex3f(-hs, hs, hs)
        glTexCoord2f(0, 1); glVertex3f(-hs, hs, -hs)
        
        # Direita
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(hs, -hs, -hs)
        glTexCoord2f(0, 1); glVertex3f(hs, hs, -hs)
        glTexCoord2f(1, 1); glVertex3f(hs, hs, hs)
        glTexCoord2f(1, 0); glVertex3f(hs, -hs, hs)
        
        # Topo
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 1); glVertex3f(-hs, hs, -hs)
        glTexCoord2f(0, 0); glVertex3f(-hs, hs, hs)
        glTexCoord2f(1, 0); glVertex3f(hs, hs, hs)
        glTexCoord2f(1, 1); glVertex3f(hs, hs, -hs)
        
        # Base
        glNormal3f(0, -1, 0)
        glTexCoord2f(0, 0); glVertex3f(-hs, -hs, -hs)
        glTexCoord2f(1, 0); glVertex3f(hs, -hs, -hs)
        glTexCoord2f(1, 1); glVertex3f(hs, -hs, hs)
        glTexCoord2f(0, 1); glVertex3f(-hs, -hs, hs)
        
        glEnd()
    
    @staticmethod
    def create_grass_display_list():
        """
        Cria Display List otimizada para grama 3D.
        Performance boost de ~90% comparado a renderização por frame.
        """
        if Primitives._grass_display_list is not None:
            return Primitives._grass_display_list
        
        random.seed(42)  # Seed fixo para consistência
        
        # Cria nova display list
        Primitives._grass_display_list = glGenLists(1)
        glNewList(Primitives._grass_display_list, GL_COMPILE)
        
        # Gera toda a geometria da grama
        total_blades = GRASS_AREA * GRASS_AREA * GRASS_DENSITY
        
        for i in range(total_blades):
            # Posição aleatória
            gx = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            gz = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            
            # Propriedades aleatórias
            height = random.uniform(GRASS_MIN_HEIGHT, GRASS_MAX_HEIGHT)
            rotation = random.uniform(0, 360)
            color_var = random.uniform(-0.3, 0.3)
            
            # Desenha folha diretamente na display list
            glPushMatrix()
            glTranslatef(gx, -1.0, gz)
            glRotatef(rotation, 0, 1, 0)
            
            # Cor verde mais clara para combinar com o novo chão
            # Base: (0.4, 0.8, 0.4) com variação
            r = 0.3 + color_var * 0.1
            g = 0.75 + color_var * 0.2
            b = 0.3 + color_var * 0.1
            glColor3f(r, g, b)
            
            # Quad vertical (folha)
            glBegin(GL_QUADS)
            w = GRASS_BLADE_WIDTH
            
            # Frente
            glVertex3f(-w, 0, 0)
            glVertex3f(w, 0, 0)
            glVertex3f(w, height, 0)
            glVertex3f(-w, height, 0)
            
            # Trás (visível de ambos os lados)
            glVertex3f(-w, 0, 0)
            glVertex3f(-w, height, 0)
            glVertex3f(w, height, 0)
            glVertex3f(w, 0, 0)
            
            glEnd()
            glPopMatrix()
        
        glEndList()
        return Primitives._grass_display_list
    
    @staticmethod
    def draw_grass():
        """Renderiza grama usando Display List otimizada"""
        if Primitives._grass_display_list is None:
            Primitives.create_grass_display_list()
        
        if Primitives._grass_display_list is not None:
            glCallList(Primitives._grass_display_list)
    
    @staticmethod
    def draw_floor():
        """Desenha chão base com grama"""
        # Chão base verde
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.5, 0.15)
        
        glPushMatrix()
        glTranslatef(0.0, -1.0, 0.0)
        glScalef(40.0, 0.02, 40.0)
        
        hs = 0.5
        tiling = 20.0  # Repete a textura 20 vezes
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-hs, hs, -hs)
        glTexCoord2f(0, tiling); glVertex3f(-hs, hs, hs)
        glTexCoord2f(tiling, tiling); glVertex3f(hs, hs, hs)
        glTexCoord2f(tiling, 0); glVertex3f(hs, hs, -hs)
        glEnd()
        
        glPopMatrix()
        
        # Grama 3D otimizada
        Primitives.draw_grass()
        
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def draw_target_marker(x, y, z):
        """
        Desenha marcador de objetivo (círculo + X) com GLOW PULSANTE.

        Args:
            x, y, z: Posição do objetivo
        """
        import time

        glPushMatrix()
        glTranslatef(x, y - 0.95, z)
        glDisable(GL_LIGHTING)

        # Efeito de pulsação (respira entre 0.7 e 1.0)
        pulse = 0.85 + 0.15 * math.sin(time.time() * 2.5)

        # === GLOW LAYER 1 (mais externo, muito transparente) ===
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending para glow

        glColor4f(0.3, 0.8, 1.0, 0.15 * pulse)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius_outer = 0.55
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius_outer, 0, math.sin(angle) * radius_outer)
        glEnd()

        # === GLOW LAYER 2 (médio) ===
        glColor4f(0.2, 0.75, 1.0, 0.3 * pulse)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius_mid = 0.45
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius_mid, 0, math.sin(angle) * radius_mid)
        glEnd()

        # === CÍRCULO AZUL BASE ===
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.7, 1.0, 0.9)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius = 0.35
        for i in range(0, 361, 12):
            angle = math.radians(i)
from OpenGL.GL import (
    glBegin, glEnd, glVertex3f, glNormal3f, glTexCoord2f, glRotatef, glTranslatef, glScalef, glPushMatrix, glPopMatrix, glColor3f, glDisable, glEnable, GL_QUADS,
    GL_LIGHTING, glGenLists, glNewList, glEndList, GL_COMPILE, glCallList, glDeleteLists, glBlendFunc, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE,
    glTexCoord2f, glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    glDeleteTextures, GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
    GL_LINEAR, GL_CLAMP_TO_EDGE, GL_RGBA, GL_UNSIGNED_BYTE, glDepthMask, GL_TRUE, GL_FALSE, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T
)
import math
import random
import time
from config import (
    GRASS_DENSITY, GRASS_AREA, GRASS_MIN_HEIGHT, GRASS_MAX_HEIGHT,
    GRASS_BLADE_WIDTH, PARTICLE_COUNT
)

class Primitives:
    """Coleção de primitivas gráficas otimizadas"""
    
    _grass_display_list = None
    _cube_display_list = None
    _particle_texture_id = None

    @staticmethod
    def generate_particle_texture():
        """Gera textura procedural para partículas (glow melhorado)"""
        if Primitives._particle_texture_id is not None:
            return Primitives._particle_texture_id

        size = 64
        texture_data = []
        center = size / 2
        max_dist = size / 2

        for y in range(size):
            for x in range(size):
                # Distância do centro
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Gradiente radial suave com glow mais forte
                if dist > max_dist:
                    alpha = 0
                else:
                    # Função de decaimento suave (glow)
                    norm_dist = dist / max_dist
                    # Curve mais agressiva para centro mais brilhante
                    alpha = max(0, 1.0 - norm_dist)
                    alpha = math.pow(alpha, 1.5) # Menos agressivo que ^2 para melhor transição
                    # Boost adicional no centro
                    if norm_dist < 0.3:
                        alpha = min(1.0, alpha * 1.5)
                
                a = int(alpha * 255)
                texture_data.extend([255, 255, 255, a])

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes(texture_data))
        
        Primitives._particle_texture_id = tex_id
        return tex_id

    @staticmethod
    def draw_textured_particle(x, y, z, size, color, camera_pos):
        """
        Desenha partícula texturizada (billboard).
        """
        if Primitives._particle_texture_id is None:
            Primitives.generate_particle_texture()
            
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, Primitives._particle_texture_id)
        
        glPushMatrix()
        glTranslatef(x, y, z)
        
        # Billboard (encarar câmera)
        dx = camera_pos[0] - x
        dz = camera_pos[2] - z
        angle = math.degrees(math.atan2(dx, dz))
        glRotatef(angle, 0, 1, 0)
        
        glColor4f(color[0], color[1], color[2], color[3])
        
        hs = size / 2
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-hs, -hs, 0)
        glTexCoord2f(1, 0); glVertex3f(hs, -hs, 0)
        glTexCoord2f(1, 1); glVertex3f(hs, hs, 0)
        glTexCoord2f(0, 1); glVertex3f(-hs, hs, 0)
        glEnd()
        
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

    @staticmethod
    def draw_unit_cube():
        """Desenha um cubo unitário (1x1x1) centrado na origem"""
        if Primitives._cube_display_list is None:
            Primitives._cube_display_list = glGenLists(1)
            glNewList(Primitives._cube_display_list, GL_COMPILE)
            
            glBegin(GL_QUADS)
            # Frente
            glNormal3f(0, 0, 1)
            glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, 0.5)
            glTexCoord2f(1, 0); glVertex3f(0.5, -0.5, 0.5)
            glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, 0.5)
            glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, 0.5)
            # Trás
            glNormal3f(0, 0, -1)
            glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, -0.5)
            glTexCoord2f(1, 1); glVertex3f(-0.5, 0.5, -0.5)
            glTexCoord2f(0, 1); glVertex3f(0.5, 0.5, -0.5)
            glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, -0.5)
            # Direita
            glNormal3f(1, 0, 0)
            glTexCoord2f(1, 0); glVertex3f(0.5, -0.5, -0.5)
            glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, -0.5)
            glTexCoord2f(0, 1); glVertex3f(0.5, 0.5, 0.5)
            glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, 0.5)
            # Esquerda
            glNormal3f(-1, 0, 0)
            glTexCoord2f(0, 0); glVertex3f(-0.5, -0.5, -0.5)
            glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, 0.5)
            glTexCoord2f(1, 1); glVertex3f(-0.5, 0.5, 0.5)
            glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, -0.5)
            # Topo
            glNormal3f(0, 1, 0)
            glTexCoord2f(0, 1); glVertex3f(-0.5, 0.5, -0.5)
            glTexCoord2f(0, 0); glVertex3f(-0.5, 0.5, 0.5)
            glTexCoord2f(1, 0); glVertex3f(0.5, 0.5, 0.5)
            glTexCoord2f(1, 1); glVertex3f(0.5, 0.5, -0.5)
            # Base
            glNormal3f(0, -1, 0)
            glTexCoord2f(1, 1); glVertex3f(-0.5, -0.5, -0.5)
            glTexCoord2f(0, 1); glVertex3f(0.5, -0.5, -0.5)
            glTexCoord2f(0, 0); glVertex3f(0.5, -0.5, 0.5)
            glTexCoord2f(1, 0); glVertex3f(-0.5, -0.5, 0.5)
            glEnd()
            
            glEndList()
            
        glCallList(Primitives._cube_display_list)
    
    @staticmethod
    def create_grass_display_list():
        """
        Cria Display List otimizada para grama 3D.
        Performance boost de ~90% comparado a renderização por frame.
        """
        if Primitives._grass_display_list is not None:
            return Primitives._grass_display_list
        
        random.seed(42)  # Seed fixo para consistência
        
        # Cria nova display list
        Primitives._grass_display_list = glGenLists(1)
        glNewList(Primitives._grass_display_list, GL_COMPILE)
        
        # Gera toda a geometria da grama
        total_blades = GRASS_AREA * GRASS_AREA * GRASS_DENSITY
        
        for i in range(total_blades):
            # Posição aleatória
            gx = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            gz = random.uniform(-GRASS_AREA/2, GRASS_AREA/2)
            
            # Propriedades aleatórias
            height = random.uniform(GRASS_MIN_HEIGHT, GRASS_MAX_HEIGHT)
            rotation = random.uniform(0, 360)
            color_var = random.uniform(-0.3, 0.3)
            
            # Desenha folha diretamente na display list
            glPushMatrix()
            glTranslatef(gx, -1.0, gz)
            glRotatef(rotation, 0, 1, 0)
            
            # Cor verde mais clara para combinar com o novo chão
            # Base: (0.4, 0.8, 0.4) com variação
            r = 0.3 + color_var * 0.1
            g = 0.75 + color_var * 0.2
            b = 0.3 + color_var * 0.1
            glColor3f(r, g, b)
            
            # Quad vertical (folha)
            glBegin(GL_QUADS)
            w = GRASS_BLADE_WIDTH
            
            # Frente
            glVertex3f(-w, 0, 0)
            glVertex3f(w, 0, 0)
            glVertex3f(w, height, 0)
            glVertex3f(-w, height, 0)
            
            # Trás (visível de ambos os lados)
            glVertex3f(-w, 0, 0)
            glVertex3f(-w, height, 0)
            glVertex3f(w, height, 0)
            glVertex3f(w, 0, 0)
            
            glEnd()
            glPopMatrix()
        
        glEndList()
        return Primitives._grass_display_list
    
    @staticmethod
    def draw_grass():
        """Renderiza grama usando Display List otimizada"""
        if Primitives._grass_display_list is None:
            Primitives.create_grass_display_list()
        
        if Primitives._grass_display_list is not None:
            glCallList(Primitives._grass_display_list)
    
    @staticmethod
    def draw_floor():
        """Desenha chão base com grama"""
        # Chão base verde
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.5, 0.15)
        
        glPushMatrix()
        glTranslatef(0.0, -1.0, 0.0)
        glScalef(40.0, 0.02, 40.0)
        
        hs = 0.5
        tiling = 20.0  # Repete a textura 20 vezes
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-hs, hs, -hs)
        glTexCoord2f(0, tiling); glVertex3f(-hs, hs, hs)
        glTexCoord2f(tiling, tiling); glVertex3f(hs, hs, hs)
        glTexCoord2f(tiling, 0); glVertex3f(hs, hs, -hs)
        glEnd()
        
        glPopMatrix()
        
        # Grama 3D otimizada
        Primitives.draw_grass()
        
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def draw_target_marker(x, y, z):
        """
        Desenha marcador de objetivo (círculo + X) com GLOW PULSANTE.

        Args:
            x, y, z: Posição do objetivo
        """
        glPushMatrix()
        glTranslatef(x, y - 0.95, z)
        glDisable(GL_LIGHTING)

        # Efeito de pulsação (respira entre 0.7 e 1.0)
        pulse = 0.85 + 0.15 * math.sin(time.time() * 2.5)

        # === GLOW LAYER 1 (mais externo, muito transparente) ===
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending para glow

        glColor4f(0.3, 0.8, 1.0, 0.15 * pulse)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius_outer = 0.55
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius_outer, 0, math.sin(angle) * radius_outer)
        glEnd()

        # === GLOW LAYER 2 (médio) ===
        glColor4f(0.2, 0.75, 1.0, 0.3 * pulse)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius_mid = 0.45
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius_mid, 0, math.sin(angle) * radius_mid)
        glEnd()

        # === CÍRCULO AZUL BASE ===
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.7, 1.0, 0.9)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        radius = 0.35
        for i in range(0, 361, 12):
            angle = math.radians(i)
            glVertex3f(math.cos(angle) * radius, 0, math.sin(angle) * radius)
        glEnd()

        # === X VERMELHO COM GLOW ===
        # Glow do X (additive)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 0.3, 0.3, 0.4 * pulse)
        glLineWidth(12.0)
        glBegin(GL_LINES)
        glVertex3f(-0.28, 0.01, -0.28)
        glVertex3f(0.28, 0.01, 0.28)
        glVertex3f(0.28, 0.01, -0.28)
        glVertex3f(-0.28, 0.01, 0.28)
        glEnd()

        # X principal
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 0.0, 0.0, 1.0)
        glLineWidth(7.0)
        glBegin(GL_LINES)
        glVertex3f(-0.25, 0.01, -0.25)
        glVertex3f(0.25, 0.01, 0.25)
        glVertex3f(0.25, 0.01, -0.25)
        glVertex3f(-0.25, 0.01, 0.25)
        glEnd()

        glLineWidth(1.0)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    @staticmethod
    def draw_shadow(x, y, z, size=0.4, alpha=0.3):
        """
        Desenha sombra projetada no chão.
        
        Args:
            x, y, z: Posição da sombra
            size: Tamanho da sombra
            alpha: Transparência (0-1)
        """
        glPushMatrix()
        glTranslatef(x, -0.99, z)
        glDisable(GL_LIGHTING)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, alpha)
        
        glBegin(GL_QUADS)
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    @staticmethod
    def draw_particle(x, y, z, size=0.1, color=(1.0, 1.0, 0.0)):
        """Legacy: Mantido para compatibilidade se necessário"""
        Primitives.draw_unit_cube() # Placeholder
    
    @staticmethod
    def cleanup():
        """Libera recursos de Display Lists e Texturas"""
        if Primitives._grass_display_list is not None:
            glDeleteLists(Primitives._grass_display_list, 1)
            Primitives._grass_display_list = None
        
        if Primitives._cube_display_list is not None:
            glDeleteLists(Primitives._cube_display_list, 1)
            Primitives._cube_display_list = None
            
        if Primitives._particle_texture_id is not None:
            glDeleteTextures([Primitives._particle_texture_id])
            Primitives._particle_texture_id = None
