import tkinter as tk
from tkinter import ttk
import socket

import udp_settings

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
        self.canvas.bind("<Button-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.stop_move)

        self.draw_axes()

 

        # Motor speeds
        self.last_left_speed = 0
        self.last_right_speed = 0

        # Start periodic UDP updates
        self.periodic_udp_update()

    def send_udp_message(self, left_speed, right_speed):
        message = f"{left_speed} {right_speed}"
        self.sock.sendto(message.encode(), (self.udp_ip, self.udp_port))
        self.last_left_speed = left_speed
        self.last_right_speed = right_speed
     #   print(f"Left: {left_speed}, Right: {right_speed} ")

    def periodic_udp_update(self):
        self.send_udp_message(self.last_left_speed, self.last_right_speed)
        self.after(10, self.periodic_udp_update)  # Schedule next update after 10 ms

    def start_move(self, event):
        self.update_motor_speeds(event.x, event.y)

    def on_move(self, event):
        self.update_motor_speeds(event.x, event.y)

    def stop_move(self, event):
        self.send_udp_message(0, 0)  # Stop both motors when the mouse is released

    def update_motor_speeds(self, x, y):
        dy = x - self.center_x
        dx = self.center_y - y  # Positive dy should mean forward
        print (f"DX {dx} DY{dy}")
        left_speed = max(-255, min(255, dy + dx))
        right_speed = max(-255, min(255, dy - dx))

 

        self.send_udp_message(left_speed, right_speed)
      

    def draw_axes(self):
        self.canvas.create_line(0, self.center_y, 600, self.center_y, fill="black")
        self.canvas.create_line(self.center_x, 0, self.center_x, 600, fill="black")

if __name__ == "__main__":
    app = JoystickEmulator()
    app.mainloop()
