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
- ESPAÇO: Empurrar caixa
- R: Reiniciar nível
- M: Música ON/OFF
- N: Sons ON/OFF
- T: Teleporte de emergência
- ESC: Sair/Menu
- ENTER: Avançar nível/Iniciar
"""

import sys
import pygame
from pygame.locals import *
from OpenGL.GLUT import glutInit

# Importa módulos do jogo
from config import *
from graphics.renderer import Renderer
from graphics.ui import UI
from game.player import Player
from game.level import Level
from game.levels_data import get_level_count
from utils.sound import get_sound_manager


class GameState:
    """Gerenciador de estados do jogo"""
    
    def __init__(self):
        self.state = GAME_STATE_MENU
        self.previous_state = GAME_STATE_MENU  # Para voltar das configurações
        self.last_push_time = 0.0
        self.victory_time = 0.0
        self.settings_option = 0  # 0: Music, 1: SFX, 2: Sensitivity
    
    def is_menu(self):
        return self.state == GAME_STATE_MENU
    
    def is_playing(self):
        return self.state == GAME_STATE_PLAYING
    
    def is_paused(self):
        return self.state == GAME_STATE_PAUSED
    
    def is_victory(self):
        return self.state == GAME_STATE_WIN
    
    def is_final_victory(self):
        return self.state == GAME_STATE_FINAL_VICTORY

    def is_settings(self):
        return self.state == GAME_STATE_SETTINGS
    
    def set_menu(self):
        self.state = GAME_STATE_MENU
    
    def set_playing(self):
        self.state = GAME_STATE_PLAYING
    
    def set_paused(self):
        self.state = GAME_STATE_PAUSED
    
    def set_victory(self, current_time):
        self.state = GAME_STATE_WIN
        self.victory_time = current_time
    
    def set_final_victory(self):
        self.state = GAME_STATE_FINAL_VICTORY

    def set_settings(self):
        # Salva estado anterior se não estiver já em settings
        if self.state != GAME_STATE_SETTINGS:
            self.previous_state = self.state
        self.state = GAME_STATE_SETTINGS
    
    def restore_previous_state(self):
        """Volta para o estado anterior (usado ao sair de settings)"""
        self.state = self.previous_state


class Game:
    """Classe principal do jogo"""
    
    def __init__(self):
        """Inicializa o jogo"""
        # Inicializa Pygame
        pygame.init()
        glutInit(sys.argv)
        
        # Inicializa sistema de som
        self.sound = get_sound_manager()
        
        # Cria janela
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        pygame.display.set_caption(WINDOW_TITLE)
        pygame.display.set_mode(
            (self.window_width, self.window_height),
            DOUBLEBUF | OPENGL | RESIZABLE
        )
        
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
        
        # Inicia música do menu
        self.sound.play_music('menu', is_menu=True)

    def start_game(self):
        """Inicia uma nova partida"""
        self.level.load_level(0)
        self.player.set_position(*self.level.spawn_position)
        self.player.reset_camera()
        self.game_state.set_playing()
        self.sound.play('level_start')
        self.sound.play_music(0)  # Música da fase 1
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        pygame.mouse.set_pos(
            (self.window_width // 2, self.window_height // 2)
        )
    
    def handle_events(self):
        """Processa eventos do Pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                # ESC sempre sai
                if event.key == K_ESCAPE:
                    if self.game_state.is_settings():
                        self.game_state.restore_previous_state()
                        self.sound.play('menu_select')
                    elif self.game_state.is_menu():
                        return False
                    else:
                        self.game_state.set_menu()
                        self.sound.stop_music()
                        self.sound.play_music('menu', is_menu=True)
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                
                # R: Reset nível (apenas durante jogo)
                elif event.key == K_r and self.game_state.is_playing():
                    self.level.reload_current_level()
                    self.player.set_position(*self.level.spawn_position)
                    self.player.reset_camera()
                    self.sound.play_music(self.level.current_level_index)
                
                # T: Teleporte de emergência
                elif event.key == K_t and self.game_state.is_playing():
                    self.player.set_position(*self.level.spawn_position)
                    self.player.reset_camera()
                
                # M: Toggle música
                elif event.key == K_m:
                    self.sound.toggle_music()
                
                # N: Toggle sons
                elif event.key == K_n:
                    self.sound.toggle_sfx()
                
                # O: Abrir configurações
                elif event.key == K_o and self.game_state.is_menu():
                    self.game_state.set_settings()
                
                # Navegação Menu Configurações (Teclado)
                elif self.game_state.is_settings():
                    if event.key == K_UP:
                        self.game_state.settings_option = (self.game_state.settings_option - 1) % 3
                        self.sound.play('menu_select')
                    elif event.key == K_DOWN:
                        self.game_state.settings_option = (self.game_state.settings_option + 1) % 3
                        self.sound.play('menu_select')
                    elif event.key == K_LEFT or event.key == K_RIGHT:
                        direction = -1 if event.key == K_LEFT else 1
                        if self.game_state.settings_option == 0:
                            new_vol = max(0.0, min(1.0, self.sound.current_music_volume + direction * 0.1))
                            self.sound.set_music_volume(new_vol)
                        elif self.game_state.settings_option == 1:
                            new_vol = max(0.0, min(1.0, self.sound.sfx_volume + direction * 0.1))
                            self.sound.set_sfx_volume(new_vol)
                            self.sound.play('menu_select')
                        elif self.game_state.settings_option == 2:
                            import config
                            new_sens = max(0.01, min(0.5, config.MOUSE_SENSITIVITY + direction * 0.01))
                            config.MOUSE_SENSITIVITY = new_sens
                            self.player.set_sensitivity(new_sens)

                # P: Pause/Unpause
                elif event.key == K_p:
                    if self.game_state.is_playing():
                        self.game_state.set_paused()
                        self.sound.stop_music() # Opcional: pausar música ou diminuir volume
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)
                    elif self.game_state.is_paused():
                        self.game_state.set_playing()
                        self.sound.play_music(self.level.current_level_index) # Retoma música
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos((self.window_width // 2, self.window_height // 2))

                # ENTER: Controle de fluxo
                if event.key == K_RETURN:
                    self.sound.play('menu_select')
                    if self.game_state.is_menu():
                        self.start_game()
                    
                    elif self.game_state.is_victory():
                        next_index = self.level.get_next_level_index()
                        if next_index is not None:
                            self.level.load_level(next_index)
                            self.player.set_position(*self.level.spawn_position)
                            self.player.reset_camera()
                            self.game_state.set_playing()
                            self.sound.play('level_start')
                            self.sound.play_music(next_index)
                        else:
                            self.game_state.set_menu()
                            self.sound.stop_music()
                            self.sound.play_music('menu', is_menu=True)
                        
                        pygame.event.set_grab(True)
                        pygame.mouse.set_visible(False)
                        pygame.mouse.set_pos(
                            (self.window_width // 2, self.window_height // 2)
                        )
                    
                    elif self.game_state.is_final_victory():
                        self.game_state.set_menu()
                        self.sound.stop_music()
                        self.sound.play_music('menu', is_menu=True)
                        pygame.event.set_grab(False)
                        pygame.mouse.set_visible(True)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    gl_my = self.window_height - my
                    
                    if self.game_state.is_menu():
                        action = UI.get_menu_action(mx, gl_my)
                        if action == 'start':
                            self.sound.play('menu_select')
                            self.start_game()
                        elif action == 'continue':
                            self.sound.play('menu_select')
                            if not self.load_game():
                                # Se falhar (ex: sem save), inicia novo jogo ou dá feedback
                                # Por enquanto, inicia novo jogo
                                self.start_game()
                        elif action == 'settings':
                            self.sound.play('menu_select')
                            self.game_state.set_settings()
                        elif action == 'quit':
                            return False
                            
                    elif self.game_state.is_settings():
                        action, data = UI.get_settings_action(mx, gl_my)
                        if action == 'slider_drag':
                            s_id, val = data
                            self._update_setting(s_id, val)
                        elif action == 'back':
                            self.game_state.restore_previous_state()
                            self.sound.play('menu_select')
                    
                    elif self.game_state.is_paused():
                        action = UI.get_pause_action(mx, gl_my)
                        if action == 'resume':
                            self.sound.play('menu_select')
                            self.game_state.set_playing()
                            self.sound.play_music(self.level.current_level_index)
                            pygame.event.set_grab(True)
                            pygame.mouse.set_visible(False)
                            pygame.mouse.set_pos((self.window_width // 2, self.window_height // 2))
                        elif action == 'save':
                            self.save_game()
                        elif action == 'settings':
                            self.sound.play('menu_select')
                            self.game_state.set_settings()
                        elif action == 'main_menu':
                            self.sound.play('menu_select')
                            self.game_state.set_menu()
                            self.sound.play_music('menu', is_menu=True)

            elif event.type == MOUSEMOTION:
                if pygame.mouse.get_pressed()[0] and self.game_state.is_settings():
                    mx, my = pygame.mouse.get_pos()
                    gl_my = self.window_height - my
                    action, data = UI.get_settings_action(mx, gl_my)
                    if action == 'slider_drag':
                        s_id, val = data
                        self._update_setting(s_id, val)
            
            elif event.type == VIDEORESIZE:
                self.window_width, self.window_height = event.size
                pygame.display.set_mode(
                    (self.window_width, self.window_height),
                    DOUBLEBUF | OPENGL | RESIZABLE
                )
                Renderer.set_perspective(self.window_width, self.window_height)
        
        return True

    def _update_setting(self, s_id, val):
        """Helper para atualizar configurações"""
        if s_id == 0: # Music
            self.sound.set_music_volume(val)
            self.game_state.settings_option = 0
        elif s_id == 1: # SFX
            self.sound.set_sfx_volume(val)
            self.game_state.settings_option = 1
        elif s_id == 2: # Sensitivity
            import config
            real_sens = 0.01 + val * (0.5 - 0.01)
            config.MOUSE_SENSITIVITY = real_sens
            self.player.set_sensitivity(real_sens)
            self.game_state.settings_option = 2

            

    
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
        if self.game_state.is_menu():
            Renderer.render_menu(self.sound, pygame.mouse.get_pos())
        
        elif self.game_state.is_paused():
            # Renderiza o jogo ao fundo (congelado)
            Renderer.render_game_scene(self.level, self.player, current_time, self.sound)
            # Renderiza menu de pause por cima
            UI.draw_pause_menu(pygame.mouse.get_pos())

        elif self.game_state.is_playing():
            Renderer.render_game_scene(self.level, self.player, current_time, self.sound)
        
        elif self.game_state.is_victory():
            Renderer.render_victory(self.level, self.player, current_time)
        
        elif self.game_state.is_final_victory():
            Renderer.render_final_victory()
        
        elif self.game_state.is_settings():
            import config
            Renderer.render_settings(
                self.game_state.settings_option,
                self.sound.current_music_volume,
                self.sound.sfx_volume,
                config.MOUSE_SENSITIVITY,
                pygame.mouse.get_pos()
            )
        
        pygame.display.flip()
    
    def save_game(self):
        """Salva o progresso do jogo"""
        import json
        import os
        
        data = {
            "level": self.level.current_level_index,
            "stats": self.level.get_progress_stats()
        }
        
        try:
            save_dir = os.path.expanduser("~/.boxpush")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            with open(os.path.join(save_dir, "savegame.json"), "w") as f:
                json.dump(data, f)
            print("Jogo salvo com sucesso!")
            self.sound.play('menu_select') # Feedback sonoro
        except Exception as e:
            print(f"Erro ao salvar jogo: {e}")

    def load_game(self):
        """Carrega o progresso do jogo"""
        import json
        import os
        
        try:
            save_path = os.path.expanduser("~/.boxpush/savegame.json")
            if not os.path.exists(save_path):
                print("Nenhum save encontrado.")
                return False
                
            with open(save_path, "r") as f:
                data = json.load(f)
            
            level_index = data.get("level", 0)
            
            # Carrega nível
            if self.level.load_level(level_index):
                self.player.set_position(*self.level.spawn_position)
                self.player.reset_camera()
                self.game_state.set_playing()
                self.sound.play('level_start')
                self.sound.play_music(level_index)
                
                # Restaura stats (opcional, se quiser manter contagem total)
                # self.level.move_count = data.get("stats", {}).get("move_count", 0)
                
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                pygame.mouse.set_pos(
                    (self.window_width // 2, self.window_height // 2)
                )
                print(f"Jogo carregado: Nível {level_index}")
                return True
            else:
                print("Erro ao carregar nível do save.")
                return False
                
        except Exception as e:
            print(f"Erro ao carregar jogo: {e}")
            return False

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
        Renderer.cleanup()
        pygame.quit()


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
    print("  O         - Configurações")
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
