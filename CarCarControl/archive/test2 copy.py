import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import time

stream_url = "http://192.168.0.102:80"


def display_mjpeg_stream(stream_url):
    while True:
        try:
            # Open a connection to the MJPEG stream with a timeout of 0.5 seconds
            stream = requests.get(stream_url, stream=True, timeout=0.5)
            if stream.status_code != 200:
                print(f"Error: Unable to open stream (status code: {stream.status_code})")
              #  time.sleep(5)  # Wait before trying to reconnect
                continue

            bytes_data = bytes()
            frame_count = 0
            start_time = time.time()

            for chunk in stream.iter_content(chunk_size=1024):
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]

                    img = Image.open(BytesIO(jpg))
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    frame_count += 1
                    elapsed_time = time.time() - start_time
                    fps = frame_count / elapsed_time

                    # Display FPS on frame
                    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    cv2.imshow(f"MJPEG Stream {stream_url}", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except (requests.exceptions.RequestException, cv2.error) as e:
            print(f"Stream error: {e}")
            time.sleep(5)  # Wait before trying to reconnect

        cv2.destroyAllWindows()  # Ensure the window is closed before reconnecting
        print("Reconnecting to stream...")


display_mjpeg_stream(stream_url)
