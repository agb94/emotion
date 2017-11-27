import mydetective
import argparse
parser = argparse.ArgumentParser(description='Input video files.')
parser.add_argument('video', metavar='V', type=str,
                    help='a video to analyze')
parser.add_argument('-K', type=int,
                    help='the number of clusters')
parser.add_argument('--interval', default=1, type=int,
                    help='time interval (sec) (default: 1)')
parser.add_argument('--metadata', type=str,
                    help='path of metadata file if exists')
parser.add_argument('--debugging', dest='debugging', action='store_true')
args = parser.parse_args()

module = "main"

def print_divider():
    print ("=================================================")

def print_msg(msg):
    print("[{}]: {}".format(module, msg))

def switch_module(module_name):
    global module
    module = module_name

print_divider()
# 1. Collector
switch_module("Collector")
print_msg("Start collecting faces")
if args.metadata:
    metadata_file_path = args.metadata
else:
    metadata_file_path = mydetective.collect(args.video, interval_sec = args.interval)
print_msg("{} created".format(metadata_file_path))

print_divider()
# 2. Identifier
switch_module("Identifier")
print_msg("Start clustering faces")
if args.K:
    K = mydetective.cluster(metadata_file_path, K=args.K, debugging=args.debugging)
else:
    K = mydetective.cluster(metadata_file_path, debugging=args.debugging)
print_msg("{} characters detected".format(K))

print_divider()
# 3. Character Analyzer
switch_module("Character Analyzer")
print_msg("Start analyzing characters")
overview_path, clip_path = mydetective.character_analyzer(metadata_file_path)
print_msg("{} created".format(overview_path))
print_msg("{} created".format(clip_path))
overview = mydetective.parse_overview_file(overview_path)
clip = mydetective.parse_clip_file_to_dict(clip_path)
ranking = 1
for char_id, features in overview:
    print_msg("Ranking #{}: Character {}".format(ranking, char_id))
    for feature in features:
        print_msg("- {}: {}".format(feature, features[feature]))
    print_msg("- clips: {}".format(clip[char_id]))
    ranking += 1

print_divider()
# 4. Relationship Analyzer
switch_module("Relationship Analyzer")
print_msg("Start analyzing relationship between characters")
relationship = mydetective.sorted_relationship(metadata_file_path)
for key, value in relationship:
    a, b = key
    print_msg ("- ({},{}): {}".format(a, b, value))

print_divider()
# 4. Emotional Changes Analyzer
switch_module("Emotional Changes Analyzer")
print_msg("Start analyzing emotional changes of a character")
emotions = mydetective.characters_emotion(metadata_file_path, 1)
print (emotions)
print_divider()
