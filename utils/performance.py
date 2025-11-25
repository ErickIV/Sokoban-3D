"""
utils/performance.py
====================
Sistema de métricas de performance e profiling.

Fornece ferramentas para monitorar performance do jogo, incluindo:
- FPS (Frames Per Second) médio e instantâneo
- Frame time (ms por frame)
- Histórico de performance
- Detecção de stuttering/lag spikes

USO:
----
```python
perf = get_performance_monitor()
perf.frame_start()  # Início do frame
# ... renderização ...
perf.frame_end()    # Fim do frame

stats = perf.get_stats()
print(f"FPS: {stats['fps']:.1f}")
```
"""

import time
from typing import Optional, List, Dict
from collections import deque
from config import FPS_AVERAGE_WINDOW
from utils.logger import get_logger


class PerformanceMonitor:
    """Monitor de performance do jogo"""

    def __init__(self, window_size: int = FPS_AVERAGE_WINDOW):
        """
        Inicializa monitor de performance.

        Args:
            window_size: Número de frames para calcular média (padrão: 60)
        """
        self.window_size = window_size
        self.logger = get_logger()

        # Histórico de frame times (em segundos)
        self.frame_times: deque = deque(maxlen=window_size)

        # Tempo do frame atual
        self.current_frame_start: Optional[float] = None
        self.last_frame_time: float = 0.0

        # Estatísticas acumuladas
        self.total_frames: int = 0
        self.total_time: float = 0.0

        # Detecção de lag spikes
        self.lag_spike_threshold: float = 0.05  # 50ms (abaixo de 20 FPS)
        self.lag_spike_count: int = 0

        # Timestamp de início
        self.start_time: float = time.perf_counter()

        self.logger.info(f"Monitor de performance inicializado (janela: {window_size} frames)")

    def frame_start(self) -> None:
        """
        Marca início de um frame.
        Deve ser chamado no início do loop de renderização.
        """
        self.current_frame_start = time.perf_counter()

    def frame_end(self) -> None:
        """
        Marca fim de um frame e calcula métricas.
        Deve ser chamado no final do loop de renderização.
        """
        if self.current_frame_start is None:
            self.logger.warning("frame_end() chamado sem frame_start() correspondente")
            return

        # Calcula tempo do frame
        frame_end_time = time.perf_counter()
        frame_time = frame_end_time - self.current_frame_start

        # Armazena no histórico
        self.frame_times.append(frame_time)
        self.last_frame_time = frame_time

        # Atualiza estatísticas
        self.total_frames += 1
        self.total_time += frame_time

        # Detecta lag spike
        if frame_time > self.lag_spike_threshold:
            self.lag_spike_count += 1
            self.logger.debug(
                f"Lag spike detectado: {frame_time*1000:.1f}ms "
                f"({1.0/frame_time:.1f} FPS)"
            )

        self.current_frame_start = None

    def get_fps(self) -> float:
        """
        Retorna FPS médio baseado na janela de frames recentes.

        Returns:
            FPS médio (frames por segundo)
        """
        if len(self.frame_times) == 0:
            return 0.0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0.0

    def get_instant_fps(self) -> float:
        """
        Retorna FPS instantâneo do último frame.

        Returns:
            FPS do último frame
        """
        if self.last_frame_time > 0:
            return 1.0 / self.last_frame_time
        return 0.0

    def get_frame_time_ms(self) -> float:
        """
        Retorna tempo médio por frame em milissegundos.

        Returns:
            Tempo médio em ms
        """
        if len(self.frame_times) == 0:
            return 0.0

        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return avg_frame_time * 1000.0

    def get_min_max_fps(self) -> tuple:
        """
        Retorna FPS mínimo e máximo da janela atual.

        Returns:
            Tupla (fps_min, fps_max)
        """
        if len(self.frame_times) == 0:
            return (0.0, 0.0)

        max_frame_time = max(self.frame_times)
        min_frame_time = min(self.frame_times)

        fps_min = 1.0 / max_frame_time if max_frame_time > 0 else 0.0
        fps_max = 1.0 / min_frame_time if min_frame_time > 0 else 0.0

        return (fps_min, fps_max)

    def get_percentile_fps(self, percentile: float) -> float:
        """
        Retorna FPS em um determinado percentil.

        Args:
            percentile: Percentil desejado (0.0-1.0)

        Returns:
            FPS no percentil especificado

        Exemplo:
            >>> perf.get_percentile_fps(0.01)  # 1% worst (1% low)
            >>> perf.get_percentile_fps(0.99)  # 99% best
        """
        if len(self.frame_times) == 0:
            return 0.0

        sorted_times = sorted(self.frame_times)
        index = int(len(sorted_times) * percentile)
        index = max(0, min(index, len(sorted_times) - 1))

        frame_time = sorted_times[index]
        return 1.0 / frame_time if frame_time > 0 else 0.0

    def get_stats(self) -> Dict[str, float]:
        """
        Retorna dicionário completo de estatísticas.

        Returns:
            Dicionário com todas as métricas disponíveis
        """
        fps_min, fps_max = self.get_min_max_fps()
        uptime = time.perf_counter() - self.start_time

        return {
            # FPS metrics
            'fps': self.get_fps(),
            'fps_instant': self.get_instant_fps(),
            'fps_min': fps_min,
            'fps_max': fps_max,
            'fps_1_percent_low': self.get_percentile_fps(0.01),
            'fps_99_percent': self.get_percentile_fps(0.99),

            # Frame time
            'frame_time_ms': self.get_frame_time_ms(),
            'last_frame_time_ms': self.last_frame_time * 1000.0,

            # Counters
            'total_frames': self.total_frames,
            'lag_spikes': self.lag_spike_count,

            # Time
            'uptime_seconds': uptime,
            'avg_fps_lifetime': self.total_frames / uptime if uptime > 0 else 0.0
        }

    def print_stats(self) -> None:
        """Imprime estatísticas formatadas no console"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("MÉTRICAS DE PERFORMANCE")
        print("="*60)
        print(f"FPS Médio:           {stats['fps']:.1f}")
        print(f"FPS Instantâneo:     {stats['fps_instant']:.1f}")
        print(f"FPS Mínimo:          {stats['fps_min']:.1f}")
        print(f"FPS Máximo:          {stats['fps_max']:.1f}")
        print(f"1% Low:              {stats['fps_1_percent_low']:.1f}")
        print(f"Frame Time (médio):  {stats['frame_time_ms']:.2f}ms")
        print(f"Frame Time (último): {stats['last_frame_time_ms']:.2f}ms")
        print(f"Total Frames:        {stats['total_frames']}")
        print(f"Lag Spikes:          {stats['lag_spikes']}")
        print(f"Uptime:              {stats['uptime_seconds']:.1f}s")
        print("="*60 + "\n")

    def reset(self) -> None:
        """Reseta todas as estatísticas"""
        self.frame_times.clear()
        self.total_frames = 0
        self.total_time = 0.0
        self.lag_spike_count = 0
        self.start_time = time.perf_counter()
        self.logger.info("Estatísticas de performance resetadas")

    def set_lag_spike_threshold(self, threshold_ms: float) -> None:
        """
        Define threshold para detecção de lag spikes.

        Args:
            threshold_ms: Tempo em milissegundos
        """
        self.lag_spike_threshold = threshold_ms / 1000.0
        self.logger.info(f"Threshold de lag spike: {threshold_ms}ms")

    def get_performance_grade(self) -> str:
        """
        Retorna uma nota de performance baseada no FPS médio.

        Returns:
            String com nota: 'Excelente', 'Bom', 'Razoável', 'Ruim'
        """
        fps = self.get_fps()

        if fps >= 90:
            return "Excelente"
        elif fps >= 60:
            return "Bom"
        elif fps >= 30:
            return "Razoável"
        else:
            return "Ruim"


# Instância global (singleton)
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Retorna instância singleton do monitor de performance.

    Returns:
        Instância do PerformanceMonitor
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor() -> None:
    """Reseta o monitor de performance global"""
    monitor = get_performance_monitor()
    monitor.reset()
