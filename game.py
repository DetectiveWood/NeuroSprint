import pygame
import sys
import random
import sqlite3
import json
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF

# ====================== НАСТРОЙКИ ======================
DB_NAME = 'reaction_trainer.db'


def __init__(self):
    pygame.init()
    # ... остальное ...

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
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )''')
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
        print("✅ База данных успешно инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
    finally:
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


# ====================== КНОПКА ======================
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, 36)

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

    def get_username_input(self):
        username = ""
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RETURN and username.strip():
                        return username.strip()
                    elif e.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif len(username) < 20 and e.unicode.isprintable():
                        username += e.unicode

            self.screen.fill((20, 20, 40))
            self.screen.blit(self.med_font.render("Введите имя пользователя:", True, (255, 255, 255)), (250, 200))
            self.screen.blit(self.med_font.render(username + "_", True, (0, 255, 100)), (250, 280))
            pygame.display.flip()
            self.clock.tick(30)

    def run(self):
        self.username = self.get_username_input()
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

            # --- ITI (без крестика) ---
            iti = random.randint(600, 1100)
            start = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start < iti:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.screen.fill((20, 20, 40))
                pygame.display.flip()
                self.clock.tick(60)

            # --- СТИМУЛ ---
            stim_start = pygame.time.get_ticks()
            responded = False
            rt = None
            stim_rect = None

            while pygame.time.get_ticks() - stim_start < timeout_ms:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not responded:
                        if stim_rect and stim_rect.collidepoint(e.pos):
                            responded = True
                            rt = pygame.time.get_ticks() - stim_start

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

            correct = (is_go and responded) or (not is_go and not responded)
            results.append({'is_go': is_go, 'rt': rt, 'correct': correct})

            # обратная связь
            self.screen.fill((20, 20, 40))
            color = (0, 255, 100) if correct else (255, 80, 80)
            text = "ПРАВИЛЬНО!" if correct else "ОШИБКА!"
            self.screen.blit(self.big_font.render(text, True, color), (360, 300))
            pygame.display.flip()
            pygame.time.delay(400)

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
            self.screen.blit(self.med_font.render("История тренировок", True, (255, 255, 255)), (320, 40))

            if not sessions:
                txt = self.small_font.render("Пока нет сессий", True, (255, 200, 100))
                self.screen.blit(txt, (320, 300))
            else:
                y = 130
                for s in sessions[:8]:
                    line = f"{s['date'][:19]} | RT: {s['avg_rt']}мс | Acc: {s['accuracy']}%"
                    self.screen.blit(self.small_font.render(line, True, (200, 220, 255)), (80, y))
                    y += 45

            back = Button(380, 580, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back.draw(self.screen)

            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back.clicked(e.pos):
                    return
            pygame.display.flip()
            self.clock.tick(30)

    def show_progress_graph(self):
        sessions = get_user_sessions(self.user_id)
        if len(sessions) < 2:
            # placeholder
            while True:
                self.screen.fill((20, 20, 40))
                self.screen.blit(self.med_font.render("Недостаточно данных", True, (255, 200, 100)), (250, 300))
                back = Button(380, 520, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
                back.draw(self.screen)
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back.clicked(e.pos):
                        return
                pygame.display.flip()
                self.clock.tick(30)
            return

        # matplotlib график
        dates = [s['date'][:10] for s in sessions[::-1]]
        rts = [s['avg_rt'] for s in sessions[::-1]]
        plt.figure(figsize=(9, 5))
        plt.plot(dates, rts, marker='o', color='#00ff88', linewidth=3)
        plt.title('Прогресс скорости реакции')
        plt.xlabel('Дата')
        plt.ylabel('Среднее RT (мс)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('progress.png', facecolor='#141428')
        plt.close()

        graph = pygame.image.load('progress.png')
        graph = pygame.transform.scale(graph, (860, 480))

        while True:
            self.screen.fill((20, 20, 40))
            self.screen.blit(graph, (70, 90))
            back = Button(380, 600, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back.draw(self.screen)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back.clicked(e.pos):
                    return
            pygame.display.flip()
            self.clock.tick(30)

    def generate_pdf_report(self):
        print("generate_pdf_report вызвана")

        sessions = get_user_sessions(self.user_id)
        if not sessions:
            print("Нет сессий → отчёт не создаётся")
            # показ сообщения на экране (оставь как есть)
            # ...
            return

        print(f"Найдено сессий: {len(sessions)} → пытаемся создать PDF")

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Тестовый отчёт Go/No-Go", ln=1, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Пользователь: {self.username}", ln=1)
            pdf.cell(0, 10, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=1)

            filename = "reaction_report.pdf"
            pdf.output(filename)
            print(f"PDF успешно создан: {filename}")
            print("Полный путь:", os.path.abspath(filename))

            # показ на экране
            while True:
                self.screen.fill((20, 20, 40))
                self.screen.blit(self.med_font.render("PDF сохранён!", True, (0, 255, 120)), (350, 280))
                self.screen.blit(self.small_font.render(os.path.abspath(filename), True, (200, 200, 255)), (200, 350))
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

        except Exception as e:
            print("Ошибка при создании PDF:", str(e))
            # показ ошибки на экране
            while True:
                self.screen.fill((20, 20, 40))
                self.screen.blit(self.med_font.render("Ошибка создания PDF", True, (255, 80, 80)), (280, 280))
                self.screen.blit(self.small_font.render(str(e), True, (255, 200, 200)), (150, 350))
                back_btn = Button(380, 520, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
                back_btn.draw(self.screen)
                # обработка событий...
                pygame.display.flip()
                self.clock.tick(30)
        # простой лидерборд
        while True:
            self.screen.fill((20, 20, 40))
            self.screen.blit(self.med_font.render("Лидерборд (в разработке)", True, (255, 255, 255)), (280, 200))
            back = Button(380, 520, 240, 70, "Назад", (0, 120, 215), (0, 160, 255))
            back.draw(self.screen)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back.clicked(e.pos):
                    return
            pygame.display.flip()
            self.clock.tick(30)


if __name__ == "__main__":
    print("=== Go/No-Go Reaction Trainer запущен ===")
    print("Запускайте из терминала, чтобы видеть сообщения о сохранении!")
    app = ReactionTrainer()
    app.run()