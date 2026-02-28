from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from UI.authForm import Ui_Dialog


class AuthDialog(QDialog):
    """Диалог аутентификации и регистрации"""
    account_created = Signal(dict)      # данные для создания аккаунта (регистрация)
    account_signed = Signal(dict)       # данные успешного входа (оставляем для совместимости)
    auth_success = Signal()             # успех (вход или регистрация)

    def __init__(self, parent=None):
        """
        check_credentials_callback: функция(username: str, password: str) -> (bool, str)
        Возвращает (успех, сообщение об ошибке или None)
        Если не передана — просто эмитит сигнал без проверки (как было раньше)
        """
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        self._user_data = {"username": "", "password": ""}
        self._current_mode = 0  # 0 = вход, 1 = регистрация
        
        self._setup_connections()
        self._clear_error_messages()

    def _setup_connections(self):
        # Переключение вкладок/режимов
        self.ui.pushButton.clicked.connect(lambda: self.switch_mode(1))     # → регистрация
        self.ui.pushButton_4.clicked.connect(lambda: self.switch_mode(0))   # → вход
        
        # Кнопки действий
        self.ui.pushButton_2.clicked.connect(self._handle_create_account)   # Зарегистрироваться
        self.ui.pushButton_3.clicked.connect(self._handle_sign_in)          # Войти

    def _clear_error_messages(self):
        self.ui.label_13.clear()
        self.ui.label_5.clear()

    def switch_mode(self, mode_index: int):
        self._current_mode = mode_index
        self.ui.stackedWidget.setCurrentIndex(mode_index)
        self._clear_error_messages()
        default_text = "Имя пользователя:"
        self.ui.label_13.setText(default_text)
        self.ui.label_5.setText(default_text)

    def _handle_create_account(self):
        username = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_3.text().strip()
        agreement = self.ui.checkBox.isChecked()

        if not self._validate_registration_data(username, password, agreement):
            return

        self._user_data.update({"username": username, "password": password})
        self.account_created.emit(self._user_data)
        self.auth_success.emit()
        self.accept()

    def _handle_sign_in(self):
        username = self.ui.lineEdit_5.text().strip()
        password = self.ui.lineEdit_6.text().strip()

        if not self._validate_login_data(username, password):
            return
        # Если проверки нет — просто пропускаем (как было раньше)

        self._user_data.update({"username": username, "password": password})
        self.account_signed.emit(self._user_data)       # сохраняем обратную совместимость
        self.auth_success.emit()
        self.accept()

    def _validate_registration_data(self, username: str, password: str, agreement: bool) -> bool:
        if not username:
            self.show_error(2, "Имя пользователя не может быть пустым")
            return False
        if not password:
            self.show_error(2, "Пароль не может быть пустым")
            return False
        if not agreement:
            self.show_error(2, "Необходимо принять условия")
            return False
        return True

    def _validate_login_data(self, username: str, password: str) -> bool:
        if not username:
            self.show_error(1, "Введите имя пользователя")
            return False
        if not password:
            self.show_error(1, "Введите пароль")
            return False
        return True

    def show_error(self, error_type: int, message: str):
        labels = {1: self.ui.label_13, 2: self.ui.label_5}
        label = labels.get(error_type)
        if label:
            label.setText(message)

    def closeEvent(self, event):
        self._clear_error_messages()
        super().closeEvent(event)