"""
graphics/renderer.py
====================
Sistema central de renderização do jogo.
Gerencia toda a pipeline de renderização 3D usando OpenGL.

PIPELINE DE RENDERIZAÇÃO:
-------------------------
1. Configuração de Perspectiva (gluPerspective)
2. Setup de Câmera em Primeira Pessoa
3. Sistema de Iluminação (luz direcional + ambient)
4. Renderização de Geometria 3D:
   - Chão com grid
   - Paredes (cubos texturizados)
   - Caixas (com cores dinâmicas baseadas no estado)
   - Objetivos (marcadores X no chão)
   - Sombras (projeção simples)
5. Efeitos de Partículas (sistema de feedback visual)
6. HUD 2D (overlay em ortho2D)

TÉCNICAS GRÁFICAS:
-----------------
- Depth Testing (Z-buffer)
- Back-face Culling
- Smooth Shading (Gouraud)
- Blending para transparências
- Materiais com propriedades especular/diffuse/ambient
- Sistema de cores procedurais para feedback visual

ESTADOS VISUAIS DAS CAIXAS:
--------------------------
- normal: Marrom (caixa comum)
- on_target: Dourado (no objetivo correto)
- pushable: Verde (pode ser empurrada)
- blocked: Vermelho (bloqueada)
"""

import math
from typing import List, Tuple, Optional
from OpenGL.GL import (
    glEnable, glDisable, glCullFace, glBlendFunc, glHint, glClearColor,
    glMatrixMode, glLoadIdentity, glPushMatrix, glPopMatrix,
    glTranslatef, glRotatef, glScalef, glColor3f, glColor4f, glBegin, glEnd, glVertex3f,
    glClear, glViewport,
    GL_DEPTH_TEST, GL_CULL_FACE, GL_BACK, GL_LINE_SMOOTH, GL_POINT_SMOOTH,
    GL_NICEST, GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION, GL_MODELVIEW, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINES, GL_QUADS, GL_LINE_SMOOTH_HINT, GL_POINT_SMOOTH_HINT, GL_LIGHTING
)
from OpenGL.GLU import gluPerspective
from config import (
    FOV, NEAR_PLANE, FAR_PLANE, PLAYER_EYE_HEIGHT, SKY_COLOR, PARTICLE_LIFETIME, PARTICLE_COUNT,
    BOX_INTERACTION_DISTANCE, BOX_COLOR_ON_TARGET, BOX_SHININESS_ON_TARGET,
    BOX_COLOR_PUSHABLE, BOX_SHININESS_PUSHABLE, BOX_COLOR_BLOCKED, BOX_SHININESS_BLOCKED,
    BOX_COLOR_NORMAL, BOX_SHININESS_NORMAL
)
from .materials import Materials, Lighting
from .primitives import Primitives
from .ui import UI
from .clouds import CloudSystem
from .visual_effects import VisualEffects


class Renderer:
    """Gerenciador de renderização 3D"""
    
    @staticmethod
    def init_opengl():
        """Inicializa OpenGL com todas as configurações"""
        # Depth test e culling
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Suavização (anti-aliasing)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        # Multisample anti-aliasing
        from OpenGL.GL import GL_MULTISAMPLE, glEnable as gl_enable
        try:
            from config import MULTISAMPLE_SAMPLES
            if MULTISAMPLE_SAMPLES > 0:
                gl_enable(GL_MULTISAMPLE)
        except:
            pass  # Se não disponível, continua sem

        # Blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Sistema de iluminação profissional
        Lighting.setup()

        # Material padrão
        Materials.apply_wall_material()

        # Cor de fundo (céu)
        glClearColor(*SKY_COLOR)

        # Inicializa efeitos visuais (fog, etc)
        VisualEffects.init()
    
    @staticmethod
    def set_perspective(width: int, height: int) -> None:
        """
        Configura matriz de projeção perspectiva.

        Args:
            width: Largura da janela em pixels
            height: Altura da janela em pixels
        """
        # Atualiza viewport para corresponder ao tamanho da janela
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, width / float(height), NEAR_PLANE, FAR_PLANE)
        glMatrixMode(GL_MODELVIEW)
    
    @staticmethod
    def setup_camera(player) -> None:
        """
        Configura câmera em primeira pessoa.

        Args:
            player: Objeto Player com posição e rotação
        """
        glLoadIdentity()
        
        # Rotação da câmera
        glRotatef(player.camera_pitch, 1, 0, 0)
        glRotatef(player.camera_yaw, 0, 1, 0)
        
        # Posição da câmera (inverte pois é a câmera que move)
        glTranslatef(-player.x, -PLAYER_EYE_HEIGHT, -player.z)
    
    @staticmethod
    def draw_wall(x: float, y: float, z: float) -> None:
        """
        Desenha uma parede.

        Args:
            x: Posição X da parede
            y: Posição Y da parede
            z: Posição Z da parede
        """
        Materials.apply_wall_material_varied(x, z)
        glPushMatrix()
        glTranslatef(x, y + 0.0, z)
        glScalef(1.0, 2.0, 1.0)
        Primitives.draw_unit_cube()
        glPopMatrix()
    
    @staticmethod
    def draw_box(x: float, y: float, z: float, status: str = 'normal') -> None:
        """
        Desenha uma caixa com cor baseada no status.

        Args:
            x: Posição X da caixa
            y: Posição Y da caixa
            z: Posição Z da caixa
            status: Estado visual - 'normal', 'on_target', 'pushable', 'blocked'
        """
        glPushMatrix()
        glTranslatef(x, y - 0.5, z)
        glScalef(1.0, 1.0, 1.0)
        
        # Define cor baseada no status
        if status == 'on_target':
            color = BOX_COLOR_ON_TARGET
            shininess = BOX_SHININESS_ON_TARGET
        elif status == 'pushable':
            color = BOX_COLOR_PUSHABLE
            shininess = BOX_SHININESS_PUSHABLE
        elif status == 'blocked':
            color = BOX_COLOR_BLOCKED
            shininess = BOX_SHININESS_BLOCKED
        else:  # normal
            color = BOX_COLOR_NORMAL
            shininess = BOX_SHININESS_NORMAL
        
        Materials.apply_box_material(color, shininess)
        Primitives.draw_unit_cube()
        
        # Restaura material padrão
        Materials.apply_wall_material()
        
        glPopMatrix()
    
    @staticmethod
    def get_box_status(box_pos: Tuple[float, float, float],
                      objectives: List[Tuple[float, float, float]],
                      player, level) -> str:
        """
        Determina status visual de uma caixa.
        CORRIGIDO: Detecção mais precisa e confiável.

        Args:
            box_pos: Posição da caixa (tupla (x, y, z))
            objectives: Lista de posições de objetivos
            player: Objeto Player com posição e direção
            level: Objeto Level com métodos de lógica

        Returns:
            Status da caixa: 'normal', 'on_target', 'pushable', ou 'blocked'
        """
        # Caixa no objetivo (prioridade máxima)
        if box_pos in objectives:
            return 'on_target'
        
        # Obtém posição do jogador no grid
        from game.physics import Physics
        px = Physics.grid_round(player.x)
        pz = Physics.grid_round(player.z)
        
        # Obtém direção que o jogador está olhando
        dir_x, dir_z = player.get_facing_direction()
        
        # Calcula posição da caixa na frente do jogador
        box_in_front_x = px + dir_x
        box_in_front_z = pz + dir_z
        
        # Verifica se ESTA caixa está na frente do jogador
        # Compara apenas X e Z (ignora Y que é sempre 0)
        if box_pos[0] == box_in_front_x and box_pos[2] == box_in_front_z:
            # Verifica distância para evitar detecção de longe
            # Calcula distância Chebyshev (max de diferenças absolutas)
            dist_x = abs(player.x - box_pos[0])
            dist_z = abs(player.z - box_pos[2])
            max_dist = max(dist_x, dist_z)

            # Só considera se estiver dentro do alcance de interação
            if max_dist <= BOX_INTERACTION_DISTANCE:
                # Verifica se pode empurrar nesta direção
                can_push, _, _ = level.can_push_box(player.x, player.z, dir_x, dir_z)
                return 'pushable' if can_push else 'blocked'
        
        return 'normal'
    
    @staticmethod
    def draw_particles(particles: List[Tuple[float, float, float, float]],
                      current_time: float) -> None:
        """
        Desenha partículas de efeito.

        Args:
            particles: Lista de tuplas (x, y, z, start_time)
            current_time: Tempo atual em segundos
        """
        glDisable(GL_LIGHTING)
        
        for (x, y, z, start_t) in particles:
            elapsed = current_time - start_t
            
            if elapsed < PARTICLE_LIFETIME:
                # Animação de partículas em espiral
                for i in range(PARTICLE_COUNT):
                    angle = (i / PARTICLE_COUNT) * 2 * math.pi
                    offset = elapsed * 2.0
                    
                    px = x + math.cos(angle + elapsed * 3) * offset
                    pz = z + math.sin(angle + elapsed * 3) * offset
                    py = y - 0.2 + math.sin(elapsed * 5) * 0.3 + 0.3
                    
                    # Partículas aprimoradas com glow
                    # Calcula alpha baseado no tempo (fade out)
                    fade = 1.0 - (elapsed / PARTICLE_LIFETIME)
                    VisualEffects.draw_enhanced_particle(
                        px, py, pz, 0.08, (1.0, 1.0, 0.0), alpha=fade
                    )
        
        glEnable(GL_LIGHTING)
    
    @staticmethod
    def render_game_scene(level, player, current_time: float,
                         sound_manager=None, show_hints: bool = True) -> None:
        """
        Renderiza cena principal do jogo.

        Args:
            level: Objeto Level com paredes, caixas, objetivos
            player: Objeto Player com posição e câmera
            current_time: Tempo atual em segundos
            sound_manager: Gerenciador de som (opcional)
            show_hints: Se deve mostrar hints de controles
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Configura câmera
        Renderer.setup_camera(player)

        # Desenha skybox primeiro (fundo infinito)
        VisualEffects.render_skybox(player.x, PLAYER_EYE_HEIGHT, player.z)

        # Desenha nuvens (no fundo, antes da geometria)
        if hasattr(level, 'clouds') and level.clouds:
            level.clouds.render((player.x, PLAYER_EYE_HEIGHT, player.z))
        
        # Desenha chão
        Primitives.draw_floor()
        
        # Desenha paredes
        for (x, y, z) in level.walls:
            Renderer.draw_wall(x, y, z)
        
        # Desenha objetivos
        for (x, y, z) in level.objectives:
            Primitives.draw_target_marker(x, y, z)
        
        # Desenha caixas com sombras suaves
        for (x, y, z) in level.boxes:
            status = Renderer.get_box_status((x, y, z), level.objectives, player, level)
            Renderer.draw_box(x, y, z, status)
            # Usa sombra suave aprimorada
            VisualEffects.draw_soft_shadow(x, y, z, size=0.45)
        
        # Desenha partículas
        Renderer.draw_particles(level.particles, current_time)
        
        # Desenha HUD com estatísticas de performance
        stats = level.get_progress_stats()

        # Obtém estatísticas de performance se disponível
        perf_stats = None
        try:
            from utils.performance import get_performance_monitor
            perf_stats = get_performance_monitor().get_stats()
        except:
            pass  # Se não disponível, continua sem mostrar FPS

        UI.draw_hud(level.current_level_index, stats, sound_manager, show_hints, perf_stats)
        UI.draw_crosshair()
    
    @staticmethod
    def render_menu_background() -> None:
        """Renderiza fundo 3D para o menu"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Câmera fixa para o menu
        glRotatef(-20, 1, 0, 0)
        glRotatef(30, 0, 1, 0)
        glTranslatef(-2, -1, -8)
        
        glEnable(GL_LIGHTING)
        
        # Chão de demonstração
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.7, 0.2)
        glPushMatrix()
        glTranslatef(0, -1, 0)
        glScalef(8, 0.02, 6)
        
        hs = 0.5
        glBegin(GL_QUADS)
        glVertex3f(-hs, hs, -hs)
        glVertex3f(-hs, hs, hs)
        glVertex3f(hs, hs, hs)
        glVertex3f(hs, hs, -hs)
        glEnd()
        glPopMatrix()
        
        glEnable(GL_LIGHTING)
        
        # Parede de demonstração
        Materials.apply_wall_material_varied(1, 1)
        glPushMatrix()
        glTranslatef(2, 0, 0)
        glScalef(1, 2, 1)
        Primitives.draw_unit_cube()
        glPopMatrix()
        
        # Caixa de demonstração
        glPushMatrix()
        glTranslatef(0, -0.5, 0)
        Materials.apply_box_material((0.72, 0.48, 0.16, 1.0), 32.0)
        Primitives.draw_unit_cube()
        glPopMatrix()
        
        # Objetivo de demonstração
        Primitives.draw_target_marker(-1, 0, 0)
    
    @staticmethod
    def render_menu(sound_manager=None) -> None:
        """
        Renderiza menu principal completo

        Args:
            sound_manager: Gerenciador de som (opcional)
        """
        Renderer.render_menu_background()
        UI.draw_menu(sound_manager)
    
    @staticmethod
    def render_victory(level, player, current_time: float) -> None:
        """
        Renderiza tela de vitória de nível.

        Args:
            level: Objeto Level com dados do nível
            player: Objeto Player com posição da câmera
            current_time: Tempo atual em segundos
        """
        # Renderiza cena de fundo
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Renderer.setup_camera(player)
        
        Primitives.draw_floor()
        
        for (x, y, z) in level.walls:
            Renderer.draw_wall(x, y, z)
        
        for (x, y, z) in level.objectives:
            Primitives.draw_target_marker(x, y, z)
        
        for (x, y, z) in level.boxes:
            Renderer.draw_box(x, y, z, 'on_target')
            Primitives.draw_shadow(x, y, z)
        
        Renderer.draw_particles(level.particles, current_time)
        
        # Overlay de vitória
        UI.draw_victory_screen(level.move_count)
    
    @staticmethod
    def render_final_victory() -> None:
        """Renderiza tela de vitória final (todos os níveis completos)"""
        UI.draw_final_victory_screen()
    
    @staticmethod
    def cleanup() -> None:
        """Limpa recursos de renderização (display lists, texturas, etc)"""
        Primitives.cleanup()
