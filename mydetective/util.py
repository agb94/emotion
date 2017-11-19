import csv
import copy

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
                'image_file_path': row['image_file_path']
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
                'position': eval(row['position'])
            }
    return metadata

def write_metadata_file(metadata_file_path, metadata):
    sorted_metadata = sorted(metadata.items(), key=lambda t: (t[1]['frame_number'], t[0]))
    with open(metadata_file_path, 'w') as tsvfile:
        columns = ['image_file_path', 'msec', 'frame_number', 'position', 'character_id'] 
        tsvfile.write("\t".join(columns) + "\n")
        for k, v in sorted_metadata:
            tsvfile.write("{}\t{}\t{}\t{}\t{}\n".format(k, v['msec'], v['frame_number'], v['position'], v['character_id']))

def parse_overview_file(overview_file_path):
    overview = dict()
    with open(overview_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            overview[int(row['character_id'])]= {
                'appearance_count': int(row['appearance_count']),
                'level_of_importance': float(row['level_of_importance'])
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