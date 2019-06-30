from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import mysql.connector
import datetime
from xlsxwriter import *

from PyQt5.uic import loadUiType

ui, _ = loadUiType('library.ui')
login, _ = loadUiType('login.ui')


class Login(QWidget, login):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.handle_login)

    def handle_login(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        un = self.lineEdit.text()
        pas = self.lineEdit_2.text()
        sql = '''SELECT * FROM admin'''
        mycursor.execute(sql)
        data = mycursor.fetchall()
        for row in data:
            if un == row[2] and pas == row[3]:
                print('User Match')
                self.window2 = MainApp()
                self.close()
                self.window2.show()
            else:
                self.label.setText('Make Sure You Have Entered Your Username And Password Correctly')

class MainApp(QMainWindow, ui):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handle_UI_Changes()
        self.Handle_Buttons()
        self.show_data()
        self.fill_Date()

    def Handle_UI_Changes(self):
        self.tabWidget.tabBar().setVisible(False)

    def Handle_Buttons(self):
        self.pushButton.clicked.connect(self.open_home)
        self.pushButton_2.clicked.connect(self.open_books)
        self.pushButton_3.clicked.connect(self.open_settings)
        self.pushButton_4.clicked.connect(self.Search_books)
        self.pushButton_5.clicked.connect(self.issue_book)
        self.pushButton_5.clicked.connect(self.show_user_data)
        self.pushButton_6.clicked.connect(self.Add_New_Book)
        self.pushButton_7.clicked.connect(self.Refresh)
        self.pushButton_8.clicked.connect(self.export_books)
        self.pushButton_9.clicked.connect(self.delete_books)
        self.pushButton_10.clicked.connect(self.show_user_data)
        self.pushButton_11.clicked.connect(self.enable_edit)
        self.pushButton_12.clicked.connect(self.return_book)
        self.pushButton_13.clicked.connect(self.export_users)

    def open_home(self):
        self.tabWidget.setCurrentIndex(0)

    def open_books(self):
        self.tabWidget.setCurrentIndex(1)

    def open_settings(self):
        self.tabWidget.setCurrentIndex(2)

    def Add_New_Book(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        book_title = self.lineEdit_5.text()
        book_code = self.lineEdit_6.text()
        book_category = self.lineEdit_10.text()
        book_author = self.lineEdit_8.text()
        book_publisher = self.lineEdit_9.text()
        book_price = self.lineEdit_7.text()
        book_count = self.lineEdit_12.text()
        if book_title != "" and book_code != "" and book_category != "" and book_author != "" and book_publisher != "" \
                and book_price != "" and book_count != "":
            try:
                int(book_code) and int(book_price)
                add_user = '''INSERT INTO book(book_name, book_code, book_category, book_author, book_publisher, 
                book_price, book_count, max_count) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) '''
                data_user = (book_title, book_code, book_category, book_author, book_publisher, book_price, book_count,
                             book_count)
                mycursor.execute(add_user, data_user)
                mydb.commit()
                self.statusBar().showMessage('Book Added')
                self.lineEdit_5.setText('')
                self.lineEdit_6.setText('')
                self.lineEdit_10.setText('')
                self.lineEdit_8.setText('')
                self.lineEdit_9.setText('')
                self.lineEdit_7.setText('')
                self.lineEdit_12.setText('')
            except ValueError:
                QMessageBox.warning(self, 'Data Incorrect', "Code and Price should be in Numeric", QMessageBox.Ok |
                                    QMessageBox.Cancel)
        else:
            QMessageBox.warning(self, 'Data Missing', "Fill all details first", QMessageBox.Ok | QMessageBox.Cancel)
        self.show_data()

    def delete_books(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        book_name = self.lineEdit_5.text()
        sql = ''' DELETE FROM book WHERE book_name = %s'''
        mycursor.execute(sql, [book_name])
        mydb.commit()
        self.statusBar().showMessage('Book Deleted')
        self.show_data()

    def issue_book(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        book_code = self.lineEdit_2.text()
        user_name = self.lineEdit_3.text()
        dat = (user_name, book_code)
        if book_code != "" and user_name != "":
            check = 'SELECT book_count,book_name from book WHERE book_code = %s'
            mycursor.execute(check, [book_code])
            data = mycursor.fetchone()
            print(data)
            value = int(data[0])
            print(value)
            title = data[1]
            print(title)
            today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(today)
            if value > 0:
                update_count = '''UPDATE book SET book_count=GREATEST(0, book_count - 1) WHERE book_code = %s '''
                mycursor.execute(update_count, [book_code])
                print("-- Update done")
                assign_book = 'INSERT INTO issued_book(Username, Book_Title, Book_Code, Date) VALUES(%s, %s, %s, %s)'
                data_user = (user_name, title, book_code, today)
                mycursor.execute(assign_book, data_user)
                print("-- Insert done")
                date_query = '''SELECT Date from issued_book WHERE Username = %s AND  Book_Code = %s'''
                mycursor.execute(date_query, dat)
                date_fetch = mycursor.fetchall()
                date1 = date_fetch[0]
                print(date1)
                d1 = date1[0]
                print("d1:", d1)
                #a = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
                #print(a)
                #d1 = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
                #print(d1)
                print("date done")
                diff = d1 + datetime.timedelta(days=15)
                print("diff:", diff.strftime('%d-%b'))
                self.label_5.setText('Return this book before: ' + diff.strftime('%d-%b'))
                mydb.commit()
                self.statusBar().showMessage('Book Issued')
            else:
                print('data incorrect')
                QMessageBox.warning(self, 'Issue Error', "Book not available", QMessageBox.Ok | QMessageBox.Cancel)
            self.show_data()
        else:
            QMessageBox.warning(self, 'Data Missing', "Fill all details first", QMessageBox.Ok | QMessageBox.Cancel)

    def return_book(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        book_code = self.lineEdit_2.text()
        user_name = self.lineEdit_3.text()
        dat = (user_name, book_code)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if book_code != "" and user_name != "":
            check = 'SELECT * FROM issued_book WHERE Username = %s AND  Book_Code = %s'
            mycursor.execute(check, dat)
            data = mycursor.fetchall()
            print(data)
            if not data:
                QMessageBox.warning(self, 'Data Missing', "Book not found", QMessageBox.Ok | QMessageBox.Cancel)
            else:
                date_query = '''SELECT Date from issued_book WHERE Username = %s AND  Book_Code = %s'''
                mycursor.execute(date_query, dat)
                date_fetch = mycursor.fetchall()
                date1 = date_fetch[0]
                print(date1)
                d1 = date1[0]
                print("d1:", d1)
                print("today:", today)
                dele_bk = 'DELETE from issued_book WHERE Username = %s AND  Book_Code = %s'
                mycursor.execute(dele_bk, dat)
                print("Delete Book Done")
                update_count = 'UPDATE book SET book_count= book_count + 1 WHERE book_code= %s '
                mycursor.execute(update_count, [book_code])
                print("Update Book Done")
                diff = d1 + datetime.timedelta(days=15)
                dc = diff.strftime('%Y-%m-%d')
                print("diff:", dc)
                today1 = datetime.datetime.today()
                print("today1:", today1.strftime('%Y-%m-%d'))
                delta = today1 - diff
                print(delta.days)
                #mydb.commit()
                if delta.days > 0:
                    fine = delta.days*5
                    print(fine)
                    QMessageBox.warning(self, 'Book Return', user_name+" have to Pay fine of ₹"+str(fine),
                                        QMessageBox.Ok | QMessageBox.Cancel)
                else:
                    print('Book Returned')
                    self.label_5.setText('Book Returned Successfully')
                mydb.commit()
                # today1 = datetime.datetime.now().strftime('%Y-%m-%d')
                # print("today1:", today1)
                # day = dc - today1
                # print(day)

                # fine = diff - today
                # print(fine.days)
                # res = abs((today - diff).days)
                # format(res)
                # print(res)
                # diff_object = datetime.strptime(diff, '%Y-%m-%d')
                # today_object = datetime.strptime(today, '%Y-%m-%d')
                # print(today_object-diff_object)
                # datetimeFormat = '%Y-%m-%d'
                # diffs = datetime.datetime.strptime(today, datetimeFormat) - datetime.datetime.strptime(diff,
                #                                                                                        datetimeFormat)
                # print("Days:", diffs.days)
        else:
            QMessageBox.warning(self, 'Data Missing', "Fill all details first", QMessageBox.Ok | QMessageBox.Cancel)


    def fill_Date(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        fill = '''UPDATE issued_book SET Today = now()'''
        mycursor.execute(fill)
        mydb.commit()

    def show_data(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        add_user = '''SELECT book_name, book_code, book_category, book_author, book_publisher, book_price, book_count 
        FROM book'''
        mycursor.execute(add_user)
        data = mycursor.fetchall()
        self.tableWidget.setRowCount(0)
        self.tableWidget.insertRow(0)
        for row, form in enumerate(data):
            for column, item in enumerate(form):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))
                column += 1
                row_position = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)

    def show_user_data(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        user = self.lineEdit_3.text()
        add_user = '''SELECT Book_Title, Book_Code, Date FROM issued_book where username = %s'''
        mycursor.execute(add_user, [user])
        data = mycursor.fetchall()
        print(data)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.insertRow(0)
        for row, form in enumerate(data):
            for column, item in enumerate(form):
                self.tableWidget_2.setItem(row, column, QTableWidgetItem(str(item)))
                column += 1
                row_position = self.tableWidget_2.rowCount()
                self.tableWidget_2.insertRow(row_position)

    def Search_books(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        book_title = self.lineEdit.text()
        sql = '''SELECT book_name, book_code, book_category, book_author, book_publisher, book_price, book_count from 
        book WHERE book_name = %s'''
        mycursor.execute(sql, [book_title])
        data = mycursor.fetchall()
        self.tableWidget.setRowCount(0)
        self.tableWidget.insertRow(0)
        for row, form in enumerate(data):
            for column, item in enumerate(form):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(item)))
                column += 1
                row_position = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)

    def Refresh(self):
        self.show_data()

    def enable_edit(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        un = self.lineEdit_11.text()
        pas = self.lineEdit_4.text()
        sql = '''SELECT * FROM admin'''
        mycursor.execute(sql)
        data = mycursor.fetchall()
        for row in data:
            if un == row[2] and pas == row[3]:
                print('User Match')
                self.statusBar().showMessage('Welcome Admin')
                self.pushButton_6.setEnabled(True)
                self.pushButton_9.setEnabled(True)
                self.pushButton_8.setEnabled(True)
                self.pushButton_13.setEnabled(True)
                break
            else:
                self.statusBar().showMessage('Make Sure You Have Entered Your Username And Password Correctly')

    def export_books(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        sql = '''SELECT book_name, book_code, book_publisher, book_category, book_author, book_price, book_count from
         book '''
        mycursor.execute(sql)
        data = mycursor.fetchall()
        wb = Workbook('BooksReport.xlsx')
        sheet1 = wb.add_worksheet()
        sheet1.write(0, 0, 'Book Title')
        sheet1.write(0, 1, 'Book Code')
        sheet1.write(0, 2, 'Book Publisher')
        sheet1.write(0, 3, 'Book Category')
        sheet1.write(0, 4, 'Book Author')
        sheet1.write(0, 5, 'Book Price')
        sheet1.write(0, 6, 'Book Count')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

        wb.close()
        self.statusBar().showMessage('Book Exported')

    def export_users(self):
        mydb = mysql.connector.connect(host="localhost", user="root", password="afif123", db="library")
        mycursor = mydb.cursor()
        sql = '''SELECT Username, Book_Title, Book_Code, Date FROM issued_book '''
        mycursor.execute(sql)
        data = mycursor.fetchall()
        wb = Workbook('UsersReport.xlsx')
        sheet1 = wb.add_worksheet()
        sheet1.write(0, 0, 'Username')
        sheet1.write(0, 1, 'Book Title')
        sheet1.write(0, 2, 'Book Code')
        sheet1.write(0, 3, 'Issued Date')

        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                sheet1.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1
        wb.close()
        self.statusBar().showMessage('Users Exported')

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
