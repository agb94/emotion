import operator
import math
from .util import *

def get_appearance(metadata):
    appearance = {}
    for character in set(list(map(lambda row: row['character_id'], metadata))):
        if character != -1:
            appearance[character] = list(map(lambda row: row['frame_number'], list(filter(lambda row: row['character_id'] == character, metadata))))
            appearance[character].sort()
    return appearance

def get_relationship(appearance):
    def relationship_key(a, b):
        if a < b:
            return (a, b)
        return (b, a)

    total_apperance_count = 0
    for character in appearance:
        total_apperance_count += len(appearance[character])
    
    relationship = {}
    for character in appearance:
        for other in appearance:
            if character == other:
                continue
            key = relationship_key(character, other)
            if key in relationship:
                continue
            else:
                relationship[key] = 0.0
            for frame in appearance[character]:
                if frame in appearance[other]:
#                    relationship[key] += float(len(appearance[character]) + len(appearance[other])) / total_apperance_count
                    continue

    for character in appearance:
        for i in range(len(appearance[character]) - 1):
            start = appearance[character][i]
            end = appearance[character][i+1]
            if start == end:
                continue
            weight = 1/float((end-start))
            for other in appearance:
                if character == other:
                    continue
                key = relationship_key(character, other)
                relationship[key] += weight * len(list(filter(lambda f: f in range(start, end+1), appearance[other])))
    if len(relationship.values()) > 0:
        _max = max(relationship.values())
        for key in relationship:
            relationship[key] /= _max
            relationship[key] *= 100
    return relationship

def sorted_relationship(metadata_file_path):
    metadata = parse_metadata_file(metadata_file_path)
    appearance = get_appearance(metadata)
    relationship = get_relationship(appearance)
    sorted_relationship = sorted(relationship.items(), key=operator.itemgetter(1))
    sorted_relationship.reverse()
    return sorted_relationship

if __name__ == "__main__":
    print (sorted_relationship('yellows1ep01-oracle.tsv'))
