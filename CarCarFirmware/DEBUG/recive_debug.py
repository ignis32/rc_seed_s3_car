import socket

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 4211))  # Bind to the port you are sending data to

print("Listening for debug messages...")
try:
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("Received message:", data.decode())
except KeyboardInterrupt:
    sock.close()