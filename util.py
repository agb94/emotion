import csv
import copy

def parse_metadata_file(metadata_file_path):
    metadata = list()
    with open(metadata_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            metadata.append({
                'character_id': int(row['Character ID']),
                'msec': float(row['MSEC']),
                'frame_number': int(row['Frame Number']),
                'position': eval(row['Position']),
                'image_file_path': row['Image File Path']
            })
    return metadata

def parse_metadata_file_to_dict(metadata_file_path):
    metadata = dict()
    with open(metadata_file_path) as tsvfile:
        rows = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in rows:
            metadata[row['Image File Path']]= {
                'character_id': int(row['Character ID']),
                'msec': float(row['MSEC']),
                'frame_number': int(row['Frame Number']),
                'position': eval(row['Position'])
            }
    return metadata
