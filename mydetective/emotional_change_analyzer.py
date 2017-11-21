# Python 3
# import http.client, urllib.request, urllib.parse, urllib.error, base64
# Python 2
import httplib, urllib, base64
import os, time, sys, util

INTERVAL = 3.0 # msec
KEYS = [
    '6f2f9a102d684ba5a7d846fe3059e2da'
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

def characters_emotion(metadata_path, character_id, crop_root_dir="crop/"):
    emotions = []
    metadata = util.parse_metadata_file(metadata_path)
    metadata = list(filter(lambda r: r['character_id'] == character_id, metadata))
    metadata = sorted(metadata, key=lambda r: r['frame_number'])
    interval = INTERVAL / len(KEYS)
    for i, row in enumerate(metadata):
        img_path = os.path.join(crop_root_dir, row['image_file_path'])
        key = KEYS[i % len(KEYS)]
        headers['Ocp-Apim-Subscription-Key'] = key
        emotion = get_emotion(img_path)
        if emotion:
            emotions.append((row['frame_number'], emotion))
        time.sleep(interval)
    return emotions

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit()
    characters_emotion(sys.argv[1], int(sys.argv[2]))
