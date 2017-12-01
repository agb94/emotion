import operator
import math
from .util import *
from collections import Counter

def get_appearance(metadata):
    appearance = {}
    for character in set(list(map(lambda row: row['character_id'], metadata))):
        if character != -1:
            appearance[character] = list(map(lambda row: row['frame_number'], list(filter(lambda row: row['character_id'] == character, metadata))))
            appearance[character].sort()
    return appearance

def get_relationship(metadata):
    def relationship_key(a, b):
        if a < b:
            return (a, b)
        return (b, a)

    appearance = get_appearance(metadata)
    frequency_weight = {}
    total_apperance_count = 0
    for character in appearance:
        total_apperance_count += len(appearance[character])
        frequency_weight[character] = math.sqrt(1/float(len(appearance[character])))
    
    relationship = {}
    for character in appearance:
        for other in list(filter(lambda p: p != character and not relationship_key(character, p) in relationship, appearance)):
            key = relationship_key(character, other)
            relationship[key] = 0.0
    for character in appearance:
        for i in range(len(appearance[character]) - 1):
            start = appearance[character][i]
            end = appearance[character][i+1]
            if start == end:
                continue
            weight = 1/float((end-start))
            counter = Counter(list(map(lambda r: r['character_id'], filter(lambda r: r['character_id'] != -1 and r['character_id'] != character and r['frame_number'] in range(start, end+1), metadata))))
            for other in counter:
                key = relationship_key(character, other)
                relationship[key] += weight * frequency_weight[other]
    if len(relationship.values()) > 0:
        _max = max(relationship.values())
        if _max != 0:
            for key in relationship:
                relationship[key] /= _max
                relationship[key] *= 100
    return relationship

def sorted_relationship(metadata_file_path):
    metadata = parse_metadata_file(metadata_file_path)
    relationship = get_relationship(metadata)
    sorted_relationship = sorted(relationship.items(), key=operator.itemgetter(1))
    sorted_relationship.reverse()
    return sorted_relationship

if __name__ == "__main__":
    print (sorted_relationship('yellows1ep01-oracle.tsv'))
