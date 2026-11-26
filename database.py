import sqlite3


class DBManager:
    def __init__(self):
        self.db_path = 'baza.sqlite'

    def add_subs(self, name, category_id, price, date, period, comment=''):
        '''Добавление новой подписки'''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = 'INSERT INTO subscription (name, category_id, price, data, period, comment) VALUES (?, ?, ?, ?, ?, ?)'

                cursor.execute(query, (name, category_id, price, date, period, comment))
                return True

        except sqlite3.Error as e:
            print(f"Ошибка добавления: {e}")
            return False

    def all_subs(self):
        '''Получение всех подписок'''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = '''
                    SELECT s.id, s.name, c.title, s.price, s.data, s.period, s.comment 
                    FROM subscription s
                    LEFT JOIN categorys c ON s.category_id = c.id
                '''

                cursor.execute(query)
                return cursor.fetchall()

        except sqlite3.Error as e:
            print(f'Ошибка чтения: {e}')
            return []

    def del_sub(self, sub_id):
        '''Удаление подписки'''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = 'DELETE FROM subscription WHERE id = ?'

                cursor.execute(query, (sub_id,))
                return True

        except sqlite3.Error as e:
            print(f'Ошибка удаления: {e}')
            return False

    def update_sub(self, sub_id, name, category_id, price, date, period, comment=""):
        '''Редактирование подписки'''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = '''
                    UPDATE subscription 
                    SET name = ?, category_id = ?, price = ?, data = ?, period = ?, comment = ?
                    WHERE id = ?'''

                cursor.execute(query, (name, category_id, price, date, period, comment, sub_id))
                return True

        except sqlite3.Error as e:
            print(f"Ошибка изменения: {e}")
            return False

    def update_date(self, sub_id, new_date):
        '''Перенос даты следующего списания'''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = 'UPDATE subscription SET data = ? WHERE id = ?'

                cursor.execute(query, (new_date, sub_id))
                return True

        except sqlite3.Error as e:
            print(f"Ошибка даты: {e}")
            return False

    def clear_database(self):
        '''Полное удаление всех подписок '''
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "DELETE FROM subscription"
                cursor.execute(query)
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при очистке базы: {e}")
            return False