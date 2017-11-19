import os, sys
from .util import *

def distinct_characters(metadata_path):
    """
    Input:
        metadata_path:  The path of the metadata file
    Output:
        num_chars:      The number of characters (in video)
    """
    num_chars = 0
    with open(metadata_path, "r") as metadata_file:
        metadata_file.readline()    # First line is an info line.
        for line in metadata_file:
            split = line.split("\t")
            char_id = int(split[4][0])

            if char_id > num_chars:
                num_chars = char_id
            else:
                continue

    return num_chars

def character_analyzer(metadata_path, frame_interval=30):
    """
    Input:
        metadata_path:  The path of the metadata file
        (deleted)overview_path:  The path of the overview file
        (deletec)clip_path:      The path of the clip file
        frame_interval: The frame interval which user set (default value=30)
    Output:
        Analyzed result of characters
    Importance Metric:
        character count * (sum-to-1 normalized) average picture size
    """
    path, extension = os.path.splitext(metadata_path)
    overview_path = path + '-characters' + extension
    clip_path = path + '-clip' + extension

    metadata = parse_metadata_file(metadata_path)
    char_ids = list(filter(lambda _id: _id != -1, set(map(lambda r: r['character_id'], metadata))))

    #num_chars = distinct_characters(metadata_path)
    character_count = { i: 0 for i in char_ids }
    average_size = { i: 0 for i in char_ids }
    frame_list = { i: list() for i in char_ids }
    tmp = { i: list() for i in char_ids }
    importance = { i: 0 for i in char_ids }
    
    previous_id = 0
    threshold = 20

    with open(overview_path, "w") as overview, open(clip_path, "w") as clip:
        for row in filter(lambda r: r['character_id'] != -1, metadata):
            current_frame = row["frame_number"]
            char_id = row["character_id"]
            position = row["position"]          # (x, y, w, h) tuple
            # photo = eval(split[3])              # (x, y, w, h) tuple
            photo_size = position[2] * position[3]    # size of photo, w * h

            character_count[char_id] += 1
            average_size[char_id] += photo_size
            
            # for a video frame list
            if previous_id == char_id:
                tmp[char_id].append(current_frame)
            else:
                # at first
                if previous_id == 0:
                    tmp[char_id].append(current_frame)
                else:
                    if len(tmp[char_id]) == 0:
                        tmp[char_id].append(current_frame)
                    elif (current_frame - tmp[char_id][-1]) / frame_interval <= threshold:
                        tmp[char_id].append(current_frame)
                    else:
                        if tmp[char_id][0] == tmp[char_id][-1]:
                            frame_list[char_id].append([tmp[char_id][0]])
                        else:
                            frame_list[char_id].append([tmp[char_id][0], tmp[char_id][-1]])
                        tmp[char_id] = []
                        tmp[char_id].append(current_frame)
              
            previous_id = char_id

        # Handling remaining frame list
        for i in range(len(tmp)):
            if len(tmp[i]) != 0:
                if tmp[i][0] == tmp[i][-1]:
                    frame_list[i].append([tmp[i][0]])
                else:
                    frame_list[i].append([tmp[i][0], tmp[i][-1]])
            else:
                continue

        normalizer = 0
        for char_id in char_ids:
            average_size[char_id] /= float(character_count[char_id])
            normalizer += average_size[char_id]
        for char_id in char_ids:
            importance[char_id] = average_size[char_id]/normalizer
            importance[char_id] *= character_count[char_id]
        
        # write on characters_overview.tsv
        writing = "character_id\tappearance_count\tlevel_of_importance"
        overview.write(writing + "\n")

        for char_id in char_ids:
            line = "{}\t{}\t{}".format(char_id, character_count[char_id], importance[char_id])
            overview.write(line + "\n")
        
        # write on clip.tsv
        writing = "character_id\tframe_range"
        clip.write(writing + "\n")
        
        for i in range(len(frame_list)):
            for frame_range in frame_list[i]:
                line = "{}\t{}".format(i, tuple(frame_range))
                clip.write(line + "\n")

        return (overview_path, clip_path)

def main():
    if len(sys.argv) < 2:
        print ("[Usage] python character_analyzer.py [metadata_file_name]")
        sys.exit()
    # yellows1ep01-oracle.tsv
    metadata_path = sys.argv[1]
    character_analyzer(metadata_path)

if __name__ == '__main__':
    main()