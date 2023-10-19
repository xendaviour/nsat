import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

import socket
import threading

from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')

class PortScannerApp(App):
    def build(self):
        return PortScannerUI()

class PortScannerUI(BoxLayout):
    def __init__(self, **kwargs):
        super(PortScannerUI, self).__init__(**kwargs)

        self.orientation = 'vertical'
        self.target_label = Label(text="Enter Your IP/Domain:")
        self.target_input = TextInput(multiline=False, size_hint=(None, None), height=50, width=2000)  # Smaller text input box
        self.start_port_label = Label(text="Start Port:")
        self.start_port_input = TextInput(multiline=False, size_hint=(None, None), height=50, width=2000)  # Smaller text input box
        self.end_port_label = Label(text="End Port:")
        self.end_port_input = TextInput(multiline=False, size_hint=(None, None), height=50, width=2000)  # Smaller text input box


        self.scan_type_label = Label(text="Select your scan type:")
        self.scan_type_button_1 = Button(text="1 to 1024")
        self.scan_type_button_2 = Button(text="1 to 65535")
        self.scan_type_button_3 = Button(text="Custom")
        self.scan_type_button_4 = Button(text="Exit")
        
        self.scan_type_button_1.size_hint = (None, None)
        self.scan_type_button_1.width = 300
        self.scan_type_button_2.size_hint = (None, None)
        self.scan_type_button_2.width = 300
        self.scan_type_button_3.size_hint = (None, None)
        self.scan_type_button_3.width = 300
        self.scan_type_button_4.size_hint = (None, None)
        self.scan_type_button_4.width = 300

        self.scan_output = ScrollView(size_hint=(1, 0.7))  # Adjust the size_hint for a larger result area
        self.scan_results = Label(text="Scan Results:\n", halign="left", valign="top", text_size=(None, None))
        self.scan_output.add_widget(self.scan_results)

        self.scan_type_button_1.bind(on_press=self.select_scan_type)
        self.scan_type_button_2.bind(on_press=self.select_scan_type)
        self.scan_type_button_3.bind(on_press=self.select_scan_type)
        self.scan_type_button_4.bind(on_press=self.exit_app)

        self.add_widget(self.target_label)
        self.add_widget(self.target_input)
        self.add_widget(self.start_port_label)
        self.add_widget(self.start_port_input)
        self.add_widget(self.end_port_label)
        self.add_widget(self.end_port_input)

        self.scan_type_layout = GridLayout(cols=4)
        self.scan_type_layout.add_widget(self.scan_type_button_1)
        self.scan_type_layout.add_widget(self.scan_type_button_2)
        self.scan_type_layout.add_widget(self.scan_type_button_3)
        self.scan_type_layout.add_widget(self.scan_type_button_4)
        self.add_widget(self.scan_type_layout)
        
        self.add_widget(self.scan_type_label)
        self.add_widget(self.scan_output)

        self.host = ""
        self.mode = 0
        self.custom_port_start = 0
        self.custom_port_end = 0

        self.loading_popup = None

    def select_scan_type(self, instance):
        self.host = self.target_input.text
        self.custom_port_start = int(self.start_port_input.text)
        self.custom_port_end = int(self.end_port_input.text)

        if instance == self.scan_type_button_1:
            self.mode = 1
        elif instance == self.scan_type_button_2:
            self.mode = 2
        elif instance == self.scan_type_button_3:
            self.mode = 3
        elif instance == self.scan_type_button_4:
            self.exit_app(instance)
            return

        self.clear_results()
        self.create_loading_popup()
        threading.Thread(target=self.scan_ports).start()

    def exit_app(self, instance):
        App.get_running_app().stop()

    def clear_results(self):
        self.scan_results.text = "Scan Results:\n"

    def update_results(self, result):
        self.scan_results.text += result + "\n"

    def create_loading_popup(self):
        content = BoxLayout(orientation='vertical', spacing=10)
        self.loading_label = Label(text="Scanning in progress...")
        self.target_info = Label(text=f"Target IP/Domain: {self.host}")
        self.loading_status = Label(text="Scanning status: Idle")
        content.add_widget(self.loading_label)
        content.add_widget(self.target_info)
        content.add_widget(self.loading_status)
        self.loading_popup = Popup(title='Scanning', content=content, auto_dismiss=False, size_hint=(None, None), size=(400, 200))
        self.loading_popup.open()

    def scan_ports(self):
        def scan(port):
            s = socket.socket()
            s.settimeout(0.05)  # 10 milliseconds (0.01 seconds)
            result = s.connect_ex((self.host, port))
            if result == 0:
                self.update_results(f"Port {port} is open!")
            self.loading_status.text = f"Scanning status: Port {port}"

        def get_ports():
            if self.mode == 1:
                return range(1, 1025)
            elif self.mode == 2:
                return range(1, 65536)
            elif self.mode == 3:
                return range(self.custom_port_start, self.custom_port_end + 1)

        for port in get_ports():
            scan(port)

        self.loading_status.text = "Scanning status: Completed"
        self.loading_popup.dismiss()

if __name__ == '__main__':
    PortScannerApp().run()
