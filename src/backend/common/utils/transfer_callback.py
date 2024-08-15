import threading
from datetime import timedelta
from time import monotonic

import structlog


class TransferCallback:
    """
    Обработка обратных вызовов от менеджера передачи.

    Менеджер передачи периодически вызывает метод __call__ на протяжении всего процесса
    в процессе загрузки и выгрузки, чтобы он мог предпринять какие-либо действия, например
    отображение прогресса для пользователя и сбор данных о передаче.
    """

    def __init__(self, target_size):
        self._target_size = target_size
        self._total_transferred = 0
        self._lock = threading.Lock()
        self._thread_info = {}
        self._transfered_percent_step = 5
        self._transfered_percent_tick = self._transfered_percent_step
        self._logger = structlog.get_logger("storage")
        self._transfered_percent = 0
        self._start_time = 0

    def __call__(self, bytes_transferred):
        """
        Метод обратного вызова, вызываемый менеджером передачи.

        Отображение прогресса во время передачи файлов и сбор данных о передаче для каждого потока
        данные. Этот метод может вызываться несколькими потоками, поэтому общие данные экземпляра
        защищены блокировкой потока.
        """
        thread = threading.current_thread()
        with self._lock:
            if not self._total_transferred:
                self._start_time = monotonic()
            self._total_transferred += bytes_transferred
            self._thread_info[thread.ident] = self._thread_info.get(thread.ident, 0) + bytes_transferred

            self._transfered_percent = (self._total_transferred / self._target_size) * 100
            if self._transfered_percent >= self._transfered_percent_tick:
                self._transfered_percent_tick += self._transfered_percent_step
                self._logger.debug(
                    f"{self._total_transferred} of {self._target_size} transferred "
                    f"({self._transfered_percent:.2f}%). "
                    f"Time passed: {timedelta(seconds=monotonic() - self._start_time)}"
                )

    def get_status(self):
        with self._lock:
            return {"percent": self._transfered_percent, "time": monotonic() - self._start_time}
