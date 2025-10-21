"""
Модели данных для работы с базой данных
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
from config.settings import DATABASE_PATH


class TaskManager:
    """
    Класс для управления задачами в базе данных SQLite
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Инициализация менеджера задач
        
        Args:
            db_path (str): Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """
        Создание таблицы tasks, если она не существует
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT NOT NULL,
                        user TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы: {e}")
    
    def add_task(self, text: str, user: str) -> bool:
        """
        Добавление новой задачи
        
        Args:
            text (str): Текст задачи
            user (str): Имя пользователя
            
        Returns:
            bool: True если задача добавлена успешно, False в противном случае
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (text, user) VALUES (?, ?)",
                    (text, user)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении задачи: {e}")
            return False
    
    def get_all_tasks(self) -> List[Tuple[int, str, str, str]]:
        """
        Получение всех задач из базы данных
        
        Returns:
            List[Tuple[int, str, str, str]]: Список кортежей (id, text, user, created_at)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, text, user, created_at FROM tasks ORDER BY created_at DESC")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении задач: {e}")
            return []
    
    def get_task_by_id(self, task_id: int) -> Optional[Tuple[int, str, str, str]]:
        """
        Получение задачи по ID
        
        Args:
            task_id (int): ID задачи
            
        Returns:
            Optional[Tuple[int, str, str, str]]: Кортеж с данными задачи или None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, text, user, created_at FROM tasks WHERE id = ?", (task_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при получении задачи по ID: {e}")
            return None
    
    def delete_task(self, task_id: int) -> bool:
        """
        Удаление задачи по ID
        
        Args:
            task_id (int): ID задачи для удаления
            
        Returns:
            bool: True если задача удалена успешно, False в противном случае
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении задачи: {e}")
            return False
    
    def get_tasks_count(self) -> int:
        """
        Получение количества задач в базе данных
        
        Returns:
            int: Количество задач
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tasks")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при подсчете задач: {e}")
            return 0
