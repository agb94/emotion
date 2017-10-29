import numpy as np
import cv2
import sys
import os
import dlib
#from skimage import io


CROP_DIR = "./crop_dlib/"
INTERVAL = 30

detector = dlib.get_frontal_face_detector()
win = dlib.image_window()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Usage] python main.py [video_file_name]")
        sys.exit()
    
    cap = cv2.VideoCapture(sys.argv[1])

    video_name = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    crop_dir = CROP_DIR + video_name
    print ('crop_dir', crop_dir)
    if not os.path.isdir(crop_dir):
        os.mkdir(crop_dir)
    metadata_file_path = os.path.join(os.path.dirname(sys.argv[1]), video_name) + '.tsv'
    metadata_file = open(metadata_file_path, 'w')
    metadata_columns = ['Image File Path', 'MSEC', 'Frame Number', 'Position', 'Character ID'] 
    metadata_file.write("\t".join(metadata_columns) + "\n")

    # Create the haar cascade
    # eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    
    frame_counter = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        msec = cap.get(cv2.CAP_PROP_POS_MSEC)
        #cv2.imshow('frame', frame)
        
        if frame_counter % INTERVAL == 0:
            # Detect faces in the image
            dets = detector(frame, 1)
            
            # Draw a rectangle around the faces
            face_counter = 1
            for i, d in enumerate(dets):
                x = d.left()
                y = d.top()
                w = d.right() - d.left()
                h = d.bottom() - d.top()
                crop_img = frame[y:(y+h), x:(x+w)]
                crop_img_path = os.path.join(crop_dir, "{}-{}.jpg".format(frame_counter, face_counter))
                cv2.imwrite(crop_img_path, crop_img)
                metadata_file.write("{}\t{}\t{}\t{}\t{}\n".format(crop_img_path, msec, frame_counter, str((x,y,w,h)), -1))
                #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_counter += 1
            win.clear_overlay()
            win.set_image(frame)
            win.add_overlay(dets)

        #cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_counter += 1
       
    metadata_file.close()
    cap.release()
    cv2.destroyAllWindows()
