import csv
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor
from add_window import AddWindow
from database import DBManager


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.db = DBManager()
        
        #Задаем 7 колонок
        self.bza_columns = 7
        self.baza.setEditTriggers(self.baza.EditTrigger.NoEditTriggers)
        self.baza.setColumnCount(self.bza_columns)
        
        self.baza.setHorizontalHeaderLabels(['ID', 'Название', 'Категория', 'Цена', 'Дата списания', 'Периодичность', 'Комментарий'])
        self.baza.setColumnHidden(0, True)
        
        self.bth_add.clicked.connect(self.bth_ad)
        self.bth_del.clicked.connect(self.bth_de)
        self.bth_chng.clicked.connect(self.bth_chn)
        self.bth_pay.clicked.connect(self.bth_py)
        self.btn_reset_filter.clicked.connect(self.reset_all_filters)

        self.action_help.triggered.connect(self.help_txt)
        self.action_clear_all.triggered.connect(self.clear_all_subs)
    
        self.action_export_csv.triggered.connect(self.export_to_csv)
    
        self.calendar.selectionChanged.connect(self.filter_cal)
        self.search_input.textChanged.connect(self.filter_search)
        self.bth_add.setShortcut("Ctrl+N")
        
        self.perenos_podpisok()
        self.load_data()

    def help_txt(self):
        try:
            with open("about.txt", "r", encoding="utf-8") as f:
                text_data = f.read()

            QMessageBox.information(self, "О программе и Справка", text_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл справки: {e}")

    def clear_all_subs(self):
        reply = QMessageBox.warning(
            self, 'Внимание!', 'Вы уверены, что хотите УДАЛИТЬ ВСЕ подписки из базы данных?\nЭто действие нельзя отменить!',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.db.clear_database():
                self.load_data()
                QMessageBox.information(self, "Успех", "База данных успешно очищена!")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось очистить базу данных.")

    def export_to_csv(self):
        subs = self.db.all_subs()
        if not subs:
            QMessageBox.warning(self, 'Внимание', 'Нет данных для экспорта отчета!')
            return

        try:
            with open('report.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Название подписки', 'Категория', 'Цена (руб.)', 'Дата списания', 'Периодичность', 'Комментарий'])
                
                for sub in subs:
                    writer.writerow([sub[1], sub[2], sub[3], sub[4], sub[5], sub[6]])
            
            QMessageBox.information(self, 
                                    'Успех!', 
                                    'Данные успешно экспортированы в report.csv!\nФайл можно открыть через Excel.')
        except Exception as e:
            QMessageBox.critical(self, 
                                'Ошибка', 
                                f'Не удалось сохранить CSV-отчет: {e}')

    def periyd(self, q_date, period):
        if period == 'раз в год':
            return q_date.addYears(1)
        elif period == 'раз в 6 месяцев':
            return q_date.addMonths(6)
        elif period == 'раз в 3 месяца':
            return q_date.addMonths(3)
        else:
            return q_date.addMonths(1)

    def load_data(self):
        subs = self.db.all_subs()
        self.display_sub(subs)

    def reset_all_filters(self):
        self.search_input.clear()                      
        self.calendar.setSelectedDate(QDate.currentDate()) 
        self.load_data()                               
        self.baza.sortByColumn(0, Qt.SortOrder.AscendingOrder) 

    def display_sub(self, subs):
        self.baza.setSortingEnabled(False)
        
        self.baza.setRowCount(0)
        self.baza.setRowCount(len(subs))
        self.baza.setColumnCount(self.bza_columns)

        total_sum = 0
        today = QDate.currentDate()
        current_ym = today.toString('yyyy-MM')

        for number, data in enumerate(subs):
            #id, na, ca, pr, da, per, com
            sub_price = float(data[3])
            sub_date_str = str(data[4])

            if sub_date_str.startswith(current_ym):
                total_sum += sub_price

            sub_date_qt = QDate.fromString(sub_date_str, 'yyyy-MM-dd')
            flag = False
            
            if sub_date_qt.isValid():
                days_to_pay = today.daysTo(sub_date_qt)
                if days_to_pay <= 2:
                    flag = True

            for n, v in enumerate(data):
                i = QTableWidgetItem(str(v))
                
                if flag:
                    i.setBackground(QColor(176, 0, 0, 40))
                    
                self.baza.setItem(number, n, i)

        self.baza.setColumnHidden(0, True)
        self.baza.setSortingEnabled(True)
        self.results.setText(f'К оплате в этом месяце: {total_sum:.2f} руб.')

    def filter_cal(self):
        selected_date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        all_subscriptions = self.db.all_subs()
        filtered_subs = []
        for sub in all_subscriptions:
            if str(sub[4]) == selected_date_str:
                filtered_subs.append(sub)
        self.display_sub(filtered_subs)

    def filter_search(self):
        search_text = self.search_input.text().lower()
        all_subs = self.db.all_subs()
        filtered = [sub for sub in all_subs if search_text in sub[1].lower()]
        self.display_sub(filtered)

    def perenos_podpisok(self):
        '''перенос подписок на периоды'''
        subs = self.db.all_subs()
        today = QDate.currentDate()

        for sub in subs:
            sub_id = sub[0]
            sub_date_str = str(sub[4])
            period = str(sub[5])
            
            q_date = QDate.fromString(sub_date_str, 'yyyy-MM-dd')

            if q_date.isValid() and q_date < today:
                while q_date < today:
                    q_date = self.periyd(q_date, period)

                new_date_str = q_date.toString('yyyy-MM-dd')
                self.db.update_date(sub_id, new_date_str)

    def bth_ad(self):
        self.new_win = AddWindow(self)
        self.new_win.show()

    def bth_de(self): 
        cur = self.baza.currentRow()
        
        if cur == -1:
            QMessageBox.warning(
                self, 
                'Внимание', 
                'Пожалуйста, выберите подписку в таблице для удаления!'
                )
            return

        sub_id = int(self.baza.item(cur, 0).text())
        sub_n = self.baza.item(cur, 1).text()

        res = QMessageBox.question(
            self, 
            'Подтверждение', 
            f'Вы уверены, что хотите удалить подписку "{sub_n}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if res == QMessageBox.StandardButton.Yes:
            if self.db.del_sub(sub_id):
                self.load_data()
            else:
                QMessageBox.critical(
                    self, 
                    'Ошибка',
                    'Не удалось удалить подписку из базы данных.'
                    )

    def bth_chn(self):
        current_row = self.baza.currentRow()
        if current_row == -1:
            QMessageBox.warning(
                self, 
                'Внимание', 
                'Выберите подписку в таблице для изменения!'
                )
            return

        sub_data = {
            'id': int(self.baza.item(current_row, 0).text()),
            'name': self.baza.item(current_row, 1).text(),
            'category': self.baza.item(current_row, 2).text(),
            'price': self.baza.item(current_row, 3).text(),
            'date': self.baza.item(current_row, 4).text(),
            'period': self.baza.item(current_row, 5).text(),
            'comment': self.baza.item(current_row, 6).text()
        }
        self.edit_win = AddWindow(self, sub_data=sub_data)
        self.edit_win.show()

    def bth_py(self):
        current_row = self.baza.currentRow()
        if current_row == -1:
            QMessageBox.warning(
                self, 
                'Внимание', 
                'Выберите подписку в таблице для оплаты!'
                )
            return

        sub_id = int(self.baza.item(current_row, 0).text())
        current_date_str = self.baza.item(current_row, 4).text()
        period = self.baza.item(current_row, 5).text()
        
        q_date = QDate.fromString(current_date_str, 'yyyy-MM-dd')
        next_month_date = self.periyd(q_date, period).toString('yyyy-MM-dd')

        if self.db.update_date(sub_id, next_month_date):
            self.load_data()
        else:
            QMessageBox.critical(
                self, 
                'Ошибка', 
                'Не удалось обновить дату списания.'
                )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Выход', 'Вы уверены, что хотите закрыть программу?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()