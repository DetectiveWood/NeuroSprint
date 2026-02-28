from PySide6.QtWidgets import QApplication
from window import MainWindow
from dataWorker import DatabaseWorker


class App:
    def __init__(self):
        self.app = QApplication.instance() or QApplication()
        self.win = MainWindow()
        self.data_worker = DatabaseWorker()
        
        # Настройка соединений между окном и базой данных
        self._setup_connections()
        
        # Запуск рабочего потока базы данных
        self.data_worker.start()
    
    def _setup_connections(self):
        """Настройка всех соединений между компонентами"""
        auth_dialog = self.win.get_auth_dialog()
        
        # Соединения для регистрации
        auth_dialog.account_created.connect(self.data_worker.handle_create_user)
        self.data_worker.user_created.connect(self._on_user_creation_result)
        
        # Соединения для входа
        auth_dialog.account_signed.connect(self.data_worker.handle_find_user)
        self.data_worker.user_authenticated.connect(self._on_user_authentication_result)
        
        # Соединение для передачи найденного пользователя
        self.data_worker.user_found.connect(self._on_user_found)
    
    def _on_user_creation_result(self, success: bool, error_msg: str):
        """
        Обработка результата создания пользователя
        
        Args:
            success: True если создание успешно
            error_msg: сообщение об ошибке если success=False
        """
        auth_dialog = self.win.get_auth_dialog()
        
        if success:
            # При успешной регистрации автоматически выполняем вход
            username = auth_dialog.ui.lineEdit.text().strip()
            password = auth_dialog.ui.lineEdit_3.text().strip()
            user_data = {"username": username, "password": password}
            auth_dialog.account_signed.emit(user_data)
        else:
            # Показываем ошибку и НЕ закрываем диалог
            auth_dialog.show_error(2, error_msg)
    
    def _on_user_authentication_result(self, success: bool, error_msg: str):
        """
        Обработка результата аутентификации пользователя
        
        Args:
            success: True если пользователь найден и пароль верен
            error_msg: сообщение об ошибке если success=False
        """
        auth_dialog = self.win.get_auth_dialog()
        
        if success:
            # При успешном входе диалог закроется автоматически
            # после получения данных пользователя
            pass
        else:
            # Показываем ошибку и НЕ закрываем диалог
            auth_dialog.show_error(1, error_msg)
    
    def _on_user_found(self, user):
        """
        Обработка получения данных найденного пользователя
        
        Args:
            user: объект User или None
        """
        if user:
            # Сохраняем пользователя и закрываем диалог (только при успехе)
            self.win.set_current_user(user)
            # Закрываем диалог аутентификации
            self.win.get_auth_dialog().accept()
    
    def show_window(self):
        """Показать главное окно"""
        self.win.show()
    
    def run(self):
        """Запустить приложение"""
        self.show_window()
        return self.app.exec()
    
    def cleanup(self):
        """Очистка ресурсов при завершении"""
        if hasattr(self, 'data_worker'):
            self.data_worker.stop()
            self.data_worker.wait()


if __name__ == "__main__":
    app = App()
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    exit(exit_code)