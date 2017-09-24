import httplib, urllib, base64
import requests, json

def main():
    headers = {}
    with open('Your image file directory.jpg', 'rb') as f:
        headers['Ocp-Apim-Subscription-Key'] = 'f32aa771906843c0b44abe75b1bc0e95'
        headers['Content-Type'] = 'application/octet-stream'
        req = requests.post('https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize', headers=headers, data=f)

    res_json = req.json()
    print json.dumps(res_json, indent=4)

if __name__ == '__main__':
    main()
