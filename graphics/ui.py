"""
graphics/ui.py
==============
Interface do usuário: HUD, menus, textos e crosshair.
Renderização 2D sobre a cena 3D.
"""

import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from config import *


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
    def draw_panel(x, y, width, height, alpha=0.75):
        """Desenha painel glassmorphism."""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.04, 0.08, 0.16, alpha)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        glLineWidth(1.5)
        glColor4f(0.4, 0.6, 1.0, 0.3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        glLineWidth(1.0)
        glDisable(GL_BLEND)
    
    @staticmethod
    def draw_progress_bar(x, y, width, height, progress, max_val=1.0):
        """Desenha barra de progresso."""
        norm = min(1.0, max(0.0, progress / max_val))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.2, 0.2, 0.25, 0.6)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        if norm > 0:
            fw = width * norm
            r = 0.2 if norm >= 1.0 else 0.0
            g = 1.0 if norm >= 1.0 else (0.8 if norm >= 0.5 else 0.6)
            b = 0.3 if norm >= 1.0 else (0.9 if norm >= 0.5 else 1.0)
            glBegin(GL_QUADS)
            glColor4f(r*0.7, g*0.7, b*0.7, 0.9)
            glVertex2f(x, y)
            glColor4f(r, g, b, 0.9)
            glVertex2f(x + fw, y)
            glVertex2f(x + fw, y + height)
            glColor4f(r*0.7, g*0.7, b*0.7, 0.9)
            glVertex2f(x, y + height)
            glEnd()
        glLineWidth(1.0)
        glColor4f(0.5, 0.5, 0.6, 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        glDisable(GL_BLEND)
    
    @staticmethod
    def draw_hud(level_index, stats, sound_manager=None):
        """
        Desenha HUD principal do jogo com visual moderno.
        
        Args:
            level_index: Índice do nível atual
            stats: Dict com estatísticas (boxes_on_target, total_boxes, move_count)
            sound_manager: Gerenciador de som para mostrar status
        """
        # Setup ortho 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # === PAINEL SUPERIOR ESQUERDO: INFO DO NÍVEL ===
        panel_x = 15
        panel_y = WINDOW_HEIGHT - 140
        panel_w = 280
        panel_h = 125
        UI.draw_panel(panel_x, panel_y, panel_w, panel_h)
        
        # Conteúdo do painel
        text_x = panel_x + 12
        text_y = panel_y + panel_h - 25
        
        # Nível
        glColor3f(1.0, 0.9, 0.2)  # Amarelo dourado
        UI.draw_text(text_x, text_y, f"* NIVEL {level_index + 1}", 18)
        
        # Caixas
        text_y -= 28
        glColor3f(0.9, 0.9, 1.0)
        UI.draw_text(text_x, text_y, 
            f"[] Caixas: {stats['boxes_on_target']}/{stats['total_boxes']}", 16)
        
        # Barra de progresso
        text_y -= 24
        bar_x = text_x + 4
        bar_w = panel_w - 70  # Reduzido para caber a porcentagem
        UI.draw_progress_bar(bar_x, text_y - 2, bar_w, 14, 
            stats['boxes_on_target'], stats['total_boxes'])
        
        # Porcentagem (na mesma linha, à direita)
        if stats['total_boxes'] > 0:
            pct = int((stats['boxes_on_target'] / stats['total_boxes']) * 100)
            glColor3f(0.7, 0.8, 0.9)
            pct_text = f"{pct}%"
            UI.draw_text(bar_x + bar_w + 10, text_y - 2, pct_text, 14)
        
        # Movimentos
        text_y -= 28
        glColor3f(0.9, 0.9, 1.0)
        UI.draw_text(text_x, text_y, f"# Movimentos: {stats['move_count']}", 16)
        
        # === PAINEL SUPERIOR DIREITO: CONTROLES DE ÁUDIO ===
        if sound_manager:
            audio_panel_w = 170
            audio_panel_h = 100
            audio_panel_x = WINDOW_WIDTH - audio_panel_w - 15
            audio_panel_y = WINDOW_HEIGHT - audio_panel_h - 15
            UI.draw_panel(audio_panel_x, audio_panel_y, audio_panel_w, audio_panel_h)
            
            audio_text_x = audio_panel_x + 12
            audio_text_y = audio_panel_y + audio_panel_h - 25
            
            # Música
            music_icon = "+" if sound_manager.music_enabled else "X"
            music_status = "ON" if sound_manager.music_enabled else "OFF"
            music_color = (0.5, 1.0, 0.5) if sound_manager.music_enabled else (0.8, 0.4, 0.4)
            glColor3f(*music_color)
            UI.draw_text(audio_text_x, audio_text_y, f"[{music_icon}] Musica [M]", 14)
            glColor3f(0.7, 0.7, 0.8)
            UI.draw_text(audio_text_x + 130, audio_text_y, music_status, 14)
            
            # Sons
            audio_text_y -= 25
            sfx_icon = "+" if sound_manager.sfx_enabled else "X"
            sfx_status = "ON" if sound_manager.sfx_enabled else "OFF"
            sfx_color = (0.5, 1.0, 0.5) if sound_manager.sfx_enabled else (0.8, 0.4, 0.4)
            glColor3f(*sfx_color)
            UI.draw_text(audio_text_x, audio_text_y, f"[{sfx_icon}] Sons   [N]", 14)
            glColor3f(0.7, 0.7, 0.8)
            UI.draw_text(audio_text_x + 130, audio_text_y, sfx_status, 14)

            # Pause Hint
            audio_text_y -= 25
            glColor3f(1.0, 1.0, 0.8)
            UI.draw_text(audio_text_x, audio_text_y, "[!] Pause  [P]", 14)

        # === PAINEL INFERIOR: DICAS E CONTROLES ===
        tip_panel_h = 50
        tip_panel_w = WINDOW_WIDTH - 30
        tip_panel_x = 15
        tip_panel_y = 15
        UI.draw_panel(tip_panel_x, tip_panel_y, tip_panel_w, tip_panel_h, alpha=0.65)
        
        tip_text_y = tip_panel_y + 28
        
        # Dica contextual
        if stats['boxes_on_target'] == 0:
            glColor3f(1.0, 0.8, 0.3)
            UI.draw_text(tip_panel_x + 12, tip_text_y, 
                "! Dica: Empurre as caixas para os alvos vermelhos!", 14)
        elif stats['boxes_on_target'] < stats['total_boxes']:
            glColor3f(0.6, 0.9, 1.0)
            UI.draw_text(tip_panel_x + 12, tip_text_y, 
                f"! Continue! Faltam {stats['total_boxes'] - stats['boxes_on_target']} caixas", 14)
        else:
            glColor3f(0.5, 1.0, 0.5)
            UI.draw_text(tip_panel_x + 12, tip_text_y, 
                "** Perfeito! Todas as caixas no lugar!", 14)
        
        # Controles (linha de baixo)
        tip_text_y -= 18
        glColor3f(0.6, 0.6, 0.7)
        UI.draw_text(tip_panel_x + 12, tip_text_y, 
            "WASD: mover | SHIFT: correr | Mouse: olhar | ESPAÇO: empurrar | R: reset", 12)
        
        # Restaura estados
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
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
    def get_text_width(text, size=18):
        """Retorna largura do texto em pixels"""
        font = GLUT_BITMAP_HELVETICA_18 if size >= 18 else GLUT_BITMAP_8_BY_13
        width = 0
        for ch in text:
            width += glutBitmapWidth(font, ord(ch))
        return width

    @staticmethod
    def draw_button(x, y, width, height, text, mouse_x, mouse_y, is_selected=False):
        """
        Desenha um botão interativo.
        
        Args:
            x, y: Centro do botão
            width, height: Dimensões
            text: Texto do botão
            mouse_x, mouse_y: Posição do mouse para hover
            is_selected: Se está selecionado (navegação teclado)
        """
        # Verifica hover
        half_w = width // 2
        half_h = height // 2
        is_hover = (x - half_w <= mouse_x <= x + half_w) and \
                   (y - half_h <= mouse_y <= y + half_h)
        
        # Cores
        if is_hover or is_selected:
            bg_color = (0.3, 0.6, 1.0, 0.8) # Azul claro
            border_color = (1.0, 1.0, 1.0, 1.0)
            scale = 1.05
        else:
            bg_color = (0.2, 0.2, 0.2, 0.6) # Cinza escuro
            border_color = (0.6, 0.6, 0.6, 1.0)
            scale = 1.0
            
        # Desenha fundo
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*bg_color)
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glScalef(scale, scale, 1.0)
        
        glBegin(GL_QUADS)
        glVertex2f(-half_w, -half_h)
        glVertex2f(half_w, -half_h)
        glVertex2f(half_w, half_h)
        glVertex2f(-half_w, half_h)
        glEnd()
        
        # Borda
        glLineWidth(2.0)
        glColor4f(*border_color)
        glBegin(GL_LINE_LOOP)
        glVertex2f(-half_w, -half_h)
        glVertex2f(half_w, -half_h)
        glVertex2f(half_w, half_h)
        glVertex2f(-half_w, half_h)
        glEnd()
        glLineWidth(1.0)
        
        glDisable(GL_BLEND)
        glPopMatrix()
        
        # Texto centralizado com precisão
        text_width = UI.get_text_width(text, 18)
        # Ajuste fino vertical (aprox 1/3 da altura da fonte para centralizar visualmente)
        text_y_offset = 5 
        UI.draw_text(x - text_width//2, y - text_y_offset, text, 18)

    @staticmethod
    def get_menu_buttons():
        """Retorna definições dos botões do menu (label, action, x_offset, y_offset)"""
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        return [
            ("NOVO JOGO", "start", 0, 80),
            ("CONTINUAR", "continue", 0, 20),
            ("CONFIGURAÇÕES", "settings", 0, -50),
            ("SAIR", "quit", 0, -120)
        ]

    @staticmethod
    def get_menu_action(mouse_x, mouse_y):
        """Retorna ação do botão clicado ou None"""
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        buttons = UI.get_menu_buttons()
        
        for label, action, x_off, y_off in buttons:
            bx = cx + x_off
            by = cy + y_off
            width, height = 200, 50
            
            if (bx - width//2 <= mouse_x <= bx + width//2) and \
               (by - height//2 <= mouse_y <= by + height//2):
                return action
        return None

    @staticmethod
    def draw_menu(sound_manager=None, mouse_pos=(0,0)):
        """
        Desenha menu principal com botões.
        
        Args:
            sound_manager: Gerenciador de som
            mouse_pos: Tupla (x, y) do mouse
        """
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        mx, my = mouse_pos
        # Inverte Y do mouse para coordenadas OpenGL (0 embaixo)
        gl_my = WINDOW_HEIGHT - my
        
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
        
        # Fundo gradiente (Azul Profundo)
        glBegin(GL_QUADS)
        glColor3f(0.02, 0.05, 0.1) # Topo escuro
        glVertex2f(0, WINDOW_HEIGHT)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glColor3f(0.1, 0.2, 0.4) # Base mais clara
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(0, 0)
        glEnd()
        
        # Título com sombra
        title = "BOXPUSH 3D"
        subtitle = "Sokoban Adventure"
        
        # Sombra do título
        glColor3f(0.0, 0.0, 0.0)
        UI.draw_text(cx - 160 + 2, cy + 180 - 2, title, 32)
        # Título Principal
        glColor3f(1.0, 0.9, 0.2) # Dourado
        UI.draw_text(cx - 160, cy + 180, title, 32)
        
        # Subtítulo
        glColor3f(0.7, 0.8, 1.0)
        UI.draw_text(cx - 120, cy + 140, subtitle, 18)
        
        # Linha decorativa
        glColor3f(0.3, 0.6, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx - 200, cy + 130)
        glVertex2f(cx + 200, cy + 130)
        glEnd()
        glLineWidth(1.0)
        
        # Botões
        buttons = UI.get_menu_buttons()
        for label, action, x_off, y_off in buttons:
            UI.draw_button(cx + x_off, cy + y_off, 220, 50, label, mx, gl_my)
        
        # Rodapé
        glColor3f(0.5, 0.5, 0.6)
        UI.draw_text(cx - 150, 30, "Desenvolvido com Pygame + OpenGL", 14)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def get_pause_buttons():
        """Retorna lista de botões do menu de pause: (label, action, x_off, y_off)"""
        return [
            ("CONTINUAR", "resume", 0, 40),
            ("SALVAR", "save", 0, -20),
            ("CONFIGURACOES", "settings", 0, -80),
            ("MENU PRINCIPAL", "main_menu", 0, -140)
        ]

    @staticmethod
    def get_pause_action(mouse_x, mouse_y):
        """Retorna ação do botão de pause clicado ou None"""
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        buttons = UI.get_pause_buttons()
        
        for label, action, x_off, y_off in buttons:
            bx = cx + x_off
            by = cy + y_off
            width, height = 220, 50
            
            if (bx - width//2 <= mouse_x <= bx + width//2) and \
               (by - height//2 <= mouse_y <= by + height//2):
                return action
        return None

    @staticmethod
    def draw_pause_menu(mouse_pos=(0,0)):
        """
        Desenha menu de pause sobre o jogo.
        """
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        mx, my = mouse_pos
        gl_my = WINDOW_HEIGHT - my
        
        # Overlay semi-transparente escuro
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Fundo escuro transparente (blur effect simulado)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()
        glDisable(GL_BLEND)
        
        # Título PAUSE
        glColor3f(1.0, 1.0, 1.0)
        UI.draw_text(cx - 60, cy + 120, "JOGO PAUSADO", 24)
        
        # Linha decorativa
        glColor3f(0.3, 0.6, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx - 150, cy + 100)
        glVertex2f(cx + 150, cy + 100)
        glEnd()
        glLineWidth(1.0)
        
        # Botões
        buttons = UI.get_pause_buttons()
        for label, action, x_off, y_off in buttons:
            UI.draw_button(cx + x_off, cy + y_off, 220, 50, label, mx, gl_my)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    @staticmethod
    def draw_slider(x, y, width, height, value, label, is_selected=False):
        """
        Desenha um slider com label.
            width, height: Dimensões da barra
            value: Valor atual (0.0 a 1.0)
            label: Texto do label
            is_selected: Se está selecionado
        """
        # Cores
        if is_selected:
            bar_color = (0.4, 0.4, 0.4, 1.0)
            fill_color = (0.3, 0.8, 1.0, 1.0) # Azul brilhante
            label_color = (1.0, 1.0, 0.0, 1.0) # Amarelo
        else:
            bar_color = (0.3, 0.3, 0.3, 1.0)
            fill_color = (0.2, 0.6, 0.8, 0.8)
            label_color = (1.0, 1.0, 1.0, 1.0)
            
        # Desenha a barra (Geometria)
        glPushMatrix()
        glTranslatef(x, y, 0)
        
        # Fundo da barra
        glColor4f(*bar_color)
        glBegin(GL_QUADS)
        glVertex2f(-width//2, -height//2)
        glVertex2f(width//2, -height//2)
        glVertex2f(width//2, height//2)
        glVertex2f(-width//2, height//2)
        glEnd()
        
        # Preenchimento (valor)
        fill_width = width * value
        glColor4f(*fill_color)
        glBegin(GL_QUADS)
        glVertex2f(-width//2, -height//2)
        glVertex2f(-width//2 + fill_width, -height//2)
        glVertex2f(-width//2 + fill_width, height//2)
        glVertex2f(-width//2, height//2)
        glEnd()
        
        # Knob (indicador)
        knob_x = -width//2 + fill_width
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(knob_x - 5, -height//2 - 4)
        glVertex2f(knob_x + 5, -height//2 - 4)
        glVertex2f(knob_x + 5, height//2 + 4)
        glVertex2f(knob_x - 5, height//2 + 4)
        glEnd()
        
        glPopMatrix()
        
        # Desenha Textos (Usando coordenadas absolutas pois draw_text reseta a matriz)
        
        # Label (Título) - Acima da barra
        text_w = len(label) * 9
        glColor3f(*label_color[:3])
        UI.draw_text(x - text_w//2, y + 25, label, 18)
        
        # Valor numérico - Ao lado direito
        if "Sensibilidade" in label:
            val_text = f"{value:.2f}"
        else:
            val_text = f"{int(value * 100)}%"
            
        glColor3f(1.0, 1.0, 1.0)
        UI.draw_text(x + width//2 + 15, y - 6, val_text, 16)

    @staticmethod
    def get_settings_sliders():
        """Retorna definições dos sliders (id, label, x_offset, y_offset, width)"""
        return [
            (0, "Volume Música", 0, 60, 300),
            (1, "Volume Efeitos", 0, -20, 300),
            (2, "Sensibilidade", 0, -100, 300)
        ]

    @staticmethod
    def get_settings_action(mouse_x, mouse_y):
        """
        Retorna ação de settings baseada no mouse.
        Retorna (action_type, data)
        action_type: 'slider_drag', 'back', None
        data: (slider_id, value) ou None
        """
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        
        # Verifica sliders
        sliders = UI.get_settings_sliders()
        for s_id, label, x_off, y_off, width in sliders:
            sx = cx + x_off
            sy = cy + y_off
            height = 20
            
            # Hitbox generosa para drag
            if (sx - width//2 - 10 <= mouse_x <= sx + width//2 + 10) and \
               (sy - height//2 - 10 <= mouse_y <= sy + height//2 + 10):
                
                # Calcula valor baseado na posição X relativa
                rel_x = mouse_x - (sx - width//2)
                val = max(0.0, min(1.0, rel_x / width))
                return ('slider_drag', (s_id, val))
        
        # Botão Voltar
        back_y = cy - 200
        # Corrigido: Largura 120 (metade 60)
        if (cx - 60 <= mouse_x <= cx + 60) and (back_y - 20 <= mouse_y <= back_y + 20):
            return ('back', None)
            
        return (None, None)

    @staticmethod
    def draw_settings_menu(selected_option, music_vol, sfx_vol, sensitivity, mouse_pos=(0,0)):
        """
        Desenha menu de configurações com sliders.
        """
        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2
        mx, my = mouse_pos
        gl_my = WINDOW_HEIGHT - my
        
        # Overlay escuro com gradiente radial (simulado)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Fundo
        glBegin(GL_QUADS)
        # Topo (Azul escuro)
        glColor3f(0.05, 0.1, 0.2)
        glVertex2f(0, WINDOW_HEIGHT)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        # Base (Preto)
        glColor3f(0.0, 0.0, 0.05)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(0, 0)
        glEnd()
        
        # Título
        glColor3f(1.0, 1.0, 1.0)
        UI.draw_text(cx - 100, cy + 160, "CONFIGURAÇÕES", 24)
        
        # Linha decorativa abaixo do título
        glColor3f(0.3, 0.6, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx - 120, cy + 150)
        glVertex2f(cx + 120, cy + 150)
        glEnd()
        glLineWidth(1.0)
        
        # Sliders
        # Normaliza sensibilidade para 0-1 (assumindo range 0.01 - 0.5)
        sens_norm = (sensitivity - 0.01) / (0.5 - 0.01)
        
        values = [music_vol, sfx_vol, sens_norm]
        sliders = UI.get_settings_sliders()
        
        for i, (s_id, label, x_off, y_off, width) in enumerate(sliders):
            val = values[i]
            UI.draw_slider(cx + x_off, cy + y_off, width, 20, val, label, i == selected_option)
        
        # Botão Voltar
        back_y = cy - 200
        UI.draw_button(cx, back_y, 120, 40, "VOLTAR", mx, gl_my)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
