import tkinter as tk
from tkinter import ttk
import socket
import mido

import udp_settings
dx=0
dy=0
class JoystickEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Joystick Emulator')
        self.geometry('600x600')

        # UDP setup
        self.udp_ip = udp_settings.ip
        self.udp_port = udp_settings.port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Joystick canvas
        self.canvas = tk.Canvas(self, width=600, height=600, bg='white')
        self.canvas.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
        self.center_x = 300
        self.center_y = 300
        self.draw_axes()

        # Motor speeds
        self.last_left_speed = 0
        self.last_right_speed = 0

        # Start periodic UDP updates
        self.periodic_udp_update()
        

        # Setup MIDI
        self.midi_input_port = self.setup_midi()

    def setup_midi(self):
        # List all available MIDI input ports
        input_names = mido.get_input_names()
        widi_port_name = next((name for name in input_names if "WIDI" in name), None)
        if widi_port_name:
            return mido.open_input(widi_port_name, callback=self.midi_callback)
        else:
            print("No WIDI device found.")
            return None

   
   
    def midi_callback(self, message):
        global dx
        global dy
        if message.type == 'control_change':
           if message.control == 13:  # Throttle (CC 11)
             #   print(f"MESSAGE 11 {message.value}")

              dx = (127- message.value)*4 - 255
                
           elif message.control == 12:  # Rotation (CC 12)
            #   print(f"MESSAGE 12        {message.value}")
               dy = (message.value)*4 - 255
        print (f"{dx} {dy}")
       
        left_speed = max(-255, min(255, dy + dx))
        right_speed = max(-255, min(255, dy - dx))

        
        self.update_motor_speeds(left_speed, right_speed)
        self.last_left_speed = left_speed
        self.last_right_speed = right_speed
        

    def update_motor_speeds(self, left_speed, right_speed):
        
        self.send_udp_message(left_speed, right_speed)

    def send_udp_message(self, left_speed, right_speed):
        message = f"{left_speed} {right_speed}"
        self.sock.sendto(message.encode(), (self.udp_ip, self.udp_port))
        self.last_left_speed = left_speed
        self.last_right_speed = right_speed
      #  print(f"Left: {left_speed}, Right: {right_speed}")

    def periodic_udp_update(self):
        self.send_udp_message(self.last_left_speed, self.last_right_speed)
        self.after(10, self.periodic_udp_update)

    def draw_axes(self):
        self.canvas.create_line(0, self.center_y, 600, self.center_y, fill="black")
        self.canvas.create_line(self.center_x, 0, self.center_x, 600, fill="black")

if __name__ == "__main__":
    app = JoystickEmulator()
    app.mainloop()
