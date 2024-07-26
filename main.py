import sys
import paho.mqtt.client as mqtt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit
)
from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont, QFontDatabase

class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WetR App by Stefan Karaga")
        self.setFixedSize(QSize(400, 400))

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
        self.fan_button.clicked.connect(self.toggle_fan)

        # MQTT client setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("192.168.100.33", 1883, 60)

        # Timer for periodic data fetching
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_data)

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

        # Create a QVBoxLayout for the third group
        vbox_layout = QVBoxLayout()

        # Create and configure the siren button
        self.siren_button = QPushButton("Uključi / Isključi Sirenu")
        self.siren_button.setFixedWidth(200)
        self.siren_button.setFont(QFont("Arial", 12))
        
        # Create and configure the fan button
        self.fan_button = QPushButton("Vent. Off/On")
        self.fan_button.setFixedWidth(200)
        self.fan_button.setFont(QFont("Arial", 12))
        
        # Add the buttons to the layout
        vbox_layout.addStretch(1)
        vbox_layout.addWidget(self.siren_button)
        vbox_layout.addWidget(self.fan_button)
        vbox_layout.addStretch(1)

        # Set the layout for the third group container
        third_group_container.setLayout(vbox_layout)

        return third_group_container

    def start_fetching_data(self):
        self.mqtt_client.loop_start()
        self.timer.start(3000)  # Fetch data every 3 seconds

    def stop_fetching_data(self):
        self.timer.stop()
        self.mqtt_client.loop_stop()
        QApplication.quit()  # Close the application

    def fetch_data(self):
        self.mqtt_client.publish("sensor/request", "GET_DATA")

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        client.subscribe("sensor/data")

    def on_message(self, client, userdata, msg):
        data = msg.payload.decode('utf-8').strip()
        self.update_ui(data)

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
        self.mqtt_client.publish("buzzer/control", "TOGGLE")

    def toggle_fan(self):
        self.mqtt_client.publish("fan/control", "TOGGLE")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec())
