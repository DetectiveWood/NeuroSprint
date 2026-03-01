from testpdf import ReactionReportGenerator
import pygame
import sys
import random
import sqlite3
import json
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
import time
# ====================== НАСТРОЙКИ ======================
DB_NAME = 'reaction_trainer.db'

def __init__(self):
    pygame.init()
    # Принудительное пересоздание таблиц (для отладки)
    conn = sqlite3.connect('reaction_trainer.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sessions")
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()
    init_db()  # теперь создаст чистые таблицы
    print("Таблицы пересозданы")
# ====================== БАЗА ДАННЫХ ======================

def init_db():
    conn = sqlite3.connect('reaction_trainer.db')
    cur = conn.cursor()
    # Таблица пользователей
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        last_training_date TEXT DEFAULT NULL,
        streak INTEGER DEFAULT 0
    )''')

    # Таблица сессий — полный запрос
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        avg_rt REAL,
        misses INTEGER DEFAULT 0,
        false_alarms INTEGER DEFAULT 0,
        variability REAL,
        accuracy REAL,
        correct_rts TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

    print("База данных инициализирована")

def get_or_create_user(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        print(f"✅ Создан новый пользователь: {username}")
        return cur.lastrowid
    except Exception as e:
        print(f"❌ Ошибка создания пользователя: {e}")
        return None
    finally:
        conn.close()

def save_session(user_id, metrics):
    if not user_id:
        print("❌ save_session: user_id отсутствует")
        return False
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        correct_rts_str = json.dumps(metrics.get('correct_rts', []))

        cur.execute('''INSERT INTO sessions 
            (user_id, date, avg_rt, misses, false_alarms, variability, accuracy, correct_rts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, date_str, metrics['avg_rt'], metrics['misses'],
                     metrics['false_alarms'], metrics['variability'],
                     metrics['accuracy'], correct_rts_str))
        conn.commit()
        print(f"✅ Сессия успешно сохранена! RT = {metrics['avg_rt']} мс")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения сессии: {e}")
        return False
    finally:
        conn.close()

def get_user_sessions(user_id):
    if not user_id: return []
    conn = sqlite3.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute('''SELECT date, avg_rt, misses, false_alarms, variability, accuracy 
                       FROM sessions WHERE user_id = ? ORDER BY date DESC''', (user_id,))
        rows = cur.fetchall()
        return [{
            'date': r[0], 'avg_rt': r[1], 'misses': r[2],
            'false_alarms': r[3], 'variability': r[4], 'accuracy': r[5]
        } for r in rows]
    finally:
        conn.close()

def get_leaderboard():
    conn = sqlite3.connect('reaction_trainer.db')
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT 
                u.username,
                AVG(s.avg_rt) as avg_rt,
                AVG(s.misses + s.false_alarms) as avg_errors,
                AVG(s.accuracy) as avg_accuracy
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            GROUP BY u.id, u.username
            HAVING COUNT(s.id) >= 1
            ORDER BY avg_rt ASC
            LIMIT 5
        ''')
        leaders = cur.fetchall()
        # Результат: [(username, avg_rt, avg_errors, avg_accuracy), ...]
        return leaders
    except Exception as e:
        print("Ошибка при получении лидерборда:", e)
        return []
    finally:
        conn.close()
# ====================== КНОПКА ======================
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, font_size=36):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, font_size)

    def draw(self, screen):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=12)
        txt = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ====================== ГЛАВНЫЙ КЛАСС ======================
class ReactionTrainer:
    def __init__(self):
        self.pdfGen = ReactionReportGenerator()
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        self.anonymous_mode = False  # по умолчанию выкл
        self.font_emoji = pygame.font.SysFont("segoeuisymbol", 40)  # или "segoe ui emoji", "arial unicode ms"
        self.font_emoji2 = pygame.font.SysFont("segoeuisymbol", 20)  # или "segoe ui emoji", "arial unicode ms"
        self.font_table = pygame.font.SysFont("arial", 28)
        pygame.display.set_caption("Go/No-Go Reaction Trainer")
        self.clock = pygame.time.Clock()
        self.big_font = pygame.font.Font(None, 74)
        self.med_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.user_id = None
        self.username = None
        init_db()  # ← сразу при запуске

    def get_user_credentials(self):
        username = ""
        password = ""
        mode = "login"  # или "register" — определяем по ходу

        input_stage = "username"  # username → password → check/repeat

        attempts = 0
        MAX_ATTEMPTS = 5

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_stage == "username":
                            if not username.strip():
                                continue
                            # проверяем существование пользователя
                            conn = sqlite3.connect('reaction_trainer.db')
                            cur = conn.cursor()
                            cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
                            row = cur.fetchone()
                            conn.close()

                            if row:
                                # пользователь существует → переходим к вводу пароля
                                self.user_id = row[0]
                                stored_password = row[1]
                                input_stage = "password"
                                mode = "login"
                            else:
                                # новый пользователь → просим придумать пароль
                                input_stage = "password"
                                mode = "register"

                        elif input_stage == "password":
                            if not password.strip():
                                continue

                            if mode == "login":
                                # проверка пароля
                                conn = sqlite3.connect('reaction_trainer.db')
                                cur = conn.cursor()
                                cur.execute("SELECT password FROM users WHERE id = ?", (self.user_id,))
                                stored = cur.fetchone()[0]
                                conn.close()

                                if password == stored:
                                    # успех
                                    return username
                                else:
                                    attempts += 1
                                    password = ""  # сбрасываем ввод
                                    if attempts >= MAX_ATTEMPTS:
                                        # слишком много попыток
                                        self.show_message("Слишком много неверных попыток. Выход.")
                                        pygame.quit()
                                        sys.exit()
                                    # показываем ошибку
                                    self.show_message("Неверный пароль. Попробуйте снова.")
                            else:  # register
                                # сохраняем нового пользователя
                                conn = sqlite3.connect('reaction_trainer.db')
                                cur = conn.cursor()
                                try:
                                    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                                                (username, password))
                                    conn.commit()
                                    self.user_id = cur.lastrowid
                                    return username
                                except sqlite3.IntegrityError:
                                    # имя уже занято (race condition)
                                    self.show_message("Это имя уже занято. Попробуйте другое.")
                                    username = ""
                                    password = ""
                                    input_stage = "username"
                                finally:
                                    conn.close()

                    elif event.key == pygame.K_BACKSPACE:
                        if input_stage == "username":
                            username = username[:-1]
                        else:
                            password = password[:-1]

                    elif event.unicode.isprintable():
                        if input_stage == "username":
                            if len(username) < 20:
                                username += event.unicode
                        else:
                            if len(password) < 30:
                                password += event.unicode

            # Отрисовка
            self.screen.fill((20, 20, 40))

            if input_stage == "username":
                prompt = self.med_font.render("Введите имя пользователя:", True, (255, 255, 255))
                value = self.med_font.render(username + "_", True, (0, 255, 100))
            else:
                prompt_text = "Введите пароль:" if mode == "login" else "Придумайте пароль:"
                prompt = self.med_font.render(prompt_text, True, (255, 255, 255))
                # показываем звёздочки вместо пароля
                masked = "*" * len(password) + "_"
                value = self.med_font.render(masked, True, (0, 255, 100))

            self.screen.blit(prompt, (250, 200))
            self.screen.blit(value, (250, 280))

            if input_stage == "password" and mode == "login" and attempts > 0:
                attempt_text = f"Неверный пароль. Попытка {attempts}/{MAX_ATTEMPTS}"
                attempt_surf = self.small_font.render(attempt_text, True, (255, 150, 150))
                self.screen.blit(attempt_surf, (250, 350))

            pygame.display.flip()
            self.clock.tick(30)

    def run(self):
        self.username = self.get_user_credentials()
        self.user_id = get_or_create_user(self.username)

        if not self.user_id:
            print("Не удалось создать пользователя")
            pygame.quit()
            sys.exit()

        buttons = [
            Button(350, 120, 300, 70, "Новая тренировка", (0, 120, 215), (0, 160, 255)),
            Button(350, 210, 300, 70, "История", (0, 120, 215), (0, 160, 255)),
            Button(350, 300, 300, 70, "График прогресса", (0, 120, 215), (0, 160, 255)),
            Button(350, 390, 300, 70, "PDF-отчёт", (0, 120, 215), (0, 160, 255)),
            Button(350, 480, 300, 70, "Лидерборд", (0, 120, 215), (0, 160, 255)),
            Button(350, 570, 300, 70, "Выход", (180, 0, 0), (220, 0, 0)),
        ]

        while True:
            self.screen.fill((20, 20, 40))
            self.screen.blit(self.big_font.render("Go/No-Go Тренажёр", True, (255, 255, 255)), (220, 40))

            for btn in buttons:
                btn.draw(self.screen)

            # Кнопка Анонимность — ПРАВЫЙ НИЖНИЙ УГОЛ
            anon_text = f"Анонимность: {'Вкл' if self.anonymous_mode else 'Выкл'}"
            anon_color = (0, 255, 0) if self.anonymous_mode else (255, 0, 0)
            anon_hover = (0, 220, 0) if self.anonymous_mode else (220, 0, 0)
            anon_btn = Button(
                self.screen.get_width() - 320,  # правый край минус ширина кнопки
                self.screen.get_height() - 110,  # нижний край минус высота кнопки + запас
                300, 60,
                anon_text,
                anon_color,
                anon_hover
            )
            anon_btn.draw(self.screen)

            # Получаем текущий streak
            conn = sqlite3.connect('reaction_trainer.db')
            cur = conn.cursor()
            cur.execute("SELECT streak FROM users WHERE id = ?", (self.user_id,))
            row = cur.fetchone()
            if row is None:
                # обработка случая "пользователь не найден"
                print("Пользователь не найден в базе!")
                streak = 0  # или raise ошибка, или return
            else:
                streak = row[0]
            conn.close()

            # Огонёк в правом верхнем углу
            streak_text = f"🔥 {streak}" if streak > 0 else "🔥 0"
            streak_surf = self.font_emoji.render(streak_text, True, (255, 215, 0))

            # Пульсация (анимация)
            pulse = (pygame.time.get_ticks() // 200 % 10) / 10.0  # 0..1
            scale = 1.0 + pulse * 0.08  # пульсация ±8%
            streak_surf_scaled = pygame.transform.rotozoom(streak_surf, 0, scale)

            # Центрируем с учётом масштаба
            x = self.screen.get_width() - streak_surf_scaled.get_width() - 20
            y = 20
            self.screen.blit(streak_surf_scaled, (x, y))

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    pos = e.pos
                    if buttons[0].clicked(pos):
                        self.run_training_session()
                    elif buttons[1].clicked(pos):
                        self.show_history()
                    elif buttons[2].clicked(pos):
                        self.show_progress_graph()
                    elif buttons[3].clicked(pos):
                        self.get_user_report_data()
                    elif buttons[4].clicked(pos):
                        self.show_leaderboard()
                    elif anon_btn.clicked(pos):  # клик по анонимности
                        self.anonymous_mode = not self.anonymous_mode
                        # Пересоздаём кнопку анонимности, чтобы обновить цвет и текст
                        anon_text = f"Анонимность: {'Вкл' if self.anonymous_mode else 'Выкл'}"
                        anon_color = (0, 255, 0) if self.anonymous_mode else (255, 0, 0)
                        anon_hover = (0, 220, 0) if self.anonymous_mode else (220, 0, 0)
                        anon_btn = Button(
                            self.screen.get_width() - 320,
                            self.screen.get_height() - 110,
                            300, 60,
                            anon_text,
                            anon_color,
                            anon_hover
                        )
                    elif buttons[5].clicked(pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()
            self.clock.tick(30)

    # ====================== ТРЕНИРОВКА ======================
    def run_training_session(self):
        num_trials = 60
        go_prob = 0.70
        timeout_ms = 800
        results = []

        print("🚀 Тренировка началась...")

        for trial in range(num_trials):
            is_go = random.random() < go_prob

            # Фиксация — тёмный экран
            iti = random.randint(600, 1100)
            start_iti = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_iti < iti:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                self.screen.fill((20, 20, 40))
                pygame.display.flip()
                self.clock.tick(60)

            # ────────────────────────────────────────────────
            # СТИМУЛ — рабочая версия с гарантированной отрисовкой
            # ────────────────────────────────────────────────
            responded = False
            rt = None
            stim_rect = None

            stim_start = pygame.time.get_ticks()  # ← отсчёт начинается здесь

            while pygame.time.get_ticks() - stim_start < timeout_ms:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not responded:
                        mouse_pos = e.pos
                        if stim_rect and stim_rect.collidepoint(mouse_pos):
                            responded = True
                            rt = pygame.time.get_ticks() - stim_start

                # Отрисовка каждый кадр
                self.screen.fill((20, 20, 40))

                if is_go:
                    stim_rect = pygame.draw.circle(self.screen, (0, 255, 80), (500, 350), 110)
                    txt = self.big_font.render("GO", True, (0, 0, 0))
                    self.screen.blit(txt, (460, 325))
                else:
                    stim_rect = pygame.Rect(390, 240, 220, 220)
                    pygame.draw.rect(self.screen, (255, 50, 50), stim_rect)
                    txt = self.big_font.render("NO GO", True, (0, 0, 0))
                    self.screen.blit(txt, (415, 325))

                pygame.display.flip()
                self.clock.tick(60)

            # Если не нажали — rt остаётся None
            correct = (is_go and responded) or (not is_go and not responded)
            results.append({'is_go': is_go, 'rt': rt, 'correct': correct})

            # Обратная связь
            self.screen.fill((20, 20, 40))
            if correct:
                fb = self.big_font.render("Правильно!", True, (0, 255, 100))
                self.screen.blit(fb, (350, 320))
            else:
                fb = self.big_font.render("Неправильно!", True, (255, 80, 80))
                self.screen.blit(fb, (330, 320))
            
            pygame.display.flip()
            pygame.time.wait(400)

        # ====================== РАСЧЁТ МЕТРИК ======================
        correct_go_rts = [r['rt'] for r in results if r['is_go'] and r['correct'] and r['rt'] is not None]

        avg_rt = sum(correct_go_rts) / len(correct_go_rts) if correct_go_rts else 0.0
        variability = (sum((x - avg_rt) ** 2 for x in correct_go_rts) / len(correct_go_rts)) ** 0.5 if len(
            correct_go_rts) > 1 else 0.0
        misses = sum(1 for r in results if r['is_go'] and not r['correct'])
        false_alarms = sum(1 for r in results if not r['is_go'] and not r['correct'])
        accuracy = (sum(1 for r in results if r['correct']) / num_trials * 100) if num_trials else 0.0

        metrics = {
            'avg_rt': round(avg_rt, 1),
            'misses': misses,
            'false_alarms': false_alarms,
            'variability': round(variability, 1),
            'accuracy': round(accuracy, 1),
            'correct_rts': correct_go_rts
        }

        # ====================== СОХРАНЕНИЕ ======================
        saved = save_session(self.user_id, metrics)

        # Обновляем streak после успешного сохранения сессии
        from datetime import datetime, timedelta

        today = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect('reaction_trainer.db')
        cur = conn.cursor()

        cur.execute("SELECT last_training_date, streak FROM users WHERE id = ?", (self.user_id,))
        row = cur.fetchone()

        if row:
            last_date_str, current_streak = row
            if last_date_str:
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
                today_date = datetime.now().date()

                if today_date == last_date:
                    # сегодня уже была тренировка — streak не меняется
                    pass
                elif today_date == last_date + timedelta(days=1):
                    # вчера была → увеличиваем streak
                    current_streak += 1
                else:
                    # пропущен день или больше — сбрасываем на 1
                    current_streak = 1
            else:
                # первая тренировка
                current_streak = 1

            cur.execute("""
                UPDATE users 
                SET last_training_date = ?, streak = ? 
                WHERE id = ?
            """, (today, current_streak, self.user_id))
            conn.commit()

        conn.close()

        # ====================== ПОКАЗ РЕЗУЛЬТАТОВ ======================
        self.show_session_results(metrics, saved)

    def show_session_results(self, metrics, saved_ok):
        while True:
            self.screen.fill((20, 20, 40))

            if not saved_ok:
                err = self.small_font.render("⚠️ Ошибка сохранения в БД!", True, (255, 80, 80))
                self.screen.blit(err, (280, 100))

            lines = [
                f"Среднее время реакции: {metrics['avg_rt']} мс",
                f"Пропуски: {metrics['misses']}",
                f"Ложные нажатия: {metrics['false_alarms']}",
                f"Вариабельность: {metrics['variability']} мс",
                f"Точность: {metrics['accuracy']}%"
            ]
            for i, line in enumerate(lines):
                txt = self.small_font.render(line, True, (255, 255, 255))
                self.screen.blit(txt, (180, 180 + i * 55))

            back_btn = Button(380, 520, 240, 70, "Назад в меню", (0, 120, 215), (0, 160, 255))
            back_btn.draw(self.screen)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if back_btn.clicked(e.pos):
                        print("↩️ Возврат в главное меню")
                        return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    return

            pygame.display.flip()
            self.clock.tick(30)

    # ====================== ОСТАЛЬНЫЕ МЕТОДЫ (без изменений по логике) ======================
    def show_history(self):
        sessions = get_user_sessions(self.user_id)

        while True:
            self.screen.fill((20, 20, 40))

            # Заголовок
            title = self.med_font.render("История тренировок", True, (255, 255, 255))
            self.screen.blit(title, (320, 40))

            if not sessions:
                txt = self.small_font.render("Пока нет тренировок", True, (255, 200, 100))
                self.screen.blit(txt, (320, 300))
            else:
                # Заголовок таблицы — чуть крупнее и жирнее
                header_font = pygame.font.Font(None, 34)
                header = header_font.render("Дата       Среднее время реакции   Точность   Вариабельность", True,
                                            (180, 220, 255))
                self.screen.blit(header, (80, 110))

                # линия-разделитель
                pygame.draw.line(self.screen, (120, 120, 160), (70, 145), (920, 145), 2)

                y = 160
                for sess in sessions[:12]:  # последние 12, чтобы не переполнять экран
                    date_short = sess['date'][:10].replace('-', '.')

                    rt_text = f"{sess['avg_rt']:.1f} мс" if sess['avg_rt'] > 0 else "—"
                    acc_text = f"{sess['accuracy']:.1f}%"
                    var_text = f"{sess['variability']:.1f} мс" if sess['variability'] > 0 else "—"

                    # выравнивание колонок
                    line = f"{date_short:<10}   {rt_text:>16}   {acc_text:>10}   {var_text:>16}"

                    txt = self.small_font.render(line, True, (220, 240, 255))
                    self.screen.blit(txt, (80, y))
                    y += 38

            # кнопка Назад
            back_btn = Button(380, 580, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back_btn.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_btn.clicked(event.pos):
                        return

            pygame.display.flip()
            self.clock.tick(30)

    def show_message(self, text, duration=2000, color=(255, 200, 100)):
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # выход по клику (опционально)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

            self.screen.fill((20, 20, 40))

            msg_surf = self.med_font.render(text, True, color)
            msg_rect = msg_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(msg_surf, msg_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def show_leaderboard(self):
        leaders = get_leaderboard()

        conn = sqlite3.connect('reaction_trainer.db')
        cur = conn.cursor()

        leaders_with_streak = []
        for username, avg_rt, avg_errors, avg_acc in leaders:
            cur.execute("SELECT streak FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            streak = row[0] if row else 0
            leaders_with_streak.append((username, avg_rt, avg_errors, avg_acc, streak))

        conn.close()

        while True:
            self.screen.fill((20, 20, 40))

            title = self.med_font.render("Топ-5 по скорости реакции", True, (255, 255, 255))
            self.screen.blit(title, (280, 60))

            if not leaders_with_streak:
                txt = self.small_font.render("Пока нет участников", True, (255, 200, 100))
                self.screen.blit(txt, (350, 300))
            else:
                header = self.font_table.render("№  Имя         Реакция      Ошибки   Точность   Стрик", True,
                                                (180, 220, 255))
                self.screen.blit(header, (80, 120))
                pygame.draw.line(self.screen, (100, 100, 150), (70, 155), (920, 155), 2)

                y = 170
                detail_buttons = []  # список для кликабельных квадратиков

                for rank, (username, avg_rt, avg_errors, avg_acc, streak) in enumerate(leaders_with_streak, 1):
                    color = (255, 215, 0) if rank == 1 else (220, 220, 255)

                    line = f"{rank:<2}  {username:<10} {avg_rt:>6.1f} мс     {avg_errors:>6.1f}      {avg_acc:>6.1f}%"
                    txt = self.small_font.render(line, True, color)
                    self.screen.blit(txt, (80, y))

                    # 🔥 стрик (остаётся как было)
                    streak_text = f"🔥 {streak}"
                    streak_color = (255, 140, 0) if streak > 0 else (150, 150, 150)
                    streak_surf = self.font_emoji2.render(streak_text, True, streak_color)
                    self.screen.blit(streak_surf, (80 + txt.get_width() + 40, y-5))

                    # Маленький квадратик "Подробнее" — теперь 28×28
                    detail_rect = pygame.Rect(900, y - 3, 24, 24)  # +6 по y для центрирования по строке
                    pygame.draw.rect(self.screen, (100, 100, 255), detail_rect, border_radius=5)  # закругление меньше
                    detail_text = self.small_font.render("...", True, (255, 255, 255))
                    self.screen.blit(detail_text, (detail_rect.centerx - detail_text.get_width() // 2,
                                                   detail_rect.centery - detail_text.get_height() // 2))

                    detail_buttons.append((detail_rect, username))

                    y += 45

            back_btn = Button(380, 580, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back_btn.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if back_btn.clicked(pos):
                        return

                    # Проверяем клик по значкам "Подробнее"
                    for rect, username in detail_buttons:
                        if rect.collidepoint(pos):
                            if self.anonymous_mode:
                                self.show_message("Анонимный режим включён — сравнение недоступно",
                                                  color=(255, 100, 100))
                            else:
                                self.show_compare_menu(username)
                            break

            pygame.display.flip()
            self.clock.tick(30)

    def show_compare_menu(self, other_username):
        while True:
            self.screen.fill((20, 20, 40))

            title = self.med_font.render(f"Сравнение с {other_username}", True, (255, 255, 255))
            self.screen.blit(title, (290, 100))

            history_btn = Button(300, 200, 400, 80, "Увидеть историю", (0, 180, 0), (0, 220, 0))
            graphs_btn = Button(300, 300, 400, 80, "Увидеть графики", (0, 120, 215), (0, 160, 255))

            history_btn.draw(self.screen)
            graphs_btn.draw(self.screen)

            back_btn = Button(380, 500, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back_btn.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if history_btn.clicked(pos):
                        self.show_compare_history(other_username)
                    elif graphs_btn.clicked(pos):
                        self.show_compare_graphs(other_username)
                    elif back_btn.clicked(pos):
                        return

            pygame.display.flip()
            self.clock.tick(30)

    def show_compare_history(self, other_username):
        # Получаем ID другого пользователя
        conn = sqlite3.connect('reaction_trainer.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (other_username,))
        row = cur.fetchone()
        other_id = row[0] if row else None
        conn.close()

        if other_id is None:
            self.show_message("Пользователь не найден", color=(255, 100, 100))
            return

        other_sessions = get_user_sessions(other_id)
        my_sessions = get_user_sessions(self.user_id)

        if len(other_sessions) == 0 and len(my_sessions) == 0:
            self.show_message("Нет историй для сравнения", color=(255, 200, 100))
            return

        while True:
            self.screen.fill((20, 20, 40))

            title = self.med_font.render(f"Сравнение истории: {other_username}", True, (255, 255, 255))
            self.screen.blit(title, (280, 40))

            # Левая колонка — чужая история (ближе к левому краю)
            left_title = self.small_font.render(f"{other_username}", True, (255, 200, 100))
            self.screen.blit(left_title, (20, 100))

            y = 140
            for sess in other_sessions[:10]:
                line = f"{sess['date'][:10]} | RT: {sess['avg_rt']:.1f} мс | Acc: {sess['accuracy']:.1f}%"
                txt = self.small_font.render(line, True, (200, 220, 255))  # светло-синий
                self.screen.blit(txt, (20, y))
                y += 35  # расстояние между строками чужой истории

            # Правая колонка — твоя история (другой цвет + большее расстояние)
            right_title = self.small_font.render("Твоя история", True, (100, 255, 100))
            self.screen.blit(right_title, (520, 100))

            y = 140
            for sess in my_sessions[:10]:
                line = f"{sess['date'][:10]} | RT: {sess['avg_rt']:.1f} мс | Acc: {sess['accuracy']:.1f}%"
                txt = self.small_font.render(line, True, (120, 255, 120))  # ярко-зелёный
                self.screen.blit(txt, (520, y))
                y += 35  # большее расстояние между твоими строками

            back_btn = Button(380, 580, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back_btn.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_btn.clicked(event.pos):
                        return

            pygame.display.flip()
            self.clock.tick(30)

    def show_compare_graphs(self, other_username):
        conn = sqlite3.connect('reaction_trainer.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (other_username,))
        row = cur.fetchone()
        other_id = row[0] if row else None
        conn.close()

        if other_id is None:
            self.show_message("Пользователь не найден", color=(255, 100, 100))
            return

        other_sessions = get_user_sessions(other_id)
        my_sessions = get_user_sessions(self.user_id)

        if len(other_sessions) < 2 or len(my_sessions) < 2:
            self.show_message("Недостаточно данных для сравнения графиков", color=(255, 200, 100))
            return

        my_sorted = sorted(my_sessions, key=lambda x: x['date'])
        other_sorted = sorted(other_sessions, key=lambda x: x['date'])

        my_numbers = list(range(1, len(my_sorted) + 1))
        my_rts = [s['avg_rt'] for s in my_sorted]
        my_acc = [s['accuracy'] for s in my_sorted]

        other_numbers = list(range(1, len(other_sorted) + 1))
        other_rts = [s['avg_rt'] for s in other_sorted]
        other_acc = [s['accuracy'] for s in other_sorted]

        # График (большой размер)
        plt.figure(figsize=(9.5, 7.0), facecolor='#141428', dpi=180)

        plt.subplot(2, 1, 1)
        plt.plot(my_numbers, my_rts, marker='o', linewidth=3, color='#00FF9F', label='Ты', markersize=8)
        plt.plot(other_numbers, other_rts, marker='s', linewidth=3, color='#FF6B6B', label=f'{other_username}',
                 markersize=8)
        plt.title('Сравнение среднего времени реакции', fontsize=15, color='white', fontweight='bold')
        plt.ylabel('Среднее RT (мс)', color='white')
        plt.tick_params(colors='white', labelsize=11)
        plt.gca().set_facecolor('#141428')
        plt.grid(True, alpha=0.3, color='gray')
        plt.legend(fontsize=10, labelcolor='black')

        plt.subplot(2, 1, 2)
        plt.plot(my_numbers, my_acc, marker='o', linewidth=3, color='#00FF9F', label='Ты', markersize=8)
        plt.plot(other_numbers, other_acc, marker='s', linewidth=3, color='#FF6B6B', label=f'{other_username}',
                 markersize=8)
        plt.title('Сравнение точности (%)', fontsize=15, color='white', fontweight='bold')
        plt.xlabel('Номер тренировки', color='white')
        plt.ylabel('Точность (%)', color='white')
        plt.tick_params(colors='white', labelsize=11)
        plt.gca().set_facecolor('#141428')
        plt.grid(True, alpha=0.3, color='gray')
        plt.legend(fontsize=10, labelcolor='black')

        plt.tight_layout(pad=1.5)

        graph_path = "temp_compare.png"
        plt.savefig(graph_path, facecolor='#141428', dpi=180)
        plt.close()

        try:
            graph = pygame.image.load(graph_path)
            graph = pygame.transform.smoothscale(graph, (920, 720))  # большой размер
        except:
            graph = None

        # Прокрутка
        scroll_y = 0
        scroll_speed = 60  # увеличил скорость для удобства
        graph_height = 720
        content_top = 80
        content_bottom = content_top + graph_height + 80  # отступ после второго графика
        max_scroll = self.screen.get_height() - content_bottom  # когда конец контента виден
        max_scroll = min(0, max_scroll)  # не больше 0

        back_btn = Button(380, self.screen.get_height() - 80, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    # Кнопка активна ТОЛЬКО если прокручено до конца
                    if scroll_y <= max_scroll and back_btn.clicked(pos):
                        return
                if event.type == pygame.MOUSEWHEEL:
                    scroll_y += event.y * scroll_speed
                    scroll_y = min(0, max(max_scroll, scroll_y))  # ограничиваем

            self.screen.fill((20, 20, 40))

            if graph:
                self.screen.blit(graph, (40, content_top + scroll_y))
            else:
                txt = self.med_font.render("Не удалось построить график сравнения", True, (255, 100, 100))
                self.screen.blit(txt, (200, 300 + scroll_y))

            # Кнопка появляется ТОЛЬКО когда прокручено до конца
            if scroll_y <= max_scroll:
                back_btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def show_progress_graph(self):
        sessions = get_user_sessions(self.user_id)

        if len(sessions) < 2:
            while True:
                self.screen.fill((20, 20, 40))
                txt = self.med_font.render("Недостаточно данных для графика", True, (255, 200, 100))
                self.screen.blit(txt, (220, 300))
                back_btn = Button(380, 520, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
                back_btn.draw(self.screen)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if back_btn.clicked(event.pos):
                            return
                pygame.display.flip()
                self.clock.tick(30)
            return

        # Сортируем сессии
        sessions_sorted = sorted(sessions, key=lambda x: x['date'])
        training_numbers = list(range(1, len(sessions_sorted) + 1))

        rts = [s['avg_rt'] for s in sessions_sorted]
        accuracy = [s['accuracy'] for s in sessions_sorted]

        # График 1: Среднее время реакции
        plt.figure(figsize=(9, 5), facecolor='#141428', dpi=180)
        plt.plot(training_numbers, rts, marker='o', linewidth=3, color='#00FF9F', markersize=9)
        plt.title('Прогресс среднего времени реакции', fontsize=16, color='white')
        plt.xlabel('Номер тренировки', fontsize=12, color='white')
        plt.ylabel('Среднее RT (мс)', fontsize=12, color='white')
        plt.tick_params(colors='white', labelsize=10)
        plt.gca().set_facecolor('#141428')
        plt.grid(True, alpha=0.3, color='gray', linestyle='--')
        plt.xticks(training_numbers)
        plt.tight_layout()
        plt.savefig("temp_rt.png", facecolor='#141428', dpi=180)
        plt.close()

        # График 2: Точность
        plt.figure(figsize=(9, 5), facecolor='#141428', dpi=180)
        plt.plot(training_numbers, accuracy, marker='s', linewidth=3, color='#4DA6FF', markersize=9)
        plt.title('Прогресс точности (%)', fontsize=16, color='white')
        plt.xlabel('Номер тренировки', fontsize=12, color='white')
        plt.ylabel('Точность (%)', fontsize=12, color='white')
        plt.tick_params(colors='white', labelsize=10)
        plt.gca().set_facecolor('#141428')
        plt.grid(True, alpha=0.3, color='gray', linestyle='--')
        plt.xticks(training_numbers)
        plt.tight_layout()
        plt.savefig("temp_acc.png", facecolor='#141428', dpi=180)
        plt.close()

        # Загрузка графиков
        try:
            graph_rt = pygame.image.load("temp_rt.png")
            graph_rt = pygame.transform.smoothscale(graph_rt, (860, 480))
            graph_acc = pygame.image.load("temp_acc.png")
            graph_acc = pygame.transform.smoothscale(graph_acc, (860, 480))
        except:
            graph_rt = graph_acc = None

        # Прокрутка
        scroll_y = 0
        scroll_speed = 30
        max_scroll = -480  # максимальное смещение вниз (высота второго графика)

        back_btn = Button(380, 600, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_btn.clicked(event.pos) and scroll_y <= max_scroll:
                        return  # выход только если прокручено до конца
                if event.type == pygame.MOUSEWHEEL:
                    scroll_y += event.y * scroll_speed
                    scroll_y = min(0, max(max_scroll, scroll_y))  # ограничиваем: от 0 до max_scroll

            self.screen.fill((20, 20, 40))

            # Рисуем графики с учётом прокрутки
            if graph_rt:
                self.screen.blit(graph_rt, (70, 80 + scroll_y))
            if graph_acc:
                self.screen.blit(graph_acc, (70, 580 + scroll_y))

            # Кнопка "Назад" видна ТОЛЬКО когда прокручено до конца
            if scroll_y <= max_scroll:
                back_btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def generate_pdf_report(self):
        sessions = get_user_sessions(self.user_id)
        if not sessions:
            self.show_message("Нет данных для отчёта", duration=2500)
            return

        sessions_sorted = sorted(sessions, key=lambda x: x['date'])
        last = sessions_sorted[-1]

        # Средние значения
        avg_rt = sum(s['avg_rt'] for s in sessions) / len(sessions)
        avg_acc = sum(s['accuracy'] for s in sessions) / len(sessions)
        avg_var = sum(s['variability'] for s in sessions) / len(sessions)

        # Графики
        training_numbers = list(range(1, len(sessions_sorted) + 1))
        rts = [s['avg_rt'] for s in sessions_sorted]
        accuracy = [s['accuracy'] for s in sessions_sorted]

        # График 1 — Время реакции
        plt.figure(figsize=(7.5, 3.6), facecolor='#141428', dpi=200)
        plt.plot(training_numbers, rts, marker='o', linewidth=3, color='#00FF9F')
        plt.title('Прогресс среднего времени реакции', color='white')
        plt.xlabel('Номер тренировки', color='white')
        plt.ylabel('RT (мс)', color='white')
        plt.tick_params(colors='white')
        plt.grid(True, alpha=0.3)
        plt.xticks(training_numbers)
        plt.tight_layout()
        plt.savefig("temp_rt.png", facecolor='#141428', dpi=200)
        plt.close()

        # График 2 — Точность
        plt.figure(figsize=(7.5, 3.6), facecolor='#141428', dpi=200)
        plt.plot(training_numbers, accuracy, marker='s', linewidth=3, color='#4DA6FF')
        plt.title('Прогресс точности', color='white')
        plt.xlabel('Номер тренировки', color='white')
        plt.ylabel('Точность (%)', color='white')
        plt.tick_params(colors='white')
        plt.grid(True, alpha=0.3)
        plt.xticks(training_numbers)
        plt.tight_layout()
        plt.savefig("temp_acc.png", facecolor='#141428', dpi=200)
        plt.close()

        # PDF
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf", uni=True)
        pdf.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf", uni=True)

        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "Go/No-Go Тренажёр — Отчёт", ln=1, align="C")

        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, f"Пользователь: {self.username}", ln=1)
        pdf.cell(0, 10, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=1)
        pdf.cell(0, 10, f"Всего тренировок: {len(sessions)}", ln=1)
        pdf.ln(10)

        pdf.set_font("Arial", "", 13)
        pdf.cell(0, 10, f"Среднее время реакции: {avg_rt:.1f} мс", ln=1)
        pdf.cell(0, 10, f"Средняя точность: {avg_acc:.1f}%", ln=1)
        pdf.cell(0, 10, f"Средняя вариабельность: {avg_var:.1f} мс", ln=1)
        pdf.ln(15)

        # Графики
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Прогресс среднего времени реакции", ln=1)
        if os.path.exists("temp_rt.png"):
            pdf.image("temp_rt.png", x=10, y=pdf.get_y(), w=190)
            pdf.ln(95)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Прогресс точности (%)", ln=1)
        if os.path.exists("temp_acc.png"):
            pdf.image("temp_acc.png", x=10, y=pdf.get_y(), w=190)

        pdf.output("reaction_report.pdf")

        # Удаляем временные файлы
        for f in ["temp_rt.png", "temp_acc.png"]:
            try:
                os.remove(f)
            except:
                pass

    def get_user_report_data(self):
        sessions = get_user_sessions(self.user_id)
        if not sessions:
            self.show_message("Нет данных для отчёта", duration=2500)
            return None

        sessions_sorted = sorted(sessions, key=lambda x: x['date'])

        n = len(sessions_sorted)
        if n == 0:
            return None

        # Средние
        avg_rt   = sum(s['avg_rt']       for s in sessions_sorted) / n
        avg_acc  = sum(s['accuracy']     for s in sessions_sorted) / n
        avg_miss = sum(s['misses']       for s in sessions_sorted) / n
        avg_fa   = sum(s['false_alarms'] for s in sessions_sorted) / n
        avg_var  = sum(s['variability']  for s in sessions_sorted) / n

        # Изменение RT
        first = sessions_sorted[0]['avg_rt']
        last  = sessions_sorted[-1]['avg_rt']
        if first > 0:
            pct = 100 * (first - last) / first
            reaction_change = f"{pct:+.1f}"
        else:
            reaction_change = "—"

        last_s = sessions_sorted[-1]

        data = {
            'user_id': self.username,
            'report_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'total_sessions': n,

            'avg_reaction': round(avg_rt, 1),
            'avg_accuracy': round(avg_acc, 1),
            'avg_misses': round(avg_miss, 1),
            'avg_false_presses': round(avg_fa, 1),
            'avg_variability': round(avg_var, 1),
            'reaction_change': reaction_change,

            'last_session': {
                'date': last_s['date'],
                'reaction': round(last_s['avg_rt'], 1),
                'accuracy': round(last_s['accuracy'], 1),
                'misses': last_s['misses'],
                'false_presses': last_s['false_alarms'],
                'variability': round(last_s['variability'], 1),
            },

            'progress_data': {
                'dates': list(range(1, n+1)),
                'values': [round(s['avg_rt'], 1) for s in sessions_sorted],
            },

            'mistake_data': {
                'dates': list(range(1, n+1)),
                'values': [s['misses'] + s['false_alarms'] for s in sessions_sorted],
            }
        }
        print(data)
        self.pdfGen.generate_report(data)
        return data


if __name__ == "__main__":
    print("=== Go/No-Go Reaction Trainer запущен ===")
    app = ReactionTrainer()
    app.run()