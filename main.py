import numpy as np
import cv2
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[Usage] python main.py [video_file_name] [casc_path]")
        sys.exit()
    
    cap = cv2.VideoCapture(sys.argv[1])
    cascPath = sys.argv[2]

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    while(cap.isOpened()):
        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30),
            flags = cv2.CASCADE_SCALE_IMAGE
        )
        
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
