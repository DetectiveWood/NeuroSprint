from typing import Callable, Any, List

class Signal:
    def __init__(self):
        self._callbacks: List[Callable] = []  # Список функций-обработчиков
        
    def connect(self, callback: Callable) -> None:
        """Подключить функцию к сигналу"""
        self._callbacks.append(callback)
        
    def disconnect(self, callback: Callable) -> None:
        """Отключить функцию от сигнала"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            
    def emit(self, *args: Any, **kwargs: Any) -> None:
        """Вызвать все подключенные функции с переданными аргументами"""
        for callback in self._callbacks:
            callback(*args, **kwargs)