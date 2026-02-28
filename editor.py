import sqlite3
from datetime import datetime

DB_NAME = 'reaction_trainer.db'
def migrate_database():
    conn = sqlite3.connect('reaction_trainer.db')
    cur = conn.cursor()
    try:
        # Проверяем столбцы в users
        cur.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cur.fetchall()]

        # Добавляем last_training_date, если нет
        if 'last_training_date' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN last_training_date TEXT DEFAULT NULL")
            conn.commit()
            print("Добавлен столбец last_training_date")

        # Добавляем streak, если нет
        if 'streak' not in columns:
            cur.execute("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0")
            conn.commit()
            print("Добавлен столбец streak")

        print("Миграция завершена")
    except Exception as e:
        print("Ошибка миграции:", e)
    finally:
        conn.close()

def edit_user_data():
    """Консольный редактор данных пользователей"""
    print("=== Редактирование данных пользователей ===")
    print("Подключение к базе:", DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    while True:
        print("\nДоступные действия:")
        print("1. Показать всех пользователей")
        print("2. Изменить данные конкретного пользователя")
        print("3. Добавить нового пользователя")
        print("4. Удалить пользователя")
        print("0. Выход")

        choice = input("Выбери действие (0-4): ").strip()

        if choice == '0':
            break

        elif choice == '1':
            # Показать всех
            cur.execute("SELECT id, username, password, last_training_date, streak FROM users")
            rows = cur.fetchall()
            if not rows:
                print("В базе пока нет пользователей.")
            else:
                print("\nID | Username | Password | Последняя тренировка | Streak")
                print("-" * 70)
                for row in rows:
                    print(f"{row[0]:2} | {row[1]:<10} | {row[2]:<10} | {row[3] or 'нет':<19} | {row[4]:>5}")

        elif choice == '2':
            # Изменение существующего
            user_id = input("Введи ID пользователя: ").strip()
            if not user_id.isdigit():
                print("ID должен быть числом")
                continue

            user_id = int(user_id)
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()

            if not user:
                print(f"Пользователь с ID {user_id} не найден.")
                continue

            print(f"\nТекущие данные пользователя {user[1]} (ID {user[0]}):")
            print(f"  Имя:       {user[1]}")
            print(f"  Пароль:    {user[2]}")
            print(f"  Последняя тренировка: {user[3] or 'нет'}")
            print(f"  Streak:    {user[4]}")

            print("\nЧто хочешь изменить? (можно несколько через пробел)")
            print("u - имя пользователя")
            print("p - пароль")
            print("d - дата последней тренировки (формат YYYY-MM-DD)")
            print("s - streak (число)")
            print("всё - изменить все поля")
            print("отмена - выйти")

            fields = input("Выбор: ").lower().strip()

            if 'отмена' in fields:
                continue

            changes = {}

            if 'u' in fields or 'всё' in fields:
                new_username = input("Новое имя пользователя: ").strip()
                if new_username:
                    changes['username'] = new_username

            if 'p' in fields or 'всё' in fields:
                new_password = input("Новый пароль: ").strip()
                if new_password:
                    changes['password'] = new_password

            if 'd' in fields or 'всё' in fields:
                new_date = input("Новая дата последней тренировки (YYYY-MM-DD или пусто): ").strip()
                if new_date:
                    try:
                        datetime.strptime(new_date, '%Y-%m-%d')
                        changes['last_training_date'] = new_date
                    except ValueError:
                        print("Неверный формат даты! Пропускаю.")
                        continue

            if 's' in fields or 'всё' in fields:
                new_streak = input("Новый streak (целое число): ").strip()
                if new_streak.isdigit():
                    changes['streak'] = int(new_streak)
                else:
                    print("Неверное число! Пропускаю streak.")

            if not changes:
                print("Ничего не изменилось.")
                continue

            # Формируем запрос
            set_clause = ", ".join(f"{k} = ?" for k in changes)
            values = list(changes.values())
            values.append(user_id)

            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            cur.execute(query, values)
            conn.commit()

            print("Данные успешно обновлены!")

        elif choice == '3':
            # Новый пользователь
            username = input("Имя пользователя: ").strip()
            if not username:
                print("Имя не может быть пустым")
                continue

            password = input("Пароль: ").strip()
            if not password:
                print("Пароль не может быть пустым")
                continue

            streak = input("Начальный streak (обычно 0): ").strip()
            streak = int(streak) if streak.isdigit() else 0

            last_date = input("Дата последней тренировки (YYYY-MM-DD или пусто): ").strip() or None

            try:
                cur.execute("""
                    INSERT INTO users (username, password, last_training_date, streak)
                    VALUES (?, ?, ?, ?)
                """, (username, password, last_date, streak))
                conn.commit()
                print(f"Пользователь {username} добавлен (ID: {cur.lastrowid})")
            except sqlite3.IntegrityError:
                print("Ошибка: имя пользователя уже занято!")

        elif choice == '4':
            # Удаление
            user_id = input("ID пользователя для удаления: ").strip()
            if not user_id.isdigit():
                print("ID должен быть числом")
                continue

            confirm = input(f"Точно удалить пользователя с ID {user_id}? (да/нет): ").lower()
            if confirm == 'да':
                cur.execute("DELETE FROM users WHERE id = ?", (int(user_id),))
                conn.commit()
                print("Пользователь удалён.")
            else:
                print("Отмена.")

    conn.close()
    print("\nРедактирование завершено. База закрыта.")

if __name__ == "__main__":
    migrate_database()
    edit_user_data()