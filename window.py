from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Signal, QDate
from UI.mainUI import Ui_MainWindow
from authDialog import AuthDialog
from dataWorker import User

class MainWindow(QMainWindow):
    """Главное окно приложения"""
   
    # Сигнал для уведомления об успешной аутентификации
    user_authenticated = Signal(object)  # передает объект User
   
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
       
        # Текущий пользователь
        self.current_user = None
       
        # Создание диалога аутентификации
        self._auth_dialog = AuthDialog(self)
       
        self._setup_connections()
   
    def _setup_connections(self):
        """Настройка соединений"""
        # Кнопки открытия диалогов
        self.ui.pushButton_2.clicked.connect(lambda: self._show_auth_dialog(0))
        self.ui.pushButton_4.clicked.connect(lambda: self._show_auth_dialog(1))
       
        # Сигнал успешной аутентификации из диалога
        self._auth_dialog.auth_success.connect(self._on_auth_success)
   
    def _show_auth_dialog(self, mode_index: int):
        """
        Показать диалог аутентификации в указанном режиме
        
        Args:
            mode_index: 0 - вход, 1 - регистрация
        """
        self._auth_dialog.switch_mode(mode_index)
        self._auth_dialog.exec()
   
    def get_auth_dialog(self):
        """Получить ссылку на диалог аутентификации"""
        return self._auth_dialog
   
    def set_current_user(self, user: User):
        """
        Установить текущего пользователя
        
        Args:
            user: объект пользователя
        """
        self.current_user = user
        self.user_authenticated.emit(user)
       
        # Обновляем интерфейс с информацией о пользователе
        self._update_ui_for_user()
   
    def _update_ui_for_user(self):
        """Обновление интерфейса после входа пользователя"""
        if not self.current_user:
            return
            
        # Имя пользователя в label_13
        self.ui.label_13.setText(self.current_user.username)
        
        # Текущая дата в label_17 (красивый русский формат)
        today = QDate.currentDate()
        self.ui.label_17.setText(today.toString("dd MMMM yyyy"))
        # Альтернативы, если нужен другой стиль:
        # self.ui.label_17.setText(today.toString("dd.MM.yyyy"))
        # self.ui.label_17.setText(today.toString("d MMMM yyyy 'г.'"))
   
    def _on_auth_success(self):
        """Действия при успешной аутентификации"""
        if not self.current_user:
            # QMessageBox.warning(self, "Ошибка", "Пользователь не установлен")
            return
            
        # QMessageBox.information(
        #     self,
        #     "Успех",
        #     f"Добро пожаловать, {self.current_user.username}!"
        # )
        
        # Переключаем на основную страницу
        self.ui.stackedWidget.setCurrentIndex(1)
        
        # Обновляем метки (имя + дата)
        self._update_ui_for_user()
   
    def closeEvent(self, event):
        """Обработка закрытия главного окна"""
        # Здесь можно сохранить данные сессии и т.д.
        super().closeEvent(event)