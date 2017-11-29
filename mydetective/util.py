import csv
import copy
import os
import cv2

def save_frame(video_file, frame_number, frame_root_dir):
    if not video_file.endswith('avi') and not video_file.endswith('mkv'):
        video_name = '-'.join(video_file.split('.')[0].split('-')[:-1])
        print (video_name)
        if os.path.exists(video_name + '.avi'):
            video_file = video_name + '.avi'
        elif os.path.exists(video_name + '.mkv'):
            video_file = video_name + '.mkv'
    print (video_file)
    cap = cv2.VideoCapture(video_file)
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    frame_dir = os.path.join(frame_root_dir, video_name)
    frame_img_path = os.path.join(video_name, "{}.jpg".format(frame_number))
    if os.path.exists(os.path.join(frame_root_dir, frame_img_path)):
        return frame_img_path
    if not os.path.isdir(frame_dir):
        os.mkdir(frame_dir)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cv2.imwrite(os.path.join(frame_root_dir, frame_img_path), frame)
    cap.release()
    cv2.destroyAllWindows()
    return frame_img_path

def get_metadata_file_path(video_file_path, interval=30, interval_sec=None):
    if interval_sec:
        cap = cv2.VideoCapture(video_file_path)    
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = int(fps * interval_sec)
        cap.release()
    video_name = os.path.splitext(os.path.basename(video_file_path))[0]
    metadata_file_path = "{}-{}.tsv".format(os.path.join(os.path.dirname(video_file_path), video_name), interval) 
    return metadata_file_path

def get_overview_and_clip(metadata_file_path):
    path, extension = os.path.splitext(metadata_file_path)
    overview_path = path + '-characters' + extension
    clip_path = path + '-clip' + extension
    if not os.path.exists(overview_path) or not os.path.exists(clip_path):
        from .character_analyzer import character_analyzer
        overview_path, clip_path = character_analyzer(metadata_file_path) 
    return (parse_overview_file(overview_path), parse_clip_file_to_dict(clip_path))
        
def parse_metadata_file(metadata_file_path):
    metadata = list()
    with open(metadata_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            metadata.append({
                'character_id': int(row['character_id']),
                'msec': float(row['msec']),
                'frame_number': int(row['frame_number']),
                'position': eval(row['position']),
                'image_file_path': row['image_file_path'],
                'centroid': bool(int(row['centroid']))
            })
    return metadata

def parse_metadata_file_to_dict(metadata_file_path):
    metadata = dict()
    with open(metadata_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            metadata[row['image_file_path']]= {
                'character_id': int(row['character_id']),
                'msec': float(row['msec']),
                'frame_number': int(row['frame_number']),
                'position': eval(row['position']),
                'centroid': bool(int(row['centroid']))
            }
    return metadata

def write_metadata_file(metadata_file_path, metadata):
    sorted_metadata = sorted(metadata.items(), key=lambda t: (t[1]['frame_number'], t[0]))
    with open(metadata_file_path, 'w') as tsvfile:
        columns = ['image_file_path', 'msec', 'frame_number', 'position', 'character_id', 'centroid']
        tsvfile.write("\t".join(columns) + "\n")
        for k, v in sorted_metadata:
            tsvfile.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(k, v['msec'], v['frame_number'], v['position'], v['character_id'], int(v['centroid'])))

def parse_overview_file(overview_file_path):
    overview = dict()
    with open(overview_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            overview[int(row['character_id'])]= {
                'appearance_count': int(row['appearance_count']),
                'level_of_importance': float(row['level_of_importance']),
                'centroid_image': row['centroid_image']
            }
    sorted_overview = sorted(overview.items(), key=lambda t: t[1]['level_of_importance'])
    sorted_overview.reverse()
    return sorted_overview

def parse_clip_file_to_dict(clip_file_path):
    clip = dict()
    with open(clip_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            clip[int(row['character_id'])] = clip.get(int(row['character_id']), list())
            clip[int(row['character_id'])].append(eval(row['frame_range']))
    return clip
