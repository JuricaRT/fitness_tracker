from PyQt5.QtWidgets import QWidget, QGridLayout, QFrame, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from .signup_helpers import Signup

class MainPanel(QWidget):
  def __init__(self, parent, controller):
    super().__init__(parent)
    self.controller = controller
    self.create_panel()

  def create_panel(self):
    grid = QGridLayout()
    grid.addLayout(self.create_login(), 0, 0, 1, 1)
    self.setLayout(grid)

  def create_login(self):
    title_frame = QFrame()
    title_layout = QVBoxLayout()

    signup_label = QLabel("Signup", self)
    signup_label.setFont(QFont("Ariel", 15))
    signup_label.setFixedHeight(70)

    title_layout.addWidget(signup_label)
    title_frame.setLayout(title_layout)

    signup_frame = QFrame()
    signup_frame.setFrameStyle(QFrame.StyledPanel)

    form_layout = self.create_form_layout()
    signup_frame.setLayout(form_layout)

    wrapper_layout = QVBoxLayout()
    wrapper_layout.addWidget(title_frame)
    wrapper_layout.addWidget(signup_frame)
    return wrapper_layout

  def create_form_layout(self):
    form_layout = QFormLayout()

    email_label = QLabel("Email", self)
    self.email_entry = QLineEdit()
    
    password_label = QLabel("Password", self)
    self.password_entry = QLineEdit()
    self.password_entry.setEchoMode(QLineEdit.Password)

    confirm_password_label = QLabel("Confirm Password", self)
    self.confirm_password_entry = QLineEdit()
    self.confirm_password_entry.setEchoMode(QLineEdit.Password)
    
    self.continue_button = QPushButton("Continue", self)
    self.continue_button.setCursor(QCursor(Qt.PointingHandCursor))
    self.continue_button.clicked.connect(lambda: self.continue_signup())

    login_label = QLabel("Already have an account?")
    self.login_button = QPushButton("Login", self)
    self.login_button.clicked.connect(lambda: self.controller.display_layout(self.login_button.text()))
    self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
    
    form_layout.addRow(email_label, self.email_entry)
    form_layout.addRow(password_label, self.password_entry)
    form_layout.addRow(confirm_password_label, self.confirm_password_entry)
    form_layout.addRow(self.continue_button)
    form_layout.addRow(login_label, self.login_button)
    return form_layout

  def continue_signup(self):
    email = self.email_entry.text()
    password = self.password_entry.text()
    confirmed_password = self.confirm_password_entry.text()
    interface = Signup()
    if password == confirmed_password and interface.check_valid_password(password) and interface.check_valid_email(email):
      interface.create_user(email, password)
      interface.create_user_table(email, password)
      self.controller.display_layout(self.continue_button.text())
