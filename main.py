"""
main.py
=======
BoxPush 3D - Jogo Sokoban em 3D
Ponto de entrada principal do jogo.

ARQUITETURA DO PROJETO:
-----------------------
- main.py: Loop principal, gerenciamento de estados e eventos
- game/: Lógica do jogo (níveis, física, jogador)
- graphics/: Sistema de renderização 3D (OpenGL)
- utils/: Utilitários (sistema de som procedural)
- config.py: Constantes e configurações

PADRÕES DE PROJETO UTILIZADOS:
------------------------------
- MVC (Model-View-Controller): Separação entre lógica e renderização
- Singleton: Gerenciador de som com instância única
- State Pattern: Estados do jogo (menu, jogando, vitória)

TECNOLOGIAS:
-----------
- Pygame: Janela, eventos e áudio
- PyOpenGL: Renderização 3D com pipeline OpenGL
- NumPy: Geração procedural de sons

Controles:
- WASD: Movimento
- SHIFT: Correr
- Mouse: Olhar ao redor
- ESPAÇO: Empurrar caixas
- R: Reiniciar nível
- H: Toggle hints (mostrar/ocultar controles)
- P: Pause
- M: Toggle música
- N: Toggle sons
- F11: Fullscreen
- T: Teleporte de emergência
- ENTER: Avançar nível/Iniciar
- ESC: Sair/Menu
"""

import sys
import pygame
from pygame.locals import (
    QUIT, KEYDOWN, VIDEORESIZE, DOUBLEBUF, OPENGL, RESIZABLE,
    K_ESCAPE, K_r, K_t, K_m, K_n, K_h, K_RETURN, K_w, K_s, K_d, K_a,
    K_SPACE, K_LSHIFT, K_RSHIFT, K_F11, K_p
)
from OpenGL.GLUT import glutInit

# Importa módulos do jogo
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    MOUSE_SENSITIVITY, PUSH_COOLDOWN, TARGET_FPS, MAX_FRAME_TIME,
    GAME_STATE_MENU, GAME_STATE_PLAYING, GAME_STATE_WIN, GAME_STATE_FINAL_VICTORY,
    PARTICLE_LIFETIME
)
from graphics.renderer import Renderer
from game.player import Player
from game.level import Level
from game.levels_data import get_level_count
from utils.sound import get_sound_manager
from utils.logger import get_logger, cleanup_logging

# Logger
logger = get_logger(__name__)


class GameState:
    """Gerenciador de estados do jogo"""

    PAUSED = 99  # Estado de pausa

    def __init__(self):
        self.state = GAME_STATE_MENU
        self.last_push_time = 0.0
        self.victory_time = 0.0
        self.paused = False

    def is_menu(self):
        return self.state == GAME_STATE_MENU

    def is_playing(self):
        return self.state == GAME_STATE_PLAYING and not self.paused

    def is_paused(self):
        return self.paused

    def is_victory(self):
        return self.state == GAME_STATE_WIN

    def is_final_victory(self):
        return self.state == GAME_STATE_FINAL_VICTORY

    def set_menu(self):
        self.state = GAME_STATE_MENU
        self.paused = False

    def set_playing(self):
        self.state = GAME_STATE_PLAYING
        self.paused = False

    def toggle_pause(self):
        """Alterna estado de pausa (apenas durante jogo)"""
        if self.state == GAME_STATE_PLAYING:
            self.paused = not self.paused
            logger.info(f"Jogo {'pausado' if self.paused else 'despausado'}")
            return self.paused
        return False

    def set_victory(self, current_time):
        self.state = GAME_STATE_WIN
        self.victory_time = current_time
        self.paused = False

    def set_final_victory(self):
        self.state = GAME_STATE_FINAL_VICTORY
        self.paused = False


class Game:
    """Classe principal do jogo"""
    
    def __init__(self):
        """Inicializa o jogo"""
        logger.info("Inicializando BoxPush 3D...")

        # Inicializa Pygame
        pygame.init()
        glutInit(sys.argv)

        # Inicializa sistema de som
        self.sound = get_sound_manager()

        # Cria janela
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.fullscreen = False
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_mode(
            (self.window_width, self.window_height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )

        logger.info(f"Janela criada: {self.window_width}x{self.window_height}")

        # Inicializa OpenGL
        Renderer.init_opengl()
        Renderer.set_perspective(self.window_width, self.window_height)

        # Objetos do jogo
        self.player = Player()
        self.level = Level()
        self.game_state = GameState()

        # Clock para FPS
        self.clock = pygame.time.Clock()

        # Mouse
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

        # UI
        self.show_hints = True  # Toggle para mostrar/ocultar hints

        # Inicia música do menu
        self.sound.play_music('menu', is_menu=True)

        logger.info("Inicialização completa!")
    
    def toggle_fullscreen(self):
        """Alterna entre modo janela e fullscreen"""
        self.fullscreen = not self.fullscreen

        if self.fullscreen:
            # Pega resolução da tela antes de mudar para fullscreen
            info = pygame.display.Info()
            screen_w, screen_h = info.current_w, info.current_h
            pygame.display.set_mode((screen_w, screen_h), DOUBLEBUF | OPENGL | pygame.FULLSCREEN)
            logger.info(f"Modo fullscreen ativado: {screen_w}x{screen_h}")
            # Atualiza viewport com resolução fullscreen
            Renderer.set_perspective(screen_w, screen_h)
        else:
            pygame.display.set_mode(
                (self.window_width, self.window_height),
                DOUBLEBUF | OPENGL | RESIZABLE
            )
            logger.info(f"Modo janela ativado: {self.window_width}x{self.window_height}")
            # Restaura viewport para tamanho da janela
            Renderer.set_perspective(self.window_width, self.window_height)

    def _handle_global_keys(self, key):
        """Trata teclas globais (funcionam em qualquer estado)"""
        if key == K_ESCAPE:
            logger.info("ESC pressionado - saindo...")
            return False
        elif key == K_F11:
            self.toggle_fullscreen()
        elif key == K_m:
            self.sound.toggle_music()
        elif key == K_n:
            self.sound.toggle_sfx()
        elif key == K_h:
            # Toggle hints
            self.show_hints = not self.show_hints
            logger.info(f"Hints {'ativados' if self.show_hints else 'desativados'}")
        elif key == K_p and self.game_state.state == GAME_STATE_PLAYING:
            # Pause apenas durante jogo
            self.game_state.toggle_pause()
            if self.game_state.is_paused():
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
            else:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
        return True

    def _handle_playing_keys(self, key):
        """Trata teclas específicas do estado de jogo"""
        if key == K_r:
            # Reset nível
            logger.info("Reiniciando nível...")
            self.level.reload_current_level()
            self.player.set_position(*self.level.spawn_position)
            self.player.reset_camera()
            self.sound.play_music(self.level.current_level_index)
        elif key == K_t:
            # Teleporte de emergência
            logger.warning("Teleporte de emergência ativado")
            self.player.set_position(*self.level.spawn_position)
            self.player.reset_camera()

    def _handle_menu_enter(self):
        """Trata ENTER no menu - inicia jogo"""
        self.sound.play('menu_select')
        self.level.load_level(0)
        self.player.set_position(*self.level.spawn_position)
        self.player.reset_camera()
        self.game_state.set_playing()
        self.sound.play('level_start')
        self.sound.play_music(0)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(
            (self.window_width // 2, self.window_height // 2)
        )
        logger.info("Jogo iniciado - Nível 1")

    def _handle_victory_enter(self):
        """Trata ENTER na tela de vitória - próximo nível ou menu"""
        self.sound.play('menu_select')
        next_index = self.level.get_next_level_index()
        if next_index is not None:
            self.level.load_level(next_index)
            self.player.set_position(*self.level.spawn_position)
            self.player.reset_camera()
            self.game_state.set_playing()
            self.sound.play('level_start')
            self.sound.play_music(next_index)
            logger.info(f"Próximo nível: {next_index + 1}")
        else:
            self.game_state.set_menu()
            self.sound.stop_music()
            self.sound.play_music('menu', is_menu=True)
            logger.info("Voltando ao menu")

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(
            (self.window_width // 2, self.window_height // 2)
        )

    def _handle_final_victory_enter(self):
        """Trata ENTER na vitória final - volta ao menu"""
        self.game_state.set_menu()
        self.sound.stop_music()
        self.sound.play_music('menu', is_menu=True)
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        logger.info("Jogo completo! Voltando ao menu")

    def handle_events(self):
        """Processa eventos do Pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                logger.info("Evento QUIT recebido")
                return False

            elif event.type == KEYDOWN:
                # Trata teclas globais primeiro
                if not self._handle_global_keys(event.key):
                    return False

                # Teclas específicas do estado de jogo
                elif self.game_state.state == GAME_STATE_PLAYING and not self.game_state.is_paused():
                    self._handle_playing_keys(event.key)

                # ENTER: Controle de fluxo
                elif event.key == K_RETURN:
                    if self.game_state.is_menu():
                        self._handle_menu_enter()
                    elif self.game_state.is_victory():
                        self._handle_victory_enter()
                    elif self.game_state.is_final_victory():
                        self._handle_final_victory_enter()
            
            elif event.type == VIDEORESIZE:
                # Redimensionamento de janela
                self.window_width, self.window_height = event.size
                pygame.display.set_mode(
                    (self.window_width, self.window_height),
                    DOUBLEBUF | OPENGL | RESIZABLE
                )
                Renderer.set_perspective(self.window_width, self.window_height)
        
        return True
    
    def update_playing(self, dt, current_time):
        """Atualiza lógica durante o jogo"""
        # Mouse look
        mx, my = pygame.mouse.get_pos()
        dx = mx - (self.window_width // 2)
        dy = my - (self.window_height // 2)
        self.player.update_camera_rotation(dx, dy)
        pygame.mouse.set_pos((self.window_width // 2, self.window_height // 2))
        
        # Atualiza nuvens
        if self.level.clouds:
            self.level.clouds.update(dt)
        
        # Input de movimento
        keys = pygame.key.get_pressed()
        
        input_forward = 0.0
        input_strafe = 0.0
        
        if keys[K_w]:
            input_forward += 1.0
        if keys[K_s]:
            input_forward -= 1.0
        if keys[K_d]:
            input_strafe += 1.0
        if keys[K_a]:
            input_strafe -= 1.0
        
        # Movimento
        is_running = keys[K_LSHIFT] or keys[K_RSHIFT]
        self.player.move(
            input_forward, input_strafe, dt,
            self.level.walls, self.level.boxes,
            is_running, current_time
        )
        
        # Empurrar caixa
        if keys[K_SPACE]:
            if (current_time - self.game_state.last_push_time) >= PUSH_COOLDOWN:
                dir_x, dir_z = self.player.get_facing_direction()
                
                if self.level.push_box(
                    self.player.x, self.player.z,
                    dir_x, dir_z, current_time
                ):
                    self.game_state.last_push_time = current_time
                    
                    # Verifica vitória
                    if self.level.check_victory():
                        self.sound.play('victory')
                        if self.level.is_last_level():
                            self.game_state.set_final_victory()
                        else:
                            self.game_state.set_victory(current_time)
                        
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
        
        # Atualiza partículas
        self.level.update_particles(current_time, PARTICLE_LIFETIME)
    
    def render(self, current_time):
        """Renderiza frame atual"""
        # Garante que viewport está correto (fix para fullscreen/resize)
        surface = pygame.display.get_surface()
        current_w, current_h = surface.get_width(), surface.get_height()

        # Só atualiza se o tamanho mudou
        if current_w != self.window_width or current_h != self.window_height:
            self.window_width = current_w
            self.window_height = current_h
            Renderer.set_perspective(current_w, current_h)
            logger.info(f"Viewport atualizado: {current_w}x{current_h}")

        if self.game_state.is_menu():
            Renderer.render_menu(self.sound)

        elif self.game_state.is_playing():
            Renderer.render_game_scene(self.level, self.player, current_time, self.sound, self.show_hints)

        elif self.game_state.is_victory():
            Renderer.render_victory(self.level, self.player, current_time)

        elif self.game_state.is_final_victory():
            Renderer.render_final_victory()

        pygame.display.flip()
    
    def run(self):
        """Loop principal do jogo"""
        running = True
        
        while running:
            # Tempo
            dt_ms = self.clock.tick(TARGET_FPS)
            dt = min(dt_ms / 1000.0, MAX_FRAME_TIME)
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Eventos
            running = self.handle_events()
            
            # Atualização
            if self.game_state.is_playing():
                self.update_playing(dt, current_time)
            
            # Renderização
            self.render(current_time)
        
        # Limpeza
        logger.info("Encerrando jogo...")
        Renderer.cleanup()
        cleanup_logging()
        pygame.quit()
        logger.info("Jogo encerrado com sucesso")


def main():
    """Função principal"""
    print("=" * 60)
    print("🎮 BOXPUSH 3D - Sokoban Game")
    print("=" * 60)
    print(f"📦 {get_level_count()} níveis disponíveis")
    print("🎯 Empurre todas as caixas para os objetivos!")
    print()
    print("Controles:")
    print("  WASD      - Mover")
    print("  SHIFT     - Correr")
    print("  Mouse     - Olhar")
    print("  ESPAÇO    - Empurrar caixa")
    print("  R         - Reiniciar nível")
    print("  M         - Música ON/OFF")
    print("  N         - Sons ON/OFF")
    print("  ENTER     - Avançar/Iniciar")
    print("  ESC       - Sair")
    print("=" * 60)
    print()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
