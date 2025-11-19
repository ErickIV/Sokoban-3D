"""
graphics/ui.py
==============
Interface do usuário: HUD, menus, textos e crosshair.
Renderização 2D sobre a cena 3D.
"""

import math
import time
from OpenGL.GL import (
    glMatrixMode, glLoadIdentity, glPushMatrix, glPopMatrix,
    glColor3f, glColor4f, glBegin, glEnd, glVertex2f, glVertex3f, glRasterPos2f,
    glDisable, glEnable, glLineWidth, glBlendFunc, glPointSize,
    GL_PROJECTION, GL_MODELVIEW, GL_DEPTH_TEST, GL_LINES, GL_LINE_LOOP,
    GL_LIGHTING, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_QUADS, GL_POINTS
)
from OpenGL.GL import glOrtho
from OpenGL.GLU import gluOrtho2D
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12, GLUT_BITMAP_8_BY_13, glutBitmapCharacter
from config import GAME_STATE_MENU, WINDOW_WIDTH, WINDOW_HEIGHT


class UI:
    """Gerenciador de interface do usuário"""
    
    @staticmethod
    def draw_text(x, y, text, size=18):
        """
        Desenha texto 2D na tela com sombra.
        
        Args:
            x, y: Posição na tela
            text: Texto a ser desenhado
            size: Tamanho da fonte
        """
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Sombra (preto)
        glColor3f(0.0, 0.0, 0.0)
        glRasterPos2f(x + 1, y - 1)
        font = GLUT_BITMAP_HELVETICA_18 if size >= 18 else GLUT_BITMAP_8_BY_13
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        
        # Texto (branco)
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def draw_crosshair():
        """Desenha crosshair no centro da tela"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        size = 12
        thickness = 2
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 1.0, 0.8)
        
        # Linha horizontal
        glBegin(GL_QUADS)
        glVertex2f(cx - size, cy - thickness//2)
        glVertex2f(cx + size, cy - thickness//2)
        glVertex2f(cx + size, cy + thickness//2)
        glVertex2f(cx - size, cy + thickness//2)
        glEnd()
        
        # Linha vertical
        glBegin(GL_QUADS)
        glVertex2f(cx - thickness//2, cy - size)
        glVertex2f(cx + thickness//2, cy - size)
        glVertex2f(cx + thickness//2, cy + size)
        glVertex2f(cx - thickness//2, cy + size)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def draw_hud(level_index, stats, sound_manager=None, show_hints=True, perf_stats=None):
        """
        Desenha HUD principal do jogo.

        Args:
            level_index: Índice do nível atual
            stats: Dict com estatísticas (boxes_on_target, total_boxes, move_count)
            sound_manager: Gerenciador de som para mostrar status
            show_hints: Se deve mostrar hints de controles (toggle com H)
            perf_stats: Estatísticas de performance (FPS, frame time, etc)
        """
        y = WINDOW_HEIGHT - 36

        # Hints de controles (toggle com H)
        if show_hints:
            UI.draw_text(20, y,
                "WASD: mover | SHIFT: correr | Mouse: olhar | ESPAÇO: empurrar",
                16)
            y -= 28
            UI.draw_text(20, y,
                "R: reset | P: pause | H: hints | F11: fullscreen | ESC: sair",
                16)
            y -= 32
        else:
            # Apenas indicador pequeno
            UI.draw_text(20, y, "Pressione H para ver controles", 14)
            y -= 32

        # Status do nível
        UI.draw_text(20, y,
            f"Level {level_index + 1} | Caixas: {stats['boxes_on_target']}/{stats['total_boxes']}",
            18)

        # Movimentos
        y -= 32
        UI.draw_text(20, y, f"Movimentos: {stats['move_count']}", 18)

        # FPS counter (se disponível)
        if perf_stats:
            y -= 32
            fps = perf_stats.get('fps', 0.0)
            frame_time = perf_stats.get('frame_time_ms', 0.0)

            # Cor baseada em performance
            if fps >= 90:
                fps_color = (0.2, 1.0, 0.2)  # Verde (excelente)
            elif fps >= 60:
                fps_color = (1.0, 1.0, 0.2)  # Amarelo (bom)
            elif fps >= 30:
                fps_color = (1.0, 0.6, 0.2)  # Laranja (razoável)
            else:
                fps_color = (1.0, 0.2, 0.2)  # Vermelho (ruim)

            # Desenha FPS com cor apropriada
            glColor3f(*fps_color)
            UI.draw_text(20, y, f"FPS: {fps:.1f} ({frame_time:.1f}ms)", 16)
            glColor3f(1.0, 1.0, 1.0)  # Restaura cor branca

        # Status de áudio (canto superior direito)
        if sound_manager:
            audio_y = WINDOW_HEIGHT - 36
            audio_x = WINDOW_WIDTH - 150

            # Status da música
            music_status = "🎵 ON" if sound_manager.music_enabled else "🔇 OFF"
            UI.draw_text(audio_x, audio_y, f"M: {music_status}", 16)

            # Status dos sons
            audio_y -= 28
            sfx_status = "🔊 ON" if sound_manager.sfx_enabled else "🔇 OFF"
            UI.draw_text(audio_x, audio_y, f"N: {sfx_status}", 16)

        # Dicas de gameplay
        if show_hints:
            y -= 32
            if stats['boxes_on_target'] == 0:
                UI.draw_text(20, y,
                    "Dica: Empurre as caixas para os X vermelhos!", 16)
            elif stats['boxes_on_target'] < stats['total_boxes']:
                UI.draw_text(20, y,
                    "Continue empurrando as caixas restantes!", 16)
    
    @staticmethod
    def draw_victory_screen(move_count):
        """Desenha tela de vitória de nível"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Overlay verde semi-transparente
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.8, 0.0, 0.7)
        
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Texto
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        
        UI.draw_text(cx - 100, cy + 50, "PARABÉNS! LEVEL COMPLETO!", 24)
        UI.draw_text(cx - 80, cy, f"Movimentos: {move_count}", 18)
        UI.draw_text(cx - 180, cy - 50, 
            "Pressione ENTER para o Próximo Level / ESC para sair", 18)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def draw_final_victory_screen():
        """Desenha tela de vitória final (todos os níveis completos)"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Fundo com gradiente
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.05, 0.2)  # Roxo escuro
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glColor3f(0.2, 0.1, 0.4)  # Roxo claro
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        
        # Estrelas cintilantes
        import random
        random.seed(42)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(100):
            x = random.randint(50, WINDOW_WIDTH - 50)
            y = random.randint(50, WINDOW_HEIGHT - 50)
            brightness = 0.5 + 0.5 * abs(math.sin(time.time() * 3 + i * 0.1))
            glColor3f(brightness, brightness, brightness)
            glVertex2f(x, y)
        glEnd()
        
        # Textos
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        
        glColor3f(1.0, 0.8, 0.0)  # Dourado
        UI.draw_text(cx - 80, WINDOW_HEIGHT - 100, "PARABÉNS!", 36)
        
        glColor3f(0.9, 0.9, 0.9)
        UI.draw_text(cx - 180, WINDOW_HEIGHT - 150, 
            "VOCÊ CONQUISTOU TODOS OS DESAFIOS!", 20)
        
        # Troféu ASCII
        trophy_lines = [
            "    🏆",
            "  ╔═══╗",
            "  ║ ★ ║",
            "  ╚═══╝",
            "   ███"
        ]
        
        for i, line in enumerate(trophy_lines):
            UI.draw_text(cx - 30, cy + (len(trophy_lines) - i) * 20, line, 14)
        
        # Instruções
        glColor3f(0.8, 0.8, 0.8)
        UI.draw_text(cx - 150, 120, 
            "Pressione ENTER para voltar ao menu", 14)
        UI.draw_text(cx - 60, 100, "ou ESC para sair", 14)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def draw_menu(sound_manager=None):
        """
        Desenha menu principal
        
        Args:
            sound_manager: Gerenciador de som para mostrar status
        """
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        
        # Overlay escuro
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.6)
        
        glBegin(GL_QUADS)
        glVertex2f(0, cy + 180)
        glVertex2f(WINDOW_WIDTH, cy + 180)
        glVertex2f(WINDOW_WIDTH, cy - 150)
        glVertex2f(0, cy - 150)
        glEnd()
        
        glDisable(GL_BLEND)
        
        # Textos do menu
        UI.draw_text(cx - 160, cy + 120, "🎮 BOXPUSH 3D SOKOBAN 🎮", 24)
        UI.draw_text(cx - 120, cy + 80, 
            "Empurre as caixas para os objetivos!", 18)
        UI.draw_text(cx - 80, cy + 50, "🎯 5 NÍVEIS DESAFIADORES 🎯", 16)
        
        UI.draw_text(cx - 100, cy + 10, "⏎ ENTER - Começar Jogo", 18)
        UI.draw_text(cx - 60, cy - 20, "⎋ ESC - Sair", 18)
        
        UI.draw_text(cx - 180, cy - 60, 
            "Controles: WASD=Mover | SHIFT=Correr | Mouse=Olhar | Espaço=Empurrar", 
            14)
        UI.draw_text(cx - 120, cy - 85, 
            "M=Música ON/OFF | N=Sons ON/OFF | R=Reiniciar", 
            14)
        
        # Status de áudio
        if sound_manager:
            audio_y = cy - 120
            music_status = "🎵 ON" if sound_manager.music_enabled else "🔇 OFF"
            sfx_status = "🔊 ON" if sound_manager.sfx_enabled else "🔇 OFF"
            UI.draw_text(cx - 100, audio_y, 
                f"Música: {music_status} | Sons: {sfx_status}", 16)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
