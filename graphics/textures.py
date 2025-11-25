"""
graphics/textures.py
====================
Gerenciador de texturas do jogo.
Suporta carregamento de imagens e geração procedural (fallback).
"""

import pygame
from OpenGL.GL import *

class TextureManager:
    """Gerenciador de texturas (Singleton)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TextureManager, cls).__new__(cls)
            cls._instance.textures = {}
        return cls._instance
    
    def load_texture(self, name, filepath=None):
        """
        Carrega uma textura ou gera uma procedural se falhar.
        
        Args:
            name: Nome identificador da textura
            filepath: Caminho do arquivo (opcional)
        """
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Configurações padrão
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        try:
            if filepath:
                image = pygame.image.load(filepath).convert_alpha()
                width, height = image.get_size()
                image_data = pygame.image.tostring(image, "RGBA", 1)
                
                # Convert to ctypes array
                import ctypes
                c_image_data = (GLubyte * len(image_data)).from_buffer_copy(image_data)
                
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, c_image_data)
            else:
                raise Exception("No filepath provided")
        except:
            # Fallback: Textura procedural realista
            self._create_procedural_texture(name)
            
        self.textures[name] = texture_id
        return texture_id
    
    def _create_procedural_texture(self, name):
        """Gera texturas procedurais mais realistas (noise-based)"""
        width, height = 64, 64
        data = bytearray(width * height * 4)
        
        import random
        random.seed(42) # Seed para consistência visual

        for y in range(height):
            for x in range(width):
                i = (y * width + x) * 4
                
                if name == 'floor':
                    # Grama: Variações de verde com ruído
                    noise = random.randint(-20, 20)
                    # Base verde grama (RGB aprox: 60, 160, 60)
                    r = max(0, min(255, 60 + noise))
                    g = max(0, min(255, 160 + noise))
                    b = max(0, min(255, 60 + noise))
                
                elif name == 'wall':
                    # Concreto: Cinza Claro (Mais claro como solicitado)
                    noise = random.randint(-20, 20)
                    # Base cinza mais clara (antes era 140)
                    gray = max(0, min(255, 190 + noise))
                    r, g, b = gray, gray, gray
                    
                    # Detalhe: Manchas ocasionais (poros do concreto)
                    if random.random() > 0.98:
                        r = max(0, r - 30)
                        g = max(0, g - 30)
                        b = max(0, b - 30)
                
                elif name == 'box':
                    # Madeira: Marrom com linhas horizontais (tábuas)
                    # Base marrom madeira
                    r, g, b = 180, 120, 60
                    
                    # Variação de ruído na madeira
                    noise = random.randint(-15, 15)
                    r = max(0, min(255, r + noise))
                    g = max(0, min(255, g + noise))
                    b = max(0, min(255, b + noise))
                    
                    # Linhas das tábuas (a cada 16 pixels)
                    if y % 16 == 0:
                        r = max(0, r - 50)
                        g = max(0, g - 50)
                        b = max(0, b - 50)
                    
                    # Borda reforçada da caixa
                    if x < 2 or x > width-3 or y < 2 or y > height-3:
                        r = 120; g = 80; b = 40
                    
                    # Diagonal simples para reforço visual
                    if abs(x - y) < 2 or abs(x - (height - y)) < 2:
                         r = max(0, r - 20)
                         g = max(0, g - 20)
                         b = max(0, b - 20)

                else:
                    # Fallback
                    r, g, b = 255, 0, 255
                
                data[i] = int(r)
                data[i+1] = int(g)
                data[i+2] = int(b)
                data[i+3] = 255
        
        # Convert to ctypes array
        import ctypes
        c_data = (GLubyte * len(data)).from_buffer_copy(data)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, c_data)

    def get_texture(self, name):
        """Retorna ID da textura"""
        return self.textures.get(name)

    def bind(self, name):
        """Ativa a textura"""
        tex_id = self.textures.get(name)
        if tex_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)
        else:
            glDisable(GL_TEXTURE_2D)
