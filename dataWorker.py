from PySide6.QtCore import QThread, Signal
import sqlite3
import hashlib
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class UserOperationStatus(Enum):
    SUCCESS = "success"
    USER_EXISTS = "user_exists"
    USER_NOT_FOUND = "user_not_found"
    INVALID_PASSWORD = "invalid_password"
    DATABASE_ERROR = "database_error"


@dataclass
class User:
    id: int
    username: str
    # password не храним в объекте User для безопасности


class DatabaseWorker(QThread):
    """Работник для асинхронной работы с базой данных"""
    
    # Сигналы для операций с пользователями
    user_created = Signal(bool, str)  # (успех, сообщение об ошибке)
    user_authenticated = Signal(bool, str)  # (успех, сообщение об ошибке)
    user_found = Signal(object)  # передает объект User или None
    
    # Сигналы для запросов
    create_user_requested = Signal(dict)
    find_user_requested = Signal(dict)
    
    DB_NAME = 'reaction_trainer.db'

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True
        self._setup_database()

    def _hash_password(self, password: str) -> str:
        """
        Создает хэш пароля с солью
        
        Args:
            password: пароль в открытом виде
            
        Returns:
            строка вида: salt$hash
        """
        # Генерируем случайную соль
        salt = os.urandom(32).hex()
        # Создаем хэш пароля с солью
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # количество итераций
        ).hex()
        return f"{salt}${password_hash}"

    def _verify_password(self, stored_password: str, provided_password: str) -> bool:
        """
        Проверяет соответствие пароля сохраненному хэшу
        
        Args:
            stored_password: сохраненная строка вида salt$hash
            provided_password: проверяемый пароль в открытом виде
            
        Returns:
            True если пароль верен
        """
        try:
            salt, stored_hash = stored_password.split('$')
            # Вычисляем хэш для предоставленного пароля с той же солью
            provided_hash = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return provided_hash == stored_hash
        except Exception as e:
            print(f"❌ Ошибка при проверке пароля: {e}")
            return False

    def _setup_database(self):
        """Инициализация структуры базы данных"""
        with sqlite3.connect(self.DB_NAME) as conn:
            cursor = conn.cursor()

            # Таблица пользователей - поле password остается, но храним хэш
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )''')

            # Таблица сессий
            cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                avg_rt REAL,
                misses INTEGER,
                false_alarms INTEGER,
                variability REAL,
                accuracy REAL,
                correct_rts TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')
            
            conn.commit()
            print("База данных инициализирована")

    # === Публичные методы для создания пользователя ===
    
    def create_user(self, username: str, password: str) -> UserOperationStatus:
        """
        Создает нового пользователя в базе данных
        
        Args:
            username: имя пользователя
            password: пароль
            
        Returns:
            статус операции
        """
        try:
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor = conn.cursor()
                
                # Проверяем существование пользователя
                if self._user_exists(cursor, username):
                    return UserOperationStatus.USER_EXISTS
                
                # Хэшируем пароль
                password_hash = self._hash_password(password)
                
                # Создаем нового пользователя
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                
                user_id = cursor.lastrowid
                print(f"✅ Создан новый пользователь: {username} (ID: {user_id})")
                return UserOperationStatus.SUCCESS
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка базы данных при создании пользователя: {e}")
            return UserOperationStatus.DATABASE_ERROR

    def find_user(self, username: str, password: str) -> tuple[UserOperationStatus, Optional[User]]:
        """
        Находит пользователя по имени и проверяет пароль
        
        Args:
            username: имя пользователя для поиска
            password: пароль для проверки
            
        Returns:
            кортеж (статус, объект пользователя или None)
        """
        try:
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor = conn.cursor()
                
                # Получаем информацию о пользователе
                cursor.execute(
                    "SELECT id, username, password FROM users WHERE username = ?", 
                    (username,)
                )
                row = cursor.fetchone()
                
                if not row:
                    print(f"❌ Пользователь не найден: {username}")
                    return UserOperationStatus.USER_NOT_FOUND, None
                
                user_id, db_username, password_hash = row
                
                # Проверяем пароль
                if not self._verify_password(password_hash, password):
                    print(f"❌ Неверный пароль для пользователя: {username}")
                    return UserOperationStatus.INVALID_PASSWORD, None
                
                # Создаем объект пользователя (без пароля)
                user = User(id=user_id, username=db_username)
                print(f"✅ Найден пользователь: {username}")
                return UserOperationStatus.SUCCESS, user
                    
        except sqlite3.Error as e:
            print(f"❌ Ошибка базы данных при поиске пользователя: {e}")
            return UserOperationStatus.DATABASE_ERROR, None

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Проверяет существование пользователя и соответствие пароля
        
        Args:
            username: имя пользователя
            password: пароль для проверки
            
        Returns:
            True если пользователь существует и пароль верен, иначе False
        """
        try:
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT password FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                
                if not row:
                    print(f"❌ Пользователь не найден: {username}")
                    return False
                
                password_hash = row[0]
                is_valid = self._verify_password(password_hash, password)
                
                if is_valid:
                    print(f"✅ Аутентификация успешна для: {username}")
                else:
                    print(f"❌ Неверный пароль для: {username}")
                    
                return is_valid
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка при аутентификации: {e}")
            return False

    def get_user_id(self, username: str) -> Optional[int]:
        """
        Получает ID пользователя по имени
        
        Args:
            username: имя пользователя
            
        Returns:
            ID пользователя или None если не найден
        """
        try:
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM users WHERE username = ?", 
                    (username,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении ID пользователя: {e}")
            return None

    # === Приватные вспомогательные методы ===
    
    def _user_exists(self, cursor, username: str) -> bool:
        """Проверяет существование пользователя (внутренний метод)"""
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ?", 
            (username,)
        )
        return cursor.fetchone() is not None

    # === Обработчики сигналов ===
    
    def handle_create_user(self, data: dict):
        """Обработчик сигнала создания пользователя"""
        username = data.get("username", "")
        password = data.get("password", "")
        
        status = self.create_user(username, password)
        
        # Определяем сообщение об ошибке
        if status == UserOperationStatus.SUCCESS:
            error_msg = ""
        elif status == UserOperationStatus.USER_EXISTS:
            error_msg = "Данное имя уже занято"
        elif status == UserOperationStatus.DATABASE_ERROR:
            error_msg = "Ошибка базы данных"
        else:
            error_msg = "Неизвестная ошибка"
        
        success = status == UserOperationStatus.SUCCESS
        self.user_created.emit(success, error_msg)

    def handle_find_user(self, data: dict):
        """Обработчик сигнала поиска пользователя с проверкой пароля"""
        username = data.get("username", "")
        password = data.get("password", "")
        
        status, user = self.find_user(username, password)
        
        # Определяем сообщение об ошибке
        if status == UserOperationStatus.SUCCESS:
            error_msg = ""
        elif status == UserOperationStatus.USER_NOT_FOUND:
            error_msg = "Пользователь не найден"
        elif status == UserOperationStatus.INVALID_PASSWORD:
            error_msg = "Неверный пароль"
        elif status == UserOperationStatus.DATABASE_ERROR:
            error_msg = "Ошибка базы данных"
        else:
            error_msg = "Неизвестная ошибка"
        
        # Отправляем сигнал аутентификации
        auth_success = status == UserOperationStatus.SUCCESS
        self.user_authenticated.emit(auth_success, error_msg)
        
        # Отправляем объект пользователя (только при успехе)
        self.user_found.emit(user if auth_success else None)

    # === Методы жизненного цикла потока ===
    
    def stop(self):
        """Останавливает работу потока"""
        self._is_running = False

    def run(self):
        """Основной цикл потока"""
        # Подключаем сигналы к обработчикам
        self.create_user_requested.connect(self.handle_create_user)
        self.find_user_requested.connect(self.handle_find_user)
        
        while self._is_running:
            self.msleep(100)


# Для обратной совместимости можно оставить алиас
dataWorker = DatabaseWorker