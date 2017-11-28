# Python 3
# import http.client, urllib.request, urllib.parse, urllib.error, base64
# Python 2
import httplib, urllib, base64
import os, time, sys, util

INTERVAL = 3.0 # msec
KEYS = [
    '6f2f9a102d684ba5a7d846fe3059e2da',
    'ea991c1ce78b4f1fae6bb9abbfa0b5ac',
    '21c1a6e336214f2dbd1d942afa11f20d',
    'cfb83bd65292431182e11a0155bc5802',
    'cdb295bb3d1749829482ad5e2d1f5ce3',
    '1a0f86313b8a4b1f8aaad6cf798ef989',
    '71b7ab691ca64e0ea40e6081ea1ff054',
    'ed8fa7a6c48541bcab8c344688533d7f',
    '22ad169ce7c8465396e2b561b2304764',
    '63457a99270b455bbf5529d3e2c72e19',
    '5f4952efbbe84bf185eca81fc35d16e7',
    '36b89b52075541618131d9b5f4d1dab5',
    'c99fc6b13ead49b5a5eedc6a33858e11',
    '0b349eb88d0a4f6bacdb9eb449446cb3',
    '986e879a3f0f4191a64e9503298ea289',
    'f546494a4f0f42cc9a7d45f47b4990b9',
    '790db3df13944294b33f97b278261b2d',
    'b3950d94bfe746f794aaa38fc4b2ca3e',
    '190c7e0f8f3146d3816765e01c100d53',
    '96a6de23ee6444729f429dbff30c30ec',
    '83192156d6904ca7bfec26ad3cdefde1',
    '45ae974484d945199be10e783a764359',
    'a64b7a4fd5e045ba88bee0fba877e64b',
    '5eff6a75cdcd4d59ad48ad74140de9b2',
    '2904824ec3b14bea80b0e119f610660c',
    '48964370c2b6476d957e7a460dc9a80e',
    'df76720d0532445caa562fe33def7f38',
    '92ef97c385634301ac06ce6b1067289e',
    'db27e49c7b0c4adb868fea9b9e6cd1dd',
    '164c523e5f66445cac7ec8fabef2dd8f',
    '6cdef4cf98624bd182a058fba63e2810',
    'b7ecf07a28fb47a5b4074b6d022c0aa2'
]
headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '6f2f9a102d684ba5a7d846fe3059e2da'
}

conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')

def get_emotion(image_file_path):
    try:
        with open(image_file_path, 'rb') as f:
            data = f.read()
        conn.request("POST", "/emotion/v1.0/recognize", data, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return eval(data)
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return None

def characters_emotion(metadata_path, character_id, crop_root_dir="crop/", limit=None):
    emotions = []
    metadata = util.parse_metadata_file(metadata_path)
    metadata = list(filter(lambda r: r['character_id'] == character_id, metadata))
    metadata = sorted(metadata, key=lambda r: r['frame_number'])
    interval = INTERVAL / len(KEYS)
    if limit:
        count = 0
    for i, row in enumerate(metadata):
        img_path = os.path.join(crop_root_dir, row['image_file_path'])
        key = KEYS[i % len(KEYS)]
        headers['Ocp-Apim-Subscription-Key'] = key
        emotion = get_emotion(img_path)
        if emotion:
            emotions.append((row['frame_number'], emotion))
        if limit:
            count += 1
            if count == limit:
                break
        if i + 1 != len(metadata):
            # last
            time.sleep(interval)
    return emotions

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit()
    characters_emotion(sys.argv[1], int(sys.argv[2]))
