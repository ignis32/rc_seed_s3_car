import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import time

stream_url = "http://192.168.0.102:80"
stream_url = "http://185.206.146.175:8080"
 

def display_mjpeg_stream(stream_url):
    last_frame = None

    while True:
        try:
            # Open a connection to the MJPEG stream with a timeout of 0.5 seconds
            stream = requests.get(stream_url, stream=True, timeout=0.5)
            if stream.status_code != 200:
                print(f"Error: Unable to open stream (status code: {stream.status_code})")
                # Display restoring connection message
                if last_frame is not None:
                    fps_text = f"FPS: {fps:.2f}"
                    (fps_text_width, _), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    cv2.putText(last_frame, "Restoring connection...", (10 + fps_text_width + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(f"MJPEG Stream {stream_url}", last_frame)
                    cv2.waitKey(1)
                time.sleep(5)  # Wait before trying to reconnect
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
                    fps_text = f"FPS: {fps:.2f}"
                    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Calculate width of the FPS text
                    (fps_text_width, _), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

                    # Update the last frame
                    last_frame = frame.copy()
                    
                    cv2.imshow(f"MJPEG Stream {stream_url}", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except (requests.exceptions.RequestException, cv2.error) as e:
            print(f"Stream error: {e}")
            # Display restoring connection message
            if last_frame is not None:
                fps_text = f"FPS: {fps:.2f}"
                (fps_text_width, _), _ = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                cv2.putText(last_frame, "Restoring connection...", (10 + fps_text_width + 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow(f"MJPEG Stream {stream_url}", last_frame)
                cv2.waitKey(1)
            time.sleep(0.010)  # Wait before trying to reconnect

    cv2.destroyAllWindows()

display_mjpeg_stream(stream_url)
