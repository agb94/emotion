import sys

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

def character_analyzer(metadata_path, overview_path, clip_path, frame_interval=30):
    """
    Input:
        metadata_path:  The path of the metadata file
        overview_path:  The path of the overview file
        clip_path:      The path of the clip file
        frame_interval: The frame interval which user set (default value=30)
    Output:
        Analyzed result of characters
    Importance Metric:
        character count * (sum-to-1 normalized) average picture size
    """
    num_chars = distinct_characters(metadata_path)
    character_count = [0 for _ in range(num_chars)]
    average_size = [0 for _ in range(num_chars)]
    frame_list = [[] for _ in range(num_chars)]
    tmp = [[] for _ in range(num_chars)]
    importance = [0 for _ in range(num_chars)]
    
    previous_id = 0
    threshold = 20

    with open(overview_path, "w") as overview, open(clip_path, "w") as clip:
        with open(metadata_path, "r") as metadata_file:
            metadata_file.readline()
            for line in metadata_file:
                split = line.split("\t")
                current_frame = int(split[2])
                char_id = int(split[4][0])
                photo = eval(split[3])              # (x, y, w, h) tuple
                photo_size = photo[2] * photo[3]    # size of photo, w * h

                character_count[char_id - 1] += 1
                average_size[char_id - 1] += photo_size
                
                # For a video frame list
                if previous_id == char_id:
                    tmp[char_id - 1].append(current_frame)
                else:
                    # At first
                    if previous_id == 0:
                        tmp[char_id - 1].append(current_frame)
                    else:
                        if len(tmp[char_id - 1]) == 0:
                            tmp[char_id - 1].append(current_frame)
                        elif (current_frame - tmp[char_id - 1][-1]) / frame_interval <= threshold:
                            tmp[char_id - 1].append(current_frame)
                        else:
                            if tmp[char_id - 1][0] == tmp[char_id - 1][-1]:
                                frame_list[char_id - 1].append([tmp[char_id - 1][0]])
                            else:
                                frame_list[char_id - 1].append([tmp[char_id - 1][0], tmp[char_id - 1][-1]])
                            tmp[char_id - 1] = []
                            tmp[char_id - 1].append(current_frame)
                  
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

        average_size = [tot_size/float(cnt) for (tot_size, cnt) in zip(average_size, character_count)]
        normalizer = sum(average_size)
        importance = [avg_size/normalizer for avg_size in average_size]
        importance = [imp * cnt for (imp, cnt) in zip(importance, character_count)]
        
        # write on characters_overview.tsv
        writing = "Character ID\tAppearance Count\tLevel of Importance"
        overview.write(writing + "\n")

        for i in range(num_chars):
            line = "{}\t{}\t{}".format(i+1, character_count[i], importance[i])
            overview.write(line + "\n")
        
        # write on clip.tsv
        writing = "Character ID\tFrame Range"
        clip.write(writing + "\n")
        
        for i in range(len(frame_list)):
            for frame_range in frame_list[i]:
                line = "{}\t{}".format(i+1, frame_range)
                clip.write(line + "\n")

def main():
    if len(sys.argv) < 2:
        print ("[Usage] python character_analyzer.py [metadata_file_name]")
        sys.exit()
    # yellows1ep01-oracle.tsv
    metadata_path = sys.argv[1]
    overview_path = "characters_overview.tsv"
    clip_path = "clip.tsv"
    character_analyzer(metadata_path, overview_path, clip_path)

if __name__ == '__main__':
    main()
