import json
import requests
import uuid
import websocket

base_url = 'http://127.0.0.1:8888'
file_path = '/test.ipynb'

headers = {
    'Authorization': 'token ' + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
}

# connection test
response = requests.get(base_url + '/api/')
print(response.status_code, response.text)

# get target notebook codes
response = requests.get(base_url + '/api/contents/test.ipynb', headers=headers)
notebook = json.loads(response.text)
codes = [c['source'] for c in notebook['content']['cells'] if c['cell_type'] == 'code']

# create kernel
response = requests.post(base_url + '/api/kernels', headers=headers)
print(response.status_code, response.text)

# get kernel id
response = requests.get(base_url + '/api/kernels', headers=headers)
kernelId = json.loads(response.text)[0]['id']
print(kernelId)

# execute codes
## create web socket connection
wsUrl = 'ws://10.0.2.15:18888/api/kernels/' + kernelId + '/channels'
socket = websocket.create_connection(wsUrl, header=headers)
print(socket.status)

## send code
for code in codes:
    header = {
        'msg_type': 'execute_request',
        'msg_id': uuid.uuid1().hex,
        'session': uuid.uuid1().hex
    }
    
    message = json.dumps({
        'header': header,
        'parent_header': header,
        'metadata': {},
        'content': {
            'code': code,
            'silent': False
        }
    })
    socket.send(message)

outputs = []
replycount = 0

## receive execution results
for _ in range(len(codes)):
    msg_type, prev_msg_type = '', ''
    
    while msg_type != 'stream':
        if msg_type != prev_msg_type:
            print(prev_msg_type, '->', msg_type)
            prev_msg_type = msg_type
        
        response = json.loads(socket.recv())
        msg_type = response['msg_type']
    
    print(prev_msg_type, '->', msg_type)
    print(response['content']['text'])
    outputs.append(response['content']['text'])

## close web socket
socket.close()

## print result
print(outputs)

# delete kernel
response = requests.delete(base_url + '/api/kernels/' + kernelId, headers=headers)
print(response.status_code)
