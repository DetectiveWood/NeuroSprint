import matplotlib
matplotlib.use('Agg')  # Важно для PyInstaller
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os
import sys

class ReactionReportGenerator:
    def __init__(self, output_filename="reaction_report.pdf"):
        self.output_filename = output_filename
        self.setup_fonts()  # Регистрируем шрифты с поддержкой кириллицы
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_fonts(self):
        """Регистрация шрифтов с поддержкой кириллицы"""
        try:
            # Используем стандартный шрифт ReportLab, который поддерживает кириллицу
            # Вместо поиска системных шрифтов, используем встроенный
            self.use_cyrillic = False
            
            # Пробуем зарегистрировать шрифт с кириллицей
            font_paths = [
                # Windows
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/times.ttf",
                # Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                # MacOS
                "/Library/Fonts/Arial.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('CyrillicFont', font_path))
                    pdfmetrics.registerFont(TTFont('CyrillicFont-Bold', font_path))
                    self.use_cyrillic = True
                    print(f"Загружен шрифт: {font_path}")
                    break
                    
        except Exception as e:
            print(f"Шрифт с кириллицей не найден, используется стандартный: {e}")
            self.use_cyrillic = False
        
    def setup_custom_styles(self):
        """Настройка пользовательских стилей с русскими шрифтами"""
        
        # Определяем, какой шрифт использовать
        if self.use_cyrillic:
            normal_font = 'CyrillicFont'
            bold_font = 'CyrillicFont-Bold'
        else:
            normal_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
        
        # Заголовок
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=bold_font,
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # Подзаголовок
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=bold_font,
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            alignment=TA_CENTER,  # Центрируем заголовки
            spaceAfter=20
        ))
        
        # Обычный текст (центрированный)
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontName=normal_font,
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,  # Центрируем обычный текст
            spaceAfter=10
        ))
        
        # Обычный текст с выравниванием влево (для особых случаев)
        self.styles.add(ParagraphStyle(
            name='CustomNormalLeft',
            parent=self.styles['Normal'],
            fontName=normal_font,
            fontSize=11,
            textColor=colors.HexColor("#000000"),
            alignment=TA_LEFT,
            spaceAfter=10
        ))
        
        # Статистика (большой текст)
        self.styles.add(ParagraphStyle(
            name='StatValue',
            parent=self.styles['Normal'],
            fontName=bold_font,
            fontSize=18,
            textColor=colors.HexColor('#2980B9'),
            alignment=TA_CENTER
        ))
        
        # Метка для статистики
        self.styles.add(ParagraphStyle(
            name='StatLabel',
            parent=self.styles['Normal'],
            fontName=normal_font,
            fontSize=18,
            textColor=colors.HexColor("#000000"),
            alignment=TA_CENTER
        ))

    def create_progress_chart(self, dates, values):
        """Создание графика прогресса с русскими подписями"""
        plt.figure(figsize=(8, 4))
        
        # Настройка русских шрифтов для matplotlib
        if self.use_cyrillic:
            plt.rcParams['font.family'] = 'DejaVu Sans'  # Поддерживает кириллицу
        
        # Стилизация графика
        plt.plot(dates, values, marker='o', linewidth=2, markersize=8, 
                color='#2E5A9C', markerfacecolor='#1A3A6B', markeredgecolor='white')
        #3498DB
        # Настройка внешнего вида с русскими подписями
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xlabel('Попытка', fontsize=10, color='#2C3E50')
        plt.ylabel('Время реакции (мс)', fontsize=10, color='#2C3E50')
        plt.title('Прогресс времени реакции', fontsize=12, color='#2C3E50', pad=15)
        
        # Форматирование дат
        plt.gcf().autofmt_xdate()
        
        # Добавление значений на график
        for i, (date, value) in enumerate(zip(dates, values)):
            plt.annotate(f'{value} ', (date, value), 
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=8, color="#000000")
        
        # Сохранение в байтовый поток
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        img_data.seek(0)
        return img_data
    
    def create_mistakes_chart(self, dates, values):
        """Создание графика прогресса с русскими подписями"""
        plt.figure(figsize=(8, 4))
        
        # Настройка русских шрифтов для matplotlib
        if self.use_cyrillic:
            plt.rcParams['font.family'] = 'DejaVu Sans'  # Поддерживает кириллицу
        
        # Стилизация графика
        plt.plot(dates, values, marker='o', linewidth=2, markersize=8, 
                color="#B44A4A", markerfacecolor="#7A2E2E", markeredgecolor='white')
        
        # Настройка внешнего вида с русскими подписями
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.xlabel('Попытка', fontsize=10, color='#2C3E50')
        plt.ylabel('Количество ошибок', fontsize=10, color='#2C3E50')
        plt.title('Прогресс точности действий', fontsize=12, color='#2C3E50', pad=15)
        
        # Форматирование дат
        plt.gcf().autofmt_xdate()
        
        # Добавление значений на график
        for i, (date, value) in enumerate(zip(dates, values)):
            plt.annotate(f'{value}', (date, value), 
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=8, color="#000000")
        
        # Сохранение в байтовый поток
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        img_data.seek(0)
        return img_data

    def generate_report(self, user_data):
        """
        Генерация отчета с поддержкой русского языка
        """
        # Создание PDF документа
        doc = SimpleDocTemplate(
            self.output_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )
        
        # Контейнер для элементов
        story = []
        
        # Заголовок
        title = Paragraph("Go/No-Go Тренажёр — Отчёт", self.styles['CustomTitle'])
        story.append(title)
        
        # Информация о пользователе (центрированная)
        user_info = f"""
        <para align="center">
            <b>Пользователь:</b> {user_data['user_id']} | 
            <b>Дата отчёта:</b> {user_data['report_date']} | 
            <b>Всего тренировок:</b> {user_data['total_sessions']}
        </para>
        """
        story.append(Paragraph(user_info, self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Сводка по всем сессиям
        story.append(Paragraph("Общая статистика", self.styles['CustomHeading']))
        
        # Создание центрированной таблицы со статистикой
        stats_data = []
        stats_pairs = [
            ("Среднее время реакции", f"{user_data['avg_reaction']} мс"),
            ("Точность", f"{user_data['avg_accuracy']}%"),
            ("Пропуски", f"{user_data['avg_misses']}"),
            ("Ложные нажатия", f"{user_data['avg_false_presses']}"),
            ("Вариабельность", f"{user_data['avg_variability']} мс"),
            ("Изменение RT", f"{user_data['reaction_change']}%")
        ]
        
        for label, value in stats_pairs:
            stats_data.append([
                Paragraph(label, self.styles['StatLabel']),
                Paragraph(value, self.styles['StatValue'])
            ])
        
        # Центрируем таблицу на странице
        # Рассчитываем ширину таблицы и отступы
        table_width = 6 * inch  # Общая ширина таблицы
        left_margin = (doc.width - table_width) / 2
        
        # Создаем таблицу с центрированием
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Центрируем содержимое ячеек
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ECF0F1')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#000000")),
            ('FONTNAME', (0, 0), (-1, -1), 'CyrillicFont' if self.use_cyrillic else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        # Оборачиваем таблицу в KeepTogether и добавляем отступы для центрирования
        story.append(Spacer(1, 10))
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # Последняя сессия
        story.append(Paragraph("Последняя сессия", self.styles['CustomHeading']))
        
        last_session = user_data['last_session']
        
        # Создаем центрированную информацию о последней сессии
        session_info_data = [
            ["Дата", last_session['date']],
            ["Среднее время реакции", f"{last_session['reaction']} мс"],
            ["Точность", f"{last_session['accuracy']}%"],
            ["Пропуски", str(last_session['misses'])],
            ["Ложные нажатия", str(last_session['false_presses'])],
            ["Вариабельность", f"{last_session['variability']} мс"]
        ]
        
        session_table = Table(session_info_data, colWidths=[3*inch, 2*inch])
        session_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Выравнивание меток вправо
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),   # Выравнивание значений влево
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ECF0F1')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('FONTNAME', (0, 0), (-1, -1), 'CyrillicFont' if self.use_cyrillic else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#000000")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(session_table)
        story.append(Spacer(1, 30))
        
        # График прогресса
        if user_data['progress_data']['dates']:
            
            # Создание графика
            chart_img = self.create_progress_chart(
                user_data['progress_data']['dates'],
                user_data['progress_data']['values']
            )
            
            # Добавление графика в PDF с центрированием
            img = Image(chart_img, width=6*inch, height=3*inch)
            img.hAlign = 'CENTER'  # Центрируем изображение
            story.append(img)
        # График прогресса
        if user_data['progress_data']['dates']:
            
            # Создание графика
            chart_img = self.create_mistakes_chart(
                user_data['mistake_data']['dates'],
                user_data['mistake_data']['values']
            )
            
            # Добавление графика в PDF с центрированием
            img = Image(chart_img, width=6*inch, height=3*inch)
            img.hAlign = 'CENTER'  # Центрируем изображение
            story.append(img)
        
        # Добавляем информацию о генерации отчета внизу страницы
        story.append(Spacer(1, 30))
        footer_text = f"""
        <para align="center">
            <font size="8" color="#95A5A6">
                Отчет сгенерирован автоматически {datetime.now().strftime('%d.%m.%Y %H:%M')}
            </font>
        </para>
        """
        story.append(Paragraph(footer_text, self.styles['CustomNormal']))
        
        # Построение PDF
        doc.build(story)
        print(f"Отчет успешно создан: {self.output_filename}")

# Пример использования
if __name__ == "__main__":
    user_data = {
        'user_id': '67',
        'report_date': '28.02.2026 19:06',
        'total_sessions': 2,
        'avg_reaction': 292.2,
        'avg_accuracy': 65.8,
        'avg_misses': 20.5,
        'avg_false_presses': 0.0,
        'avg_variability': 40.7,
        'reaction_change': '+2.7',
        'last_session': {
            'date': '2026-02-28 12:19:42',
            'reaction': 288.2,
            'accuracy': 31.7,
            'misses': 41,
            'false_presses': 0,
            'variability': 19.1
        },
        'progress_data': {
            'dates': ['1', '2'],
            'values': [288.2, 281.2]
        },
        'mistake_data': {
            'dates': ['1', '2'],
            'values': [288.2, 281.2]
        }
    }
    
    generator = ReactionReportGenerator("reaction_report_improved.pdf")
    generator.generate_report(user_data)