import cv2

# 1. Initialize the webcam (0 is usually the default built-in camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
else:
    # 2. Get width and height using OpenCV properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 3. Calculate the aspect ratio
    aspect_ratio = width / height

    # 4. Display the results
    print(f"Width: {width} pixels")
    print(f"Height: {height} pixels")
    print(f"Aspect Ratio: {aspect_ratio:.2f}")

# Release the webcam resource
cap.release()