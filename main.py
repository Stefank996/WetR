import sys
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QFontDatabase

class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Window")
        self.setFixedSize(QSize(400, 300))

        # Load custom font
        font_id = QFontDatabase.addApplicationFont(r"C:\Users\Stefan\Documents\priums2\Anton.ttf")
        if font_id == -1:
            print("Failed to load font!")
            return
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        anton_font = QFont(font_family, 16)

        # Create widgets for the first group
        self.label = QLabel("Izaberite mikrokontroler: ")
        self.label.setFont(anton_font)
        self.label.setAlignment(Qt.AlignCenter)

        self.combobox = QComboBox(self)
        self.combobox.addItems(["ESP32", "Arduino", "ST32", "Raspberry Pi"])
        self.combobox.setFont(anton_font)

        self.activate_button = QPushButton("Aktivacija")
        self.activate_button.setFont(anton_font)
        self.stop_button = QPushButton("Prekid")
        self.stop_button.setFont(anton_font)

        # Create widgets for the second group
        self.second_group_container = self.create_second_group_container()

        # Layouts
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.label)
        top_layout.addWidget(self.combobox)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.activate_button)
        button_layout.addWidget(self.stop_button)

        # Create a main layout and add the first group, buttons, and second group
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)  # Add spacing between groups
        main_layout.addWidget(self.second_group_container)  # Add the second group container

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
        line_edit_width = 90  # Width in pixels (adjusted to be half)

        # Create labels and QLineEdits
        self.temp_label = QLabel("Temperatura:")
        self.temp_value = QLineEdit()
        self.temp_value.setFixedWidth(line_edit_width)
        self.temp_value.setAlignment(Qt.AlignCenter)

        self.humidity_label = QLabel("Vlaznost vazduha:")
        self.humidity_value = QLineEdit()
        self.humidity_value.setFixedWidth(line_edit_width)
        self.humidity_value.setAlignment(Qt.AlignCenter)

        self.soil_label = QLabel("Vlaznost zemlje:")
        self.soil_value = QLineEdit()
        self.soil_value.setFixedWidth(line_edit_width)
        self.soil_value.setAlignment(Qt.AlignCenter)

        self.fan_speed_label = QLabel("Brzina ventilatora(%):")
        self.fan_speed_value = QLineEdit()
        self.fan_speed_value.setFixedWidth(line_edit_width)
        self.fan_speed_value.setAlignment(Qt.AlignCenter)

        # Add labels and text boxes to the form layout
        form_layout.addRow(self.temp_label, self.temp_value)
        form_layout.addRow(self.humidity_label, self.humidity_value)
        form_layout.addRow(self.soil_label, self.soil_value)
        form_layout.addRow(self.fan_speed_label, self.fan_speed_value)

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
        esp32_ip = "192.168.100.82"  # Replace with your ESP32 IP address
        port = 12345

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((esp32_ip, port))
                s.sendall(b"GET / HTTP/1.1\r\n\r\n")
                data = s.recv(1024).decode()
                
                if data:
                    data_dict = self.parse_data(data)
                    self.temp_value.setText(data_dict.get("Temperature", "N/A"))
                    self.humidity_value.setText(data_dict.get("Humidity", "N/A"))
                    self.soil_value.setText(data_dict.get("SoilMoisture", "N/A"))
                    self.fan_speed_value.setText(data_dict.get("FanSpeed", "N/A"))
        except Exception as e:
            print(f"Error: {e}")

    def parse_data(self, data):
        data_dict = {}
        pairs = data.strip().split(',')
        for pair in pairs:
            key, value = pair.split(':')
            data_dict[key.strip()] = value.strip()
        return data_dict

if __name__ == "__main__":
    app = QApplication(sys.argv)
    control_window = ControlWindow()
    control_window.show()
    sys.exit(app.exec())
