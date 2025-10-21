"""
Inline клавиатуры для Telegram бота
"""
import telebot
from telebot import types
from typing import List, Tuple


def get_tasks_keyboard(tasks: List[Tuple[int, str, str, str]]) -> types.InlineKeyboardMarkup:
    """
    Создание inline клавиатуры со списком задач для удаления
    
    Args:
        tasks: Список задач в формате (id, text, user, created_at)
        
    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопками задач
    """
    keyboard = []
    
    # Добавляем кнопки для каждой задачи
    for task_id, text, user, created_at in tasks:
        # Обрезаем текст задачи если он слишком длинный
        display_text = text[:30] + "..." if len(text) > 30 else text
        button_text = f"ID {task_id:03d}: {display_text}"
        
        keyboard.append([
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"delete_task_{task_id}"
            )
        ])
    
    # Добавляем кнопку отмены
    keyboard.append([
        types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
    ])
    
    return types.InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard() -> types.InlineKeyboardMarkup:
    """
    Создание клавиатуры с кнопкой отмены
    
    Returns:
        types.InlineKeyboardMarkup: Клавиатура с кнопкой отмены
    """
    keyboard = [[
        types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_delete")
    ]]
    
    return types.InlineKeyboardMarkup(keyboard)
