import util
import numpy as np
import cv2
import sys
import os
import dlib

CROP_DIR = "crop_dlib/"
IMG_DIM = 96

def collect(video_file_path, interval=30):
    detector = dlib.get_frontal_face_detector()
    win = dlib.image_window()
    cap = cv2.VideoCapture(video_file_path)
    video_name = os.path.splitext(os.path.basename(video_file_path))[0]
    crop_dir = CROP_DIR + video_name
    print ('crop_dir', crop_dir)
    if not os.path.isdir(crop_dir):
        os.mkdir(crop_dir)
    metadata_file_path = "{}-{}.tsv".format(os.path.join(os.path.dirname(video_file_path), video_name), interval)
    print ('metadata_file', metadata_file_path)
    
    metadata = dict()
    frame_counter = 0
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    curr_frame = 0
    while(curr_frame < total_frames):
        # cv2.imshow('frame', frame) 
        cap.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        ret, frame = cap.read()
        msec = cap.get(cv2.CAP_PROP_POS_MSEC)
 
        # Detect faces in the image
        try:
            dets = detector(frame, 1)
        except:
            break

        # Draw a rectangle around the faces
        face_counter = 1
        for i, d in enumerate(dets):
            x = d.left()
            y = d.top()
            w = d.right() - d.left()
            h = d.bottom() - d.top()
            #if w >= IMG_DIM and h >= IMG_DIM:
            crop_img = frame[y:(y+h), x:(x+w)]
            crop_img_path = os.path.join(crop_dir, "{}-{}.jpg".format(curr_frame, face_counter))
            cv2.imwrite(crop_img_path, crop_img)
            metadata[crop_img_path] = {
                'msec': msec,
                'frame_number': curr_frame,
                'position': str((x,y,w,h)),
                'character_id': -1
            }
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_counter += 1
        win.clear_overlay()
        win.set_image(frame)
        win.add_overlay(dets)
        cv2.imshow('frame', frame)
        curr_frame += interval
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    util.write_metadata_file(metadata_file_path, metadata)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Usage] python main.py [video_file_name]")
        sys.exit()
    if len(sys.argv) == 3:
        interval = int(sys.argv[2])
        collect(sys.argv[1], interval)
    else:
        collect(sys.argv[1])
