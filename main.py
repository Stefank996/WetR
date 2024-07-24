import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontDatabase

class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WetR App by Stefan Karaga")
        self.setFixedSize(QSize(400, 300))

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(r"C:\Users\Stefan\Documents\Arduino\priums2\BebasNeue-Regular.ttf")
        if font_id == -1:
            print("Failed to load font!")
            return
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        anton_font = QFont(font_family, 15)

        # Create widgets for the first group
        self.label = QLabel("Izaberi mikrokontroler: ")
        self.label.setFont(anton_font)
        self.label.setAlignment(Qt.AlignCenter)

        self.combobox = QComboBox(self)
        self.combobox.addItems(["ESP32", "Arduino", "ST32", "Raspberry Pi"])
        self.combobox.setFont(anton_font)
        self.combobox.setFixedWidth(220)  # Adjust width as needed

        self.activate_button = QPushButton("Aktivacija")
        self.activate_button.setFixedWidth(70)
        self.stop_button = QPushButton("Prekid")
        self.stop_button.setFixedWidth(70)

        # Create widgets for the second group
        self.second_group_container = self.create_second_group_container()

        # Layouts
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.label)

        combobox_layout = QHBoxLayout()
        combobox_layout.addStretch(1)
        combobox_layout.addWidget(self.combobox)
        combobox_layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.stop_button)

        # Create a main layout and add the first group, buttons, and second group
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(combobox_layout)  # Add combobox layout
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)  # Add spacing between groups
        main_layout.addWidget(self.second_group_container, alignment=Qt.AlignCenter)  # Add the second group container with alignment

        self.setLayout(main_layout)

        # Connect buttons to methods
        self.activate_button.clicked.connect(self.activate_system)
        self.stop_button.clicked.connect(self.close)

    def create_second_group_container(self):
        # Create a QWidget to serve as the container for the second group
        second_group_container = QWidget()

        # Create a QFormLayout for the second group
        form_layout = QFormLayout()

        # Define the width for QLineEdits
        line_edit_width = 90  # Width in pixels

        # Create labels and QLineEdits
        temp_label = QLabel("Temperatura:")
        temp_value = QLineEdit()
        temp_value.setFixedWidth(line_edit_width)
        temp_value.setAlignment(Qt.AlignCenter)

        humidity_label = QLabel("Vlaznost vazduha:")
        humidity_value = QLineEdit()
        humidity_value.setFixedWidth(line_edit_width)
        humidity_value.setAlignment(Qt.AlignCenter)

        soil_label = QLabel("Vlaznost zemlje:")
        soil_value = QLineEdit()
        soil_value.setFixedWidth(line_edit_width)
        soil_value.setAlignment(Qt.AlignCenter)

        fan_speed_label = QLabel("Brzina ventilatora(%):")
        fan_speed_value = QLineEdit()
        fan_speed_value.setFixedWidth(line_edit_width)
        fan_speed_value.setAlignment(Qt.AlignCenter)

        # Add labels and text boxes to the form layout
        form_layout.addRow(temp_label, temp_value)
        form_layout.addRow(humidity_label, humidity_value)
        form_layout.addRow(soil_label, soil_value)
        form_layout.addRow(fan_speed_label, fan_speed_value)

        # Optionally set read-only for QLineEdits
        for i in range(form_layout.rowCount()):
            form_layout.itemAt(i*2 + 1).widget().setReadOnly(True)

        # Create a QWidget for the second group and set its layout
        second_group_widget = QWidget()
        second_group_widget.setLayout(form_layout)

        # Create an outer QVBoxLayout and add the second group widget
        second_group_outer_layout = QVBoxLayout()
        second_group_outer_layout.addWidget(second_group_widget)
        second_group_outer_layout.setAlignment(Qt.AlignCenter)  # Center align the second group

        # Set the layout for the second group container
        second_group_container.setLayout(second_group_outer_layout)

        return second_group_container

    def activate_system(self):
        print("Aktivacija sistema clicked")

app = QApplication(sys.argv)

control_window = ControlWindow()
control_window.show()

app.exec()
