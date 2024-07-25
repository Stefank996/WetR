import sys
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit
)
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase

class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WetR App by Stefan Karaga")
        self.setFixedSize(QSize(400, 350))

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
        self.combobox.setFixedWidth(220)

        self.activate_button = QPushButton("Aktivacija")
        self.activate_button.setFixedWidth(70)
        self.stop_button = QPushButton("Prekid")
        self.stop_button.setFixedWidth(70)

        # Create widgets for the second group
        self.second_group_container = self.create_second_group_container()

        # Create widgets for the third group
        self.third_group_container = self.create_third_group_container()

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

        # Create a main layout and add the first group, buttons, and second and third groups
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(combobox_layout)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.second_group_container, alignment=Qt.AlignCenter)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.third_group_container, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

        # Connect buttons to methods
        self.activate_button.clicked.connect(self.start_fetching_data)
        self.stop_button.clicked.connect(self.stop_fetching_data)
        self.siren_button.clicked.connect(self.toggle_siren)

        # Timer for periodic data fetching
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_data)

        # Initialize socket
        self.sock = None

    def create_second_group_container(self):
        # Create a QWidget to serve as the container for the second group
        second_group_container = QWidget()

        # Create a QFormLayout for the second group
        form_layout = QFormLayout()

        # Define the width for QLineEdits
        line_edit_width = 90

        # Create labels and QLineEdits
        self.temp_value = QLineEdit()
        self.temp_value.setFixedWidth(line_edit_width)
        self.temp_value.setAlignment(Qt.AlignCenter)
        
        self.humidity_value = QLineEdit()
        self.humidity_value.setFixedWidth(line_edit_width)
        self.humidity_value.setAlignment(Qt.AlignCenter)
        
        self.soil_value = QLineEdit()
        self.soil_value.setFixedWidth(line_edit_width)
        self.soil_value.setAlignment(Qt.AlignCenter)
        
        self.fan_speed_value = QLineEdit()
        self.fan_speed_value.setFixedWidth(line_edit_width)
        self.fan_speed_value.setAlignment(Qt.AlignCenter)

        # Add labels and text boxes to the form layout
        form_layout.addRow("Temperatura (°C):", self.temp_value)
        form_layout.addRow("Vlažnost (%):", self.humidity_value)
        form_layout.addRow("Vlažnost zemlje (%):", self.soil_value)
        form_layout.addRow("Brzina ventilatora (%):", self.fan_speed_value)

        # Set the layout for the container
        second_group_container.setLayout(form_layout)

        return second_group_container

    def create_third_group_container(self):
        # Create a QWidget to serve as the container for the third group
        third_group_container = QWidget()

        # Create a QHBoxLayout for the third group
        hbox_layout = QHBoxLayout()

        # Create and configure the siren button
        self.siren_button = QPushButton("Uključi / Isključi Sirenu")
        self.siren_button.setFixedWidth(200)
        self.siren_button.setFont(QFont("Arial", 12))
        
        # Add the button to the layout
        hbox_layout.addStretch(1)
        hbox_layout.addWidget(self.siren_button)
        hbox_layout.addStretch(1)

        # Set the layout for the third group container
        third_group_container.setLayout(hbox_layout)

        return third_group_container

    def start_fetching_data(self):
        self.connect_to_esp32()
        self.timer.start(3000)  # Fetch data every 3 seconds

    def stop_fetching_data(self):
        self.timer.stop()
        if self.sock:
            self.sock.close()
            self.sock = None
        QApplication.quit()  # Close the application

    def connect_to_esp32(self):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('192.168.100.82', 12345))  # Use the IP address and port of your ESP32
        except Exception as e:
            print(f"Failed to connect to ESP32: {e}")
            self.sock = None

    def fetch_data(self):
        if self.sock:
            try:
                self.sock.sendall(b'GET_DATA')  # Send request to ESP32
                data = self.sock.recv(1024).decode('utf-8').strip()
                if data:
                    self.update_ui(data)
            except socket.error as e:
                print(f"Error fetching data: {e}")
                self.connect_to_esp32()  # Try to reconnect if there is an error

    def update_ui(self, data):
        print(f"Received data: {data}")
        try:
            parts = data.split()
            temp = float(parts[0].split(":")[1])
            humidity = float(parts[1].split(":")[1])
            soil_moisture = float(parts[2].split(":")[1])
            fan_speed = float(parts[3].split(":")[1])
            
            self.temp_value.setText(f"{temp:.2f}")
            self.humidity_value.setText(f"{humidity:.2f}")
            self.soil_value.setText(f"{soil_moisture:.2f}")
            self.fan_speed_value.setText(f"{fan_speed:.2f}")
        except (IndexError, ValueError) as e:
            print(f"Error parsing data: {e}")

    def toggle_siren(self):
        if self.sock:
            try:
                self.sock.sendall(b'TOGGLE_SIREN')  # Send command to toggle siren
            except socket.error as e:
                print(f"Error sending siren command: {e}")
                self.connect_to_esp32()  # Try to reconnect if there is an error

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec())
