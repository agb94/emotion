import numpy as np
import cv2
import sys
import os

CROP_DIR = "./crop/"
INTERVAL = 10

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[Usage] python main.py [video_file_name] [casc_path]")
        sys.exit()
    
    cap = cv2.VideoCapture(sys.argv[1])
    cascPath = sys.argv[2]
    
    video_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    metadata_file_path = os.path.join(os.path.dirname(sys.argv[1]), video_name) + '.tsv'
    metadata_file = open(metadata_file_path, 'w')
    metadata_columns = ['Image File Path', 'MSEC', 'Frame Number', 'Position', 'Character ID'] 
    metadata_file.write("\t".join(metadata_columns) + "\n")

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    frame_counter = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        cv2.imshow('frame', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if frame_counter % INTERVAL == 0:
            # Detect faces in the image
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30, 30),
                flags = cv2.CASCADE_SCALE_IMAGE
            )
            
            # Draw a rectangle around the faces
            face_counter = 1
            for (x, y, w, h) in faces:
                crop_img = frame[y:(y+h), x:(x+w)]
                crop_img_path = CROP_DIR + "{}-{}.jpg".format(frame_counter, face_counter)
                cv2.imwrite(crop_img_path, crop_img)
                metadata_file.write("{}\t{}\t{}\t{}\t{}\n".format(crop_img_path, msec, frame_counter, str((x,y,w,h)), -1))
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_counter += 1

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_counter += 1

    metadata_file.close()
    cap.release()
    cv2.destroyAllWindows()
