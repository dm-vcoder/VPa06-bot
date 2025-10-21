"""
Главный файл для запуска Telegram бота
"""
import logging
import telebot
from telebot import types
from telebot.storage import StateMemoryStorage

from config.settings import BOT_TOKEN
from handlers.commands import (
    cmd_start, cmd_add, cmd_list, cmd_list_csv, cmd_delete,
    process_task_text, process_delete_task, process_cancel_delete
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Создаем хранилище состояний
storage = StateMemoryStorage()


def register_handlers():
    """
    Регистрируем обработчики команд и сообщений
    """
    # Инициализируем бота и хранилище в handlers
    from handlers.commands import init_bot
    init_bot(bot, storage)
    
    # Регистрируем обработчики состояний ПЕРВЫМИ
    from handlers.commands import TaskStates
    bot.message_handler(func=lambda message: storage.get_state(message.from_user.id, message.from_user.id) == TaskStates.waiting_for_task_text)(process_task_text)
    
    # Регистрируем команды
    bot.message_handler(commands=['start'])(cmd_start)
    bot.message_handler(commands=['add'])(cmd_add)
    bot.message_handler(commands=['list'])(cmd_list)
    bot.message_handler(commands=['list_csv'])(cmd_list_csv)
    bot.message_handler(commands=['del'])(cmd_delete)
    
    # Регистрируем callback обработчики
    bot.callback_query_handler(func=lambda call: call.data.startswith("delete_task_"))(process_delete_task)
    bot.callback_query_handler(func=lambda call: call.data == "cancel_delete")(process_cancel_delete)


if __name__ == "__main__":
    try:
        # Регистрируем обработчики
        register_handlers()
        
        logger.info("Бот запущен!")
        
        # Запускаем бота с обработкой ошибок
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
