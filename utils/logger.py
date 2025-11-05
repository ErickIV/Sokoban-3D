"""
utils/logger.py
===============
Sistema de logging centralizado para o jogo.

Configura logging com múltiplos handlers:
- Console: INFO e acima
- Arquivo: DEBUG e acima
- Arquivo de erros: ERROR e acima

Uso:
    from utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("Jogo iniciado")
    logger.error("Erro ao carregar nível")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class GameLogger:
    """Gerenciador de logging do jogo (Singleton)"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Garante que existe apenas uma instância"""
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa o sistema de logging"""
        if GameLogger._initialized:
            return

        # Cria diretório de logs
        self.log_dir = Path.home() / '.boxpush' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Nomes dos arquivos de log
        timestamp = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f'boxpush_{timestamp}.log'
        self.error_file = self.log_dir / f'boxpush_errors_{timestamp}.log'

        # Configura logger raiz
        self.root_logger = logging.getLogger('boxpush')
        self.root_logger.setLevel(logging.DEBUG)

        # Remove handlers existentes
        self.root_logger.handlers.clear()

        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para console (INFO e acima)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.root_logger.addHandler(console_handler)

        # Handler para arquivo geral (DEBUG e acima)
        try:
            file_handler = logging.FileHandler(
                self.log_file, mode='a', encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Não foi possível criar arquivo de log: {e}")

        # Handler para arquivo de erros (ERROR e acima)
        try:
            error_handler = logging.FileHandler(
                self.error_file, mode='a', encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.root_logger.addHandler(error_handler)
        except Exception as e:
            print(f"⚠️ Não foi possível criar arquivo de erros: {e}")

        GameLogger._initialized = True
        self.root_logger.info("Sistema de logging inicializado")
        self.root_logger.debug(f"Logs salvos em: {self.log_dir}")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Retorna logger para um módulo específico.

        Args:
            name: Nome do módulo (geralmente __name__)

        Returns:
            Logger configurado
        """
        return logging.getLogger(f'boxpush.{name}')

    def cleanup(self):
        """Limpa handlers e fecha arquivos"""
        for handler in self.root_logger.handlers[:]:
            handler.close()
            self.root_logger.removeHandler(handler)


# Instância global
_game_logger = None


def get_logger(name: str = 'main') -> logging.Logger:
    """
    Retorna logger para uso em qualquer módulo.

    Args:
        name: Nome do módulo (use __name__ preferencialmente)

    Returns:
        Logger configurado

    Example:
        logger = get_logger(__name__)
        logger.info("Mensagem informativa")
        logger.error("Erro crítico")
    """
    global _game_logger
    if _game_logger is None:
        _game_logger = GameLogger()
    return _game_logger.get_logger(name)


def cleanup_logging():
    """Limpa sistema de logging ao fechar o jogo"""
    global _game_logger
    if _game_logger:
        _game_logger.cleanup()
