"""
graphics/gl_utils.py
====================
Utilitários OpenGL para verificação de erros e debugging.

Este módulo fornece wrappers e ferramentas para facilitar o desenvolvimento
e debugging de código OpenGL, incluindo verificação automática de erros.

FUNÇÕES PRINCIPAIS:
------------------
- check_gl_error(): Verifica erros OpenGL e loga se encontrado
- gl_debug_callback(): Callback para debugging no OpenGL 4.3+
- safe_gl_enable(): Wrapper seguro para glEnable com verificação de erros

USO RECOMENDADO:
---------------
Em desenvolvimento: Ative verificação de erros após operações críticas
Em produção: Desative para melhor performance
"""

from typing import Optional
from OpenGL.GL import (
    glGetError, glEnable, glDisable,
    GL_NO_ERROR, GL_INVALID_ENUM, GL_INVALID_VALUE,
    GL_INVALID_OPERATION, GL_STACK_OVERFLOW, GL_STACK_UNDERFLOW,
    GL_OUT_OF_MEMORY
)
from utils.logger import get_logger


# Mapeamento de códigos de erro para mensagens legíveis
GL_ERROR_MESSAGES = {
    GL_INVALID_ENUM: "GL_INVALID_ENUM - Valor de enumeração inaceitável",
    GL_INVALID_VALUE: "GL_INVALID_VALUE - Valor numérico fora do intervalo",
    GL_INVALID_OPERATION: "GL_INVALID_OPERATION - Operação não permitida no estado atual",
    GL_STACK_OVERFLOW: "GL_STACK_OVERFLOW - Estouro de pilha",
    GL_STACK_UNDERFLOW: "GL_STACK_UNDERFLOW - Pilha vazia ao tentar pop",
    GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY - Memória insuficiente"
}


class GLDebugger:
    """Gerenciador de debugging OpenGL"""

    def __init__(self, enabled: bool = True):
        """
        Inicializa debugger OpenGL.

        Args:
            enabled: Se verificação de erros está habilitada (padrão: True)
        """
        self.enabled = enabled
        self.logger = get_logger()
        self.error_count = 0

    def check_error(self, context: str = "") -> bool:
        """
        Verifica se há erros OpenGL pendentes.

        Args:
            context: Descrição do contexto onde a verificação ocorre

        Returns:
            True se encontrou erro, False caso contrário
        """
        if not self.enabled:
            return False

        error = glGetError()
        if error != GL_NO_ERROR:
            self.error_count += 1
            error_msg = GL_ERROR_MESSAGES.get(error, f"Erro desconhecido: {error}")

            if context:
                self.logger.error(f"Erro OpenGL em '{context}': {error_msg}")
            else:
                self.logger.error(f"Erro OpenGL: {error_msg}")

            return True

        return False

    def safe_enable(self, capability: int, context: str = "") -> bool:
        """
        Habilita uma capacidade OpenGL com verificação de erros.

        Args:
            capability: Constante GL da capacidade a habilitar
            context: Descrição do contexto (opcional)

        Returns:
            True se operação bem-sucedida, False se houve erro
        """
        try:
            glEnable(capability)
            if self.check_error(f"glEnable({context if context else capability})"):
                return False
            return True
        except Exception as e:
            self.logger.error(f"Exceção ao habilitar {context}: {e}")
            return False

    def safe_disable(self, capability: int, context: str = "") -> bool:
        """
        Desabilita uma capacidade OpenGL com verificação de erros.

        Args:
            capability: Constante GL da capacidade a desabilitar
            context: Descrição do contexto (opcional)

        Returns:
            True se operação bem-sucedida, False se houve erro
        """
        try:
            glDisable(capability)
            if self.check_error(f"glDisable({context if context else capability})"):
                return False
            return True
        except Exception as e:
            self.logger.error(f"Exceção ao desabilitar {context}: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Retorna estatísticas de erros.

        Returns:
            Dicionário com contadores de erros
        """
        return {
            'total_errors': self.error_count,
            'enabled': self.enabled
        }

    def reset_stats(self) -> None:
        """Reseta contadores de estatísticas"""
        self.error_count = 0

    def set_enabled(self, enabled: bool) -> None:
        """
        Habilita/desabilita verificação de erros.

        Args:
            enabled: True para habilitar, False para desabilitar
        """
        self.enabled = enabled
        if enabled:
            self.logger.info("Verificação de erros OpenGL habilitada")
        else:
            self.logger.info("Verificação de erros OpenGL desabilitada (modo performance)")


# Instância global do debugger (singleton pattern)
_gl_debugger: Optional[GLDebugger] = None


def get_gl_debugger() -> GLDebugger:
    """
    Retorna instância singleton do debugger OpenGL.

    Returns:
        Instância do GLDebugger
    """
    global _gl_debugger
    if _gl_debugger is None:
        _gl_debugger = GLDebugger(enabled=True)
    return _gl_debugger


def check_gl_error(context: str = "") -> bool:
    """
    Função de conveniência para verificar erros OpenGL.

    Args:
        context: Descrição do contexto onde a verificação ocorre

    Returns:
        True se encontrou erro, False caso contrário

    Exemplo:
        >>> glEnable(GL_DEPTH_TEST)
        >>> check_gl_error("Habilitando depth test")
    """
    return get_gl_debugger().check_error(context)


def safe_gl_enable(capability: int, context: str = "") -> bool:
    """
    Wrapper seguro para glEnable com verificação de erros.

    Args:
        capability: Constante GL da capacidade
        context: Descrição opcional do contexto

    Returns:
        True se sucesso, False se erro

    Exemplo:
        >>> safe_gl_enable(GL_DEPTH_TEST, "Depth testing")
    """
    return get_gl_debugger().safe_enable(capability, context)


def safe_gl_disable(capability: int, context: str = "") -> bool:
    """
    Wrapper seguro para glDisable com verificação de erros.

    Args:
        capability: Constante GL da capacidade
        context: Descrição opcional do contexto

    Returns:
        True se sucesso, False se erro

    Exemplo:
        >>> safe_gl_disable(GL_LIGHTING, "Desabilitando iluminação para HUD")
    """
    return get_gl_debugger().safe_disable(capability, context)


def set_gl_debug_enabled(enabled: bool) -> None:
    """
    Habilita/desabilita verificação de erros OpenGL globalmente.

    Args:
        enabled: True para habilitar, False para desabilitar

    Nota:
        Desabilitar em produção pode melhorar performance
    """
    get_gl_debugger().set_enabled(enabled)


def get_gl_debug_stats() -> dict:
    """
    Retorna estatísticas de debugging OpenGL.

    Returns:
        Dicionário com informações de erros
    """
    return get_gl_debugger().get_stats()
