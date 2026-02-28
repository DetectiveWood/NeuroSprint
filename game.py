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
def init_db(force_recreate=False):
    conn = sqlite3.connect('reaction_trainer.db')
    cur = conn.cursor()

    if force_recreate:
        cur.execute("DROP TABLE IF EXISTS sessions")
        cur.execute("DROP TABLE IF EXISTS users")
        print("Старые таблицы удалены (force_recreate=True)")

    # Таблица пользователей
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # Таблица сессий
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
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
    conn.close()
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
            SELECT u.username, AVG(s.avg_rt) as avg_rt 
            FROM users u 
            JOIN sessions s ON u.id = s.user_id 
            GROUP BY u.id, u.username 
            HAVING COUNT(s.id) >= 1
            ORDER BY avg_rt ASC 
            LIMIT 5
        ''')
        leaders = cur.fetchall()
        return leaders  # список кортежей: [(username, avg_rt), ...]
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
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
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
                        self.generate_pdf_report()
                    elif buttons[4].clicked(pos):
                        self.show_leaderboard()
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
                    self.screen.blit(txt, (435, 310))
                else:
                    stim_rect = pygame.Rect(390, 240, 220, 220)
                    pygame.draw.rect(self.screen, (255, 50, 50), stim_rect)
                    txt = self.big_font.render("NO GO", True, (0, 0, 0))
                    self.screen.blit(txt, (410, 310))

                pygame.display.flip()
                self.clock.tick(60)

            # Если не нажали — rt остаётся None
            correct = (is_go and responded) or (not is_go and not responded)
            results.append({'is_go': is_go, 'rt': rt, 'correct': correct})

            # Обратная связь
            self.screen.fill((20, 20, 40))
            if correct:
                fb = self.big_font.render("Правильно!", True, (0, 255, 100))
            else:
                fb = self.big_font.render("Ошибка!", True, (255, 80, 80))
            self.screen.blit(fb, (360, 300))
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
        leaders = get_leaderboard()  # предполагается, что функция уже есть

        while True:
            self.screen.fill((20, 20, 40))

            title = self.med_font.render("Топ-5 по скорости реакции", True, (255, 255, 255))
            self.screen.blit(title, (280, 60))

            if not leaders:
                txt = self.small_font.render("Пока нет данных", True, (255, 200, 100))
                self.screen.blit(txt, (380, 300))
            else:
                y = 140
                for rank, (username, avg_rt) in enumerate(leaders, 1):
                    color = (255, 215, 0) if rank == 1 else (220, 220, 255)
                    line = f"{rank}. {username} — {avg_rt:.1f} мс"
                    txt = self.small_font.render(line, True, color)
                    self.screen.blit(txt, (200, y))
                    y += 50

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

    def show_progress_graph(self):
        sessions = get_user_sessions(self.user_id)
        if len(sessions) < 2:
            # ... код с сообщением ...
            return

        dates = [s['date'][:10] for s in sessions[::-1]]
        rts = [s['avg_rt'] for s in sessions[::-1]]

        plt.figure(figsize=(9, 5), facecolor='#141428')  # тёмный фон графика

        # Сам график
        plt.plot(dates, rts, marker='o', linewidth=3, color='#00ff88')

        # Текст и оси — всё белое
        plt.title('Прогресс скорости реакции', fontsize=16, color='white', pad=15)
        plt.xlabel('Дата', fontsize=12, color='white')
        plt.ylabel('Среднее время реакции (мс)', fontsize=12, color='white')

        # Цвет меток осей
        plt.tick_params(axis='x', colors='white', labelsize=10)
        plt.tick_params(axis='y', colors='white', labelsize=10)

        # Сетка светло-серого цвета
        plt.grid(True, alpha=0.3, color='gray', linestyle='--')

        # Фон осей тоже тёмный
        plt.gca().set_facecolor('#141428')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Сохраняем с тёмным фоном
        plt.savefig('progress.png', facecolor='#141428', bbox_inches='tight', dpi=120)
        plt.close()

        # Загружаем в pygame
        try:
            graph = pygame.image.load('progress.png')
            graph = pygame.transform.scale(graph, (860, 480))
        except:
            graph = None

        while True:
            self.screen.fill((20, 20, 40))
            if graph:
                self.screen.blit(graph, (70, 90))
            else:
                txt = self.self.med_font.render("Не удалось загрузить график", True, (255, 100, 100))
                self.screen.blit(txt, (250, 300))

            back_btn = Button(380, 600, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
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

    def generate_pdf_report(self):
        sessions = get_user_sessions(self.user_id)
        if not sessions:
            # показ сообщения на экране (оставляем как было)
            return

        # ────────────────────────────────────────────────
        # 1. Готовим график (аналогично show_progress_graph)
        # ────────────────────────────────────────────────
        dates = [s['date'][:10] for s in sessions[::-1]]  # последние → первые
        rts = [s['avg_rt'] for s in sessions[::-1]]

        plt.figure(figsize=(7.5, 4.0), dpi=100)
        plt.plot(dates, rts, marker='o', color='#00aa88', linewidth=2.5, markersize=8)
        plt.title('Прогресс среднего времени реакции', fontsize=14, pad=12)
        plt.xlabel('Дата', fontsize=11)
        plt.ylabel('Среднее RT, мс', fontsize=11)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        graph_path = "temp_progress_graph.png"
        plt.savefig(graph_path, dpi=120, bbox_inches='tight')
        plt.close()

        # ────────────────────────────────────────────────
        # 2. Считаем сводные показатели
        # ────────────────────────────────────────────────
        all_rts = [s['avg_rt'] for s in sessions if s['avg_rt'] > 0]
        all_acc = [s['accuracy'] for s in sessions]
        all_misses = [s['misses'] for s in sessions]
        all_fa = [s['false_alarms'] for s in sessions]
        all_var = [s['variability'] for s in sessions]

        avg_rt_all = sum(all_rts) / len(all_rts) if all_rts else 0
        avg_accuracy = sum(all_acc) / len(all_acc) if all_acc else 0
        avg_misses = sum(all_misses) / len(all_misses) if all_misses else 0
        avg_false = sum(all_fa) / len(all_fa) if all_fa else 0
        avg_variability = sum(all_var) / len(all_var) if all_var else 0

        # Изменение RT от первой к последней сессии
        if len(sessions) >= 2:
            first_rt = sessions[-1]['avg_rt']  # самая старая
            last_rt = sessions[0]['avg_rt']  # самая новая
            rt_change_pct = ((first_rt - last_rt) / first_rt * 100) if first_rt > 0 else 0
            trend_text = f"Изменение RT: {rt_change_pct:+.1f}% (от первой к последней сессии)"
        else:
            trend_text = "Недостаточно сессий для расчёта тренда"

        # ────────────────────────────────────────────────
        # 3. Создаём PDF
        # ────────────────────────────────────────────────
        pdf = FPDF()
        pdf.add_page()

        # Шрифты
        pdf.add_font("ArialCyr", "", r"C:\Windows\Fonts\arial.ttf")
        pdf.add_font("ArialCyr", "B", r"C:\Windows\Fonts\arialbd.ttf")

        # Заголовок
        pdf.set_font("ArialCyr", "B", 20)
        pdf.cell(0, 15, "Go/No-Go Тренажёр — Отчёт", ln=1, align="C")

        # Информация о пользователе
        pdf.set_font("ArialCyr", "", 14)
        pdf.cell(0, 10, f"Пользователь: {self.username}", ln=1)
        pdf.cell(0, 10, f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=1)
        pdf.cell(0, 10, f"Всего тренировок: {len(sessions)}", ln=1)
        pdf.ln(6)

        # Краткая сводка
        pdf.set_font("ArialCyr", "B", 16)
        pdf.cell(0, 12, "Сводка по всем сессиям", ln=1)

        pdf.set_font("ArialCyr", "", 13)
        pdf.cell(0, 10, f"Среднее время реакции (все сессии): {avg_rt_all:.1f} мс", ln=1)
        pdf.cell(0, 10, f"Средняя точность: {avg_accuracy:.1f}%", ln=1)
        pdf.cell(0, 10, f"Среднее количество пропусков: {avg_misses:.1f}", ln=1)
        pdf.cell(0, 10, f"Среднее количество ложных нажатий: {avg_false:.1f}", ln=1)
        pdf.cell(0, 10, f"Средняя вариабельность: {avg_variability:.1f} мс", ln=1)
        pdf.set_font("ArialCyr", "", 12)
        pdf.cell(0, 10, trend_text, ln=1)
        pdf.ln(8)

        # Последняя сессия
        pdf.set_font("ArialCyr", "B", 16)
        pdf.cell(0, 12, "Последняя сессия", ln=1)

        pdf.set_font("ArialCyr", "", 13)
        last = sessions[0]
        pdf.cell(0, 10, f"Дата: {last['date']}", ln=1)
        pdf.cell(0, 10, f"Среднее время реакции: {last['avg_rt']} мс", ln=1)
        pdf.cell(0, 10, f"Точность: {last['accuracy']}%", ln=1)
        pdf.cell(0, 10, f"Пропуски: {last['misses']}", ln=1)
        pdf.cell(0, 10, f"Ложные нажатия: {last['false_alarms']}", ln=1)
        pdf.cell(0, 10, f"Вариабельность: {last['variability']} мс", ln=1)
        pdf.ln(10)

        # График
        pdf.set_font("ArialCyr", "B", 14)
        pdf.cell(0, 10, "График прогресса", ln=1)

        if os.path.exists(graph_path):
            pdf.image(graph_path, x=10, w=190)  # ширина почти на всю страницу
        else:
            pdf.set_font("ArialCyr", "I", 11)
            pdf.cell(0, 10, "(график не удалось сгенерировать)", ln=1)

        pdf.output("reaction_report.pdf")
        print("PDF сохранён →", os.path.abspath("reaction_report.pdf"))

        # Удаляем временный график (опционально)
        try:
            os.remove(graph_path)
        except:
            pass

if __name__ == "__main__":
    print("=== Go/No-Go Reaction Trainer запущен ===")
    app = ReactionTrainer()
    app.run()