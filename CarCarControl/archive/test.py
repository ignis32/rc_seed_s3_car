import cv2

def display_video_stream():
    # URL of the video stream from DroidCamX
   
    stream_url = "http://192.168.0.102:80"
    # Create a VideoCapture object
    print(">>")
    cap = cv2.VideoCapture(stream_url)
    print("<<")
    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return
    
    # Read and display frames continuously
    while True:
        print(".")
        ret, frame = cap.read()  # Read a frame
        if not ret:
            print("Error: Cannot read from stream.")
            break
        
        cv2.imshow('DroidCamX Stream', frame)  # Display the frame
        print("a")
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q' key press
            break
    
    # Release the VideoCapture object and close windows
    cap.release()
    cv2.destroyAllWindows()
print("hi")
display_video_stream()