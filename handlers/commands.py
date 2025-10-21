"""
Обработчики команд для Telegram бота
"""
import csv
import io
from datetime import datetime
import telebot
from telebot import types

from database.models import TaskManager
from keyboards.inline import get_tasks_keyboard, get_cancel_keyboard

# Создаем экземпляр менеджера задач
task_manager = TaskManager()

# Импортируем бота и хранилище из main.py
bot = None
storage = None

def init_bot(bot_instance, storage_instance):
    """Инициализация бота и хранилища"""
    global bot, storage
    bot = bot_instance
    storage = storage_instance


class TaskStates:
    """Состояния для FSM (Finite State Machine)"""
    waiting_for_task_text = "waiting_for_task_text"
    waiting_for_task_id = "waiting_for_task_id"


def cmd_start(message):
    """
    Обработчик команды /start
    Приветствует пользователя и показывает доступные команды
    """
    welcome_text = """
🤖 Добро пожаловать в бот для управления задачами!

Доступные команды:
• /add - добавить новую задачу
• /list - показать все задачи
• /list_csv - скачать список задач в CSV формате
• /del - удалить задачу

Для начала работы выберите команду из меню или введите её вручную.
    """
    
    bot.reply_to(message, welcome_text)


def cmd_add(message):
    """
    Обработчик команды /add
    Запрашивает текст задачи у пользователя
    """
    storage.set_state(message.from_user.id, message.from_user.id, TaskStates.waiting_for_task_text)
    bot.reply_to(
        message,
        "📝 Введите текст задачи:",
        reply_markup=get_cancel_keyboard()
    )


def process_task_text(message):
    """
    Обработка введенного текста задачи
    """
    task_text = message.text.strip()
    
    # Проверяем, что текст не пустой
    if not task_text:
        bot.reply_to(message, "❌ Текст задачи не может быть пустым. Попробуйте еще раз:")
        return
    
    # Проверяем длину текста
    if len(task_text) > 500:
        bot.reply_to(message, "❌ Текст задачи слишком длинный (максимум 500 символов). Попробуйте еще раз:")
        return
    
    # Получаем информацию о пользователе
    user_name = message.from_user.full_name or message.from_user.username or "Неизвестный"
    
    # Добавляем задачу в базу данных
    if task_manager.add_task(task_text, user_name):
        bot.reply_to(message, "✅ Задача успешно добавлена!")
    else:
        bot.reply_to(message, "❌ Ошибка при добавлении задачи. Попробуйте позже.")
    
    # Сбрасываем состояние
    storage.set_state(message.from_user.id, message.from_user.id, None)


def cmd_list(message):
    """
    Обработчик команды /list
    Показывает все задачи в красивом формате
    """
    tasks = task_manager.get_all_tasks()
    
    if not tasks:
        bot.reply_to(message, "📋 Список задач пуст.")
        return
    
    # Формируем красивый список задач
    tasks_text = "📋 Список всех задач:\n\n"
    
    for task_id, text, user, created_at in tasks:
        # Парсим дату и время
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_date = created_at
        
        # Форматируем ID как трехзначный номер
        formatted_id = f"{task_id:03d}"
        
        tasks_text += f"🆔 ID: {formatted_id}\n"
        tasks_text += f"👤 Автор: {user}\n"
        tasks_text += f"📅 Создано: {formatted_date}\n"
        tasks_text += f"📝 Задача: {text}\n"
        tasks_text += "─" * 30 + "\n\n"
    
    # Если текст слишком длинный, разбиваем на части
    if len(tasks_text) > 4000:
        # Разбиваем на части по 4000 символов
        parts = []
        current_part = ""
        lines = tasks_text.split('\n')
        
        for line in lines:
            if len(current_part + line + '\n') > 4000:
                parts.append(current_part)
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        for i, part in enumerate(parts):
            if i == 0:
                bot.reply_to(message, part)
            else:
                bot.send_message(message.chat.id, part)
    else:
        bot.reply_to(message, tasks_text)


def cmd_list_csv(message):
    """
    Обработчик команды /list_csv
    Отправляет CSV файл со списком задач
    """
    tasks = task_manager.get_all_tasks()
    
    if not tasks:
        bot.reply_to(message, "📋 Список задач пуст.")
        return
    
    # Создаем CSV файл в памяти
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer, delimiter='\t')  # Используем табуляцию как разделитель
    
    # Записываем заголовки
    writer.writerow(['ID', 'Текст задачи', 'Автор', 'Дата создания'])
    
    # Записываем данные
    for task_id, text, user, created_at in tasks:
        # Форматируем дату
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_date = created_at
        
        writer.writerow([task_id, text, user, formatted_date])
    
    # Получаем содержимое файла
    csv_content = csv_buffer.getvalue()
    csv_buffer.close()
    
    # Создаем файл для отправки
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    csv_file.name = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    bot.send_document(
        message.chat.id,
        document=csv_file,
        caption="📊 Список задач в формате CSV"
    )


def cmd_delete(message):
    """
    Обработчик команды /del
    Показывает список задач для удаления
    """
    tasks = task_manager.get_all_tasks()
    
    if not tasks:
        bot.reply_to(message, "📋 Список задач пуст. Нечего удалять.")
        return
    
    bot.reply_to(
        message,
        "🗑️ Выберите задачу для удаления:",
        reply_markup=get_tasks_keyboard(tasks)
    )


def process_delete_task(callback):
    """
    Обработка удаления задачи
    """
    # Извлекаем ID задачи из callback_data
    task_id = int(callback.data.split("_")[-1])
    
    # Получаем информацию о задаче
    task = task_manager.get_task_by_id(task_id)
    
    if not task:
        bot.answer_callback_query(callback.id, "❌ Задача не найдена!")
        return
    
    # Удаляем задачу
    if task_manager.delete_task(task_id):
        bot.edit_message_text("✅ Задача успешно удалена!", callback.message.chat.id, callback.message.message_id)
    else:
        bot.edit_message_text("❌ Ошибка при удалении задачи.", callback.message.chat.id, callback.message.message_id)
    
    bot.answer_callback_query(callback.id)


def process_cancel_delete(callback):
    """
    Обработка отмены удаления
    """
    bot.edit_message_text("❌ Операция отменена.", callback.message.chat.id, callback.message.message_id)
    storage.set_state(callback.from_user.id, callback.from_user.id, None)
    bot.answer_callback_query(callback.id)
