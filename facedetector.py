# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
from json import JSONDecoder
import cv2
import time

http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
key = "your key"
secret = "your secret"
filepath = r"1.jpg"

boundary = '----------%s' % hex(int(time.time() * 1000))
data = []
data.append('--%s' % boundary)
data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
data.append(key)
data.append('--%s' % boundary)
data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
data.append(secret)
data.append('--%s' % boundary)
fr = open(filepath, 'rb')
data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
data.append('Content-Type: %s\r\n' % 'application/octet-stream')
data.append(fr.read())
fr.close()
data.append('--%s' % boundary)
data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
data.append('1')
data.append('--%s' % boundary)
data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
data.append(
    "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
data.append('--%s--\r\n' % boundary)

for i, d in enumerate(data):
    if isinstance(d, str):
        data[i] = d.encode('utf-8')

http_body = b'\r\n'.join(data)

# build http request
req = urllib.request.Request(url=http_url, data=http_body)

# header
req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

try:
    # post data to server
    resp = urllib.request.urlopen(req, timeout=5)
    # get response
    qrcont = resp.read().decode('utf-8')
    # if you want to load as json, you should decode first,
    # for example: json.loads(qrount.decode('utf-8'))

    req_dict = JSONDecoder().decode(qrcont)
    faces = req_dict['faces']
    face_rectangles = []
    attributes = []
    for face in faces:
        if 'face_rectangle' in face.keys():
            face_rectangles.append(face['face_rectangle'])
        if 'attributes' in face.keys():
            attributes.append(face['attributes'])

    frame = cv2.imread(filepath)

    for i, j in zip(face_rectangles, attributes):
        w = i['width']
        t = i['top']
        l = i['left']
        h = i['height']
        # 性别 + 年龄显示位置
        Msg_position = (l + 5 ,t - 5)
        # 性别 + 年龄信息
        Msg = ('M' if(j['gender']['value'] == 'Male') else 'F') + ' ' + str(j['age']['value'])
        # 在图片上显示性别和年龄信息
        cv2.putText(frame, Msg, Msg_position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
        # 用方框圈出脸部位置
        cv2.rectangle(frame, (l, t), (w + l, h + t), (0, 0, 255), 2)

    cv2.imshow('img', frame)
    cv2.waitKey(1)  # 刷新界面

    time.sleep(10)
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))