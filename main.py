#!/usr/bin/python3

import sys
import random
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget,
        QPushButton, QLineEdit, QInputDialog, QDialog, QDialogButtonBox,
        QFormLayout, QLabel, QSpinBox, QTreeView, QVBoxLayout, QHBoxLayout, QFileDialog, QScrollArea, QListWidgetItem, QScrollBar, QListWidget)

from PyQt5 import QtCore
from PyQt5.QtGui import (QImage, QPalette, QPixmap, QIcon)

import myDatabase
from myDatabase import Msg


class Message(QWidget):
    def __init__(self, msg, small=False, parent=None):
        super().__init__(parent=parent)
        self.small = small
        self.msg = msg
        layout = QFormLayout()
        super().setLayout(layout)
        
        self.setAutoFillBackground(True)

        self.change_bg(False)
        self.pixmap = QPixmap(self.msg.avatar)
        self.pixmap = self.pixmap.scaled(QtCore.QSize(40, 40), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

        def add_author_date(msg):
            l = QHBoxLayout()
            label = QLabel()
            title = QLabel('  ' + msg.date.toString())
            label.setPixmap(self.pixmap)
            label.setAlignment(QtCore.Qt.AlignCenter)
            title.setMinimumHeight(self.pixmap.height())
            title.setAlignment(QtCore.Qt.AlignCenter)
            l.addWidget(label)
            l.addWidget(title)
            l.setSpacing(0)
            l.addStretch()
            return l

        if msg.is_text():
            label = QLabel(msg.text)
            label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            layout.addRow(label, add_author_date(msg))

        elif msg.is_img():
            img = QLabel()
            pixmap = QPixmap(msg.img).scaledToHeight(300)
            if self.small:
                pixmap = pixmap.scaledToHeight(300)
            img.setPixmap(pixmap)
            layout.addRow(img, add_author_date(msg))

        if msg.replay != None:
            m = Message(msg.replay)
            layout.addRow('', m)


    doubleClicked = QtCore.pyqtSignal()
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


    def change_bg(self, clicked):
        p = QPalette()
        if clicked:
            p.setColor(QPalette.Background, QtCore.Qt.gray)
        else:
            p.setColor(QPalette.Background, QtCore.Qt.white)
        self.setPalette(p)


class Dialog(QWidget):
    def __init__(self, msg, author, d_id=None, d_acc_id = None, parent=None):
        super().__init__(parent=parent)
        self.msg = Message(msg = msg.msg, small = True)
        self.d_id = d_id
        self.d_acc_id = d_acc_id
        self.author = author
        layout = QHBoxLayout()
        super().setLayout(layout)
        author_label = QLabel(author)
        layout.addWidget(author_label)
        layout.addWidget(self.msg)

    doubleClicked = QtCore.pyqtSignal()
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class myDialog(QScrollArea):
    def __init__(self, msgs, title = "question", d_id = None, parent = None, d_acc_id = None):
        self.d_id = d_id
        self.d_acc_id = d_acc_id
        super(myDialog, self).__init__()
        widget = QWidget()
        self.setWindowTitle(title)
        layout = QVBoxLayout(widget)
        layout.setAlignment(QtCore.Qt.AlignTop)
        #super().setLayout(layout)

        self.msg_layout = QVBoxLayout()
        layout.addLayout(self.msg_layout)

        self.send = QPushButton("Send")
        self.send.clicked.connect(lambda: self.send_msg(1))
        self.text = QLineEdit()
        self.bot_answer = None
        self.attach = QPushButton("Send Pic")
        self.attach.clicked.connect(self.attach_msg)
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.text)
        tmp_layout.addWidget(self.attach)
        tmp_layout.addWidget(self.send)
        layout.addLayout(tmp_layout)

        self.img = None
        self.replay_to = None

        self.update(msgs)

        self.setWidget(widget)
        self.setWidgetResizable(True)


    def update(self, msgs):
        self.msgs = {}

        for i in reversed(range(self.msg_layout.count())): 
            self.msg_layout.itemAt(i).widget().deleteLater()

        for msg in msgs:
            m = Message(msg)
            m.doubleClicked.connect(self.replay)
            self.msgs[msg] = m
            self.msg_layout.addWidget(m)


    def attach_msg(self):
        self.img = QFileDialog.getOpenFileName(self, "Attach Img", ".", "Image Files (*.png *.jpg *.jpeg *.bmp * .tif)")[0]
        self.send_msg(1)
        self.img = None

    send_sig = QtCore.pyqtSignal(Msg)

    def send_msg(self, send_id):
        m = None
        if self.bot_answer != '':
            #print(self.bot_answer)
            m = Msg(m_id=len(self.msgs.keys()), text=self.bot_answer, f=True, sender=send_id)
            self.bot_answer = None
            self.send_sig.emit(m)

        if self.img == None:
            if self.text.text() == '':
                return
            m = Msg(m_id = len(self.msgs.keys()), text=self.text.text(), f=True, sender = send_id)
        else:
            m = Msg(m_id = len(self.msgs.keys()), img=self.img, f=True, sender = send_id)#text=self.text.text()
            self.img = None
        if self.replay_to != None:
            m.replay = self.replay_to
            self.replay_to = None
            self.unselect()
        self.send_sig.emit(m)
        self.text.clear()
        if send_id == 1:
            self.generate_reply()

    def unselect(self, l_id = []):
        for k in self.msgs.keys():
            self.msgs[k].change_bg(k in l_id)

    def replay(self):
        msg = self.sender()
        self.replay_to = msg.msg
        self.unselect([self.replay_to])

    def generate_reply(self):
        replies = ["ok!", "interesting", "wow", "great", "sorry, cant answer"]
        bot_reply = random.choice(replies)
        self.bot_answer = bot_reply
        self.send_msg(self.d_acc_id)

class Profile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        super().setWindowTitle("Add dialog with ...")
        layout = QFormLayout()
        self.img = QLabel()
        self.file = QPushButton("Open...")
        self.file.clicked.connect(self.set_avatar)
        self.text = QLineEdit()
        self.img_file = None
        super().setLayout(layout)
        layout.addRow("Avatar", self.img)
        layout.addRow("Set avatar", self.file)
        layout.addRow("Name", self.text)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def set_avatar(self):
        self.img_file = QFileDialog.getOpenFileName(self, "Attach Img", ".", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.webp)")[0]
        self.img.setPixmap(QPixmap(self.img_file).scaledToHeight(300))


class MyProfile(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        super().setWindowTitle("My profile...")
        layout = QFormLayout()
        self.img = QLabel()
        self.img_file = myDatabase.DBAccount.select().where(myDatabase.DBAccount.id == 1).get().avatar
        self.img.setPixmap(QPixmap(self.img_file).scaledToHeight(300))
        self.file = QPushButton("Open...")
        self.file.clicked.connect(self.set_avatar)
        self.text = QLineEdit(f'{myDatabase.DBAccount.select().where(myDatabase.DBAccount.id == 1).get().name}')
        super().setLayout(layout)
        layout.addRow("My avatar", self.img)
        layout.addRow("Set avatar", self.file)
        layout.addRow("My name", self.text)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def set_avatar(self):
        self.img_file = QFileDialog.getOpenFileName(self, "Attach Img", ".", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.webp)")[0]
        self.img.setPixmap(QPixmap(self.img_file).scaledToHeight(300))

class MainWindow(QMainWindow):
    def __init__(self, dataBaseName):
        super().__init__()
        self._myDatabase = myDatabase.MyDataBase(dataBaseName)

        self.setGeometry(300, 300, 200, 200)
        self.setWindowTitle('Messenger')
        self.setWindowIcon(QIcon('avatars/base.jpg'))

        w = QWidget()

        layout = QVBoxLayout()
        self.mainLayout = QVBoxLayout()
        w.setLayout(layout)
        layout.addLayout(self.mainLayout)

        self.setCentralWidget(w)
        
        self.add = QPushButton("New Dialog")
        self.profile = QPushButton("My profile")
        self.add.clicked.connect(self.new_dialog)
        self.profile.clicked.connect(self.changeProfile)
        layout.addWidget(self.add)
        layout.addWidget(self.profile)

        self.update()

    def update(self):
        for i in reversed(range(self.mainLayout.count())): 
            self.mainLayout.itemAt(i).widget().deleteLater()

        dialogs = []
        for d, m in self._myDatabase.dialogs():
            msg = Message(m)
            dialogs.append(Dialog(msg, author=d.account.name, d_id = d.id, d_acc_id=d.account.id))

        for d in dialogs:
            d.doubleClicked.connect(self.create_my_dialog)
            self.mainLayout.addWidget(d)

    def new_dialog(self):
        d = Profile(self)
        if d.exec() == QDialog.Accepted:
            self._myDatabase.add_dialog(name=d.text.text(), img=d.img_file)
            self.update()

    def changeProfile(self):
        d = MyProfile(self)
        if d.exec() == QDialog.Accepted:
            self._myDatabase.my_profile(name=d.text.text(), img=d.img_file)
            #self.update()

    def create_my_dialog(self):
        d = self.sender()
        msgs = self._myDatabase.messages(d.d_id)

        self.md = myDialog(msgs, title=d.author, parent=self, d_id=d.d_id, d_acc_id=d.d_acc_id)
        self.md.send_sig.connect(self.msg_sended)
        self.md.show()

    def msg_sended(self, msg):
        md = self.sender()
        self._myDatabase.add_msg(md.d_id, msg) #sender = !
        md.update(self._myDatabase.messages(md.d_id))
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = MainWindow("test.db")
    w.show()

    sys.exit(app.exec_())


