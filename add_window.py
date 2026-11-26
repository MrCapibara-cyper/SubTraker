from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QPixmap
from database import DBManager


class AddWindow(QMainWindow):
    def __init__(self, parent=None, sub_data=None):
        super().__init__(parent)
        uic.loadUi('add_window.ui', self)

        self.main_window = parent
        self.sub_data = sub_data

        # Список категорий
        self.category_sub.addItems([
            'комуналка', 'кино', 'интернет', 'подписки'])

        self.period_sub.addItems([
            'раз в месяц', 
            'раз в 3 месяца', 
            'раз в 6 месяцев', 
            'раз в год'])

        self.db = DBManager()
        self.bth_add.clicked.connect(self.bth_ad)

        #добавление изображение
        pixmap = QPixmap('i.webp')
        self.cartinka.setPixmap(pixmap)
        self.cartinka.setScaledContents(True)

        if self.sub_data:
            self.setWindowTitle("Изменить подписку")
            self.bth_add.setText("Сохранить")

            # Подставляем значения
            self.name_sub.setText(self.sub_data['name'])
            self.category_sub.setCurrentText(self.sub_data['category'])
            self.price_sub.setValue(float(self.sub_data['price']))
            self.data_sub.setDate(QDate.fromString(self.sub_data['date'], "yyyy-MM-dd"))
            self.period_sub.setCurrentText(self.sub_data['period'])

    def bth_ad(self):
        '''Сбор данных'''
        name = self.name_sub.text().strip()
        category = self.category_sub.currentText()
        date = self.data_sub.date()
        price = self.price_sub.value()
        comment = self.comments.toPlainText().strip()
        period = self.period_sub.currentText()

        date_now = QDate.currentDate()

        # Проверка ввода
        if not name and date < date_now:
            self.name_date_warning()
            return
        elif not name:
            self.name_warning()
            return
        elif date < date_now:
            self.date_warning()
            return

        date_str = date.toString('yyyy-MM-dd')

        a = {
            'комуналка': 1,
            'кино': 2,
            'интернет': 3,
            'подписки': 4
        }

        #обнавляем или создаём подписку
        if self.sub_data:
            result = self.db.update_sub(
                sub_id=self.sub_data['id'],
                name=name,
                category_id=a[category],
                price=price,
                date=date_str,
                period=period,
                comment=comment
            )
        else:
            result = self.db.add_subs(
                name=name,
                category_id=a[category],
                price=price,
                date=date_str,
                period=period,
                comment=comment
            )

        if result:
            self.close()
        else:
            QMessageBox.critical(
                self,
                'Ошибка!',
                'Не удалось сохранить данные.'
            )

    def closeEvent(self, event):
        '''обновление таблицы при закрытии окна'''
        if self.main_window:
            self.main_window.load_data()
        event.accept()

    '''Методы вывода предупреждений'''

    def name_warning(self):
        '''название'''
        QMessageBox.warning(
            self,
            'Ошибка!',
            'Вы не внесли данные в название!\nНевозможно добавить подписку!'
        )

    def name_date_warning(self):
        '''название и дата'''
        QMessageBox.warning(
            self,
            'Ошибка!',
            'Некорректные данные!\nНевозможно добавить подписку!'
        )

    def date_warning(self):
        '''дата'''
        QMessageBox.warning(
            self,
            'Ошибка',
            'Некорректная дата!\nНевозможно добавить подписку!'
        )