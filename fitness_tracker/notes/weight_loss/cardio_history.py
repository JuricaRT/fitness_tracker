import json
from functools import partial
from PyQt5.QtWidgets import (QWidget, QScrollArea, QGridLayout, QLabel, QPushButton,
                            QFormLayout, QLineEdit, QHBoxLayout, QVBoxLayout)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from fitness_tracker.user_profile.profile_db import fetch_units
from .weight_loss_db import fetch_cardio_history, update_cardio_entry, delete_cardio_entry

class CardioHistory(QScrollArea):
  refresh_cardio_labels_signal = pyqtSignal(bool)

  def __init__(self, sqlite_connection, pg_connection):
    super().__init__()
    self.sqlite_connection = sqlite_connection
    self.pg_connection = pg_connection
    self.sqlite_cursor = self.sqlite_connection.cursor()
    self.pg_cursor = self.pg_connection.cursor()
    self.setStyleSheet("""
    QWidget{
      background-color: #322d2d;
      font-weight: bold;
      color:#c7c7c7;
    }
    QPushButton{
      background-color: rgba(0, 0, 0, 0);
      border: 1px solid;
      font-size: 18px;
      font-weight: bold;
      border-color: #808080;
      min-height: 28px;
      white-space:nowrap;
      text-align: center;
      padding-left: 5%;
      font-family: Montserrat;
    }
    QPushButton:hover:!pressed{
      border: 2px solid;
      border-color: #747474;
    }
    QPushButton:pressed{
      border: 2px solid;
      background-color: #323232;
    }
    """)
    self.units = "kg" if fetch_units(self.sqlite_cursor) == "metric" else "lb"
    self.cardio_history = json.loads(fetch_cardio_history(self.sqlite_cursor))
    self.setWindowModality(Qt.ApplicationModal)
    self.setWindowFlags(Qt.Tool)
    self.setWindowTitle("Cardio History")
    
    widget = QWidget()
    self.layout = QGridLayout(widget)
    self.setWidget(widget)
    self.setWidgetResizable(True)
    
    self.entry_count = 0
    for date in self.cardio_history:
      for activity in self.cardio_history[date]:
        self.entry_count += len(self.cardio_history[date][activity])
    self.create_history(True, True)
  
  @pyqtSlot(bool)
  def create_history(self, create, init_layout=False):
    if create:
      if not init_layout:
        self.refresh_cardio_labels_signal.emit(True)
        self.delete_history()
    
      date_label = QLabel("Date")
      date_label.setAlignment(Qt.AlignCenter)
      activity_label = QLabel("Activity")
      activity_label.setAlignment(Qt.AlignCenter)
      
      edit_label = QLabel("Edit")
      edit_label.setAlignment(Qt.AlignCenter)
      delete_label = QLabel("Delete")
      delete_label.setAlignment(Qt.AlignCenter)
      
      self.layout.addWidget(date_label, 0, 0)
      self.layout.addWidget(activity_label, 0, 1)
      self.layout.addWidget(edit_label, 0, 2)
      self.layout.addWidget(delete_label, 0, 3)

      self.date_labels = [None] * self.entry_count
      self.cardio_labels = [None] * self.entry_count
      self.edit_buttons = [None] * self.entry_count
      self.delete_buttons = [None] * self.entry_count

      for i in range(self.entry_count):
        self.date_labels[i] = QLabel(self)
        self.cardio_labels[i] = QLabel(self)
        self.edit_buttons[i] = QPushButton("Edit", self)
        self.delete_buttons[i] = QPushButton("X", self) 
      
      row = 1
      j = 0
      for date in reversed(list(self.cardio_history.keys())):
        for activity in self.cardio_history[date]:
          if len(self.cardio_history[date][activity]) > 0:
            for data_index, activity_data in enumerate(list(reversed(self.cardio_history[date][activity]))):
              self.cardio_labels[j].setText(activity)
              self.date_labels[j].setText(date)
              self.edit_buttons[j].setProperty("data_index", data_index)
              self.edit_buttons[j].clicked.connect(partial(self.edit_cardio_dialog, date, activity, self.edit_buttons[j].property("data_index")))
              self.delete_buttons[j].setProperty("data_index", data_index)
              self.delete_buttons[j].clicked.connect(partial(self.delete_entry, j, date, activity, self.edit_buttons[j].property("data_index")))

              self.layout.addWidget(self.date_labels[j], row, 0, 1, 1)
              self.layout.addWidget(self.cardio_labels[j], row, 1, 1, 1)
              self.layout.addWidget(self.edit_buttons[j], row, 2, 1, 1)
              self.layout.addWidget(self.delete_buttons[j], row, 3, 1, 1)
              j += 1
              row += 1

  def edit_cardio_dialog(self, date, activity, index):
    self.edit_entry_dialog = EditCardioHistoryEntry(self.cardio_history, date, activity, index, self.sqlite_connection, self.pg_connection)
    self.edit_entry_dialog.update_cardio_history_signal.connect(lambda signal: self.create_history(signal))
    self.edit_entry_dialog.show()

  def delete_history(self):
    self.cardio_history = json.loads(fetch_cardio_history(self.sqlite_cursor))
    self.refresh_cardio_labels_signal.emit(True)
    for i in reversed(range(self.layout.count())):
      self.layout.itemAt(i).widget().setParent(None) 

  def delete_entry(self, j, date, activity, index):
    self.date_labels[j].setParent(None)
    self.cardio_labels[j].setParent(None)
    self.edit_buttons[j].setParent(None)
    self.delete_buttons[j].setParent(None)
    delete_cardio_entry(date, activity, index, self.sqlite_connection, self.pg_connection) 


class EditCardioHistoryEntry(QWidget):
  update_cardio_history_signal = pyqtSignal(bool)

  def __init__(self, cardio_history, date, activity, index, sqlite_connection, pg_connection):
    super().__init__()
    self.sqlite_connection = sqlite_connection
    self.pg_connection = pg_connection
    self.sqlite_cursor = self.sqlite_connection.cursor()
    self.pg_cursor = self.pg_connection.cursor()
    self.cardio_history = cardio_history
    self.date = date
    self.activity = activity
    self.index = index
    self.entry = self.cardio_history[self.date][self.activity][self.index]
    self.setStyleSheet("""
    QWidget{
      background-color: #322d2d;
      font-weight: bold;
      color:#c7c7c7;
    }
    QPushButton{
      background-color: rgba(0, 0, 0, 0);
      border: 1px solid;
      font-size: 18px;
      font-weight: bold;
      border-color: #808080;
      min-height: 28px;
      white-space:nowrap;
      text-align: center;
      padding-left: 5%;
      font-family: Montserrat;
    }
    QPushButton:hover:!pressed{
      border: 2px solid;
      border-color: #747474;
    }
    QPushButton:pressed{
      border: 2px solid;
      background-color: #323232;
    }
    """)
    self.units = "kg" if fetch_units(self.sqlite_cursor) == "metric" else "lb"
    self.cardio_history = json.loads(fetch_cardio_history(self.sqlite_cursor))
    self.setWindowModality(Qt.ApplicationModal)
    self.setWindowFlags(Qt.Tool)
    self.setWindowTitle("Edit Cardio History Entry")
    self.create_layout()

  def create_layout(self):
    layout = QVBoxLayout()
    form_layout = QFormLayout()
    activity_parameter_label = QLabel("Activity Parameter")
    value_label = QLabel("Value")

    time_spent_label = QLabel("Time Spent")
    self.time_spent_line_edit = QLineEdit()
    self.time_spent_line_edit.setValidator(QIntValidator())
    self.time_spent_line_edit.setText(self.entry["Time Spent"])
    
    distance_travelled_label = QLabel("Distance Travelled")
    self.distance_travelled_line_edit = QLineEdit()
    self.distance_travelled_line_edit.setValidator(QIntValidator())
    self.distance_travelled_line_edit.setText(self.entry["Distance Travelled"])

    calories_burnt_label = QLabel("Calories Burnt")
    self.calories_burnt_line_edit = QLineEdit()
    self.calories_burnt_line_edit.setValidator(QIntValidator())
    self.calories_burnt_line_edit.setText(self.entry["Calories Burnt"])
    
    buttons_layout = QHBoxLayout()
    save_button = QPushButton("Save")
    save_button.clicked.connect(lambda: self.save_entry())
    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(lambda: self.close())
    buttons_layout.addWidget(save_button)
    buttons_layout.addWidget(cancel_button)

    form_layout.addRow(activity_parameter_label, value_label)
    form_layout.addRow(time_spent_label, self.time_spent_line_edit)
    form_layout.addRow(distance_travelled_label, self.distance_travelled_line_edit)
    form_layout.addRow(calories_burnt_label, self.calories_burnt_line_edit)
    
    layout.addLayout(form_layout)
    layout.addLayout(buttons_layout)
    self.setLayout(layout)

  def save_entry(self):
    new_activity_entry = {"Time Spent": str(self.time_spent_line_edit.text()),
                          "Distance Travelled": str(self.distance_travelled_line_edit.text()),
                          "Calories Burnt": str(self.calories_burnt_line_edit.text())}
    update_cardio_entry(self.date, self.activity, new_activity_entry, self.index, self.sqlite_connection, self.pg_connection)
    self.update_cardio_history_signal.emit(True)
    self.close()
