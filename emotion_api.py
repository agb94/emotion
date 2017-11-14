import http.client, urllib.request, urllib.parse, urllib.error, base64
import time, sys, util

INTERVAL = 3.0 # msec
KEYS = [
    '6f2f9a102d684ba5a7d846fe3059e2da',
    '3e89ec1763ba43eabe03342f8b2e8710'
]
headers = {
    'Content-Type': 'application/octet-stream'
}
conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')

def get_emotion(image_file_path):
    try:
        with open(image_file_path, 'rb') as f:
            params = urllib.parse.urlencode({ 'data': f })
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        return data
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit()
    char_id = int(sys.argv[2])
    metadata = util.parse_metadata_file(sys.argv[1])
    metadata = list(filter(lambda r: r['character_id'] == char_id, metadata))
    metadata = sorted(metadata, key=lambda r: r['frame_number'])
    interval = INTERVAL / len(KEYS)
    for i, row in enumerate(metadata):
        img_path = row['image_file_path']
        key = KEYS[i % len(KEYS)]
        headers['Ocp-Apim-Subscription-Key'] = key
        print(img_path)
        print(get_emotion(img_path))
        time.sleep(interval)
