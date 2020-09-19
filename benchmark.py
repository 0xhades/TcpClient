import time, hashlib, hmac, random, string, socket, ssl, uuid, json
from threading import Thread
from io import BytesIO
import gzip

def hmacsha256(_key, _message):
    byte_key = _key.encode('utf-8')
    message = _message.encode('utf-8')
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest()

def hex_digest(*args):
    m = hashlib.md5()
    m.update(b''.join([arg.encode('utf-8') for arg in args]))
    return m.hexdigest()

def generate_device_id(seed):
    volatile_seed = "12345"
    m = hashlib.md5()
    m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
    return 'android-' + m.hexdigest()[:16]

def RandomStringChars(n = 10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(n))

def randomStringWithChar(stringLength=10):
    letters = string.ascii_lowercase + '1234567890'
    result = ''.join(random.choice(letters) for i in range(stringLength - 1))
    return RandomStringChars(1) + result

username = randomStringWithChar(15)
password = randomStringWithChar(10)
IP = socket.gethostbyname('b.i.instagram.com')
url = f'https://{IP}/api/v1/accounts/login/'
_url = 'https://b.i.instagram.com/api/v1/accounts/login/'
KEY = 'c36436a942ea1dbb40d7f2d7d45280a620d991ce8c62fb4ce600f0a048c32c11'
USERAGENT = 'Instagram 107.0.0.27.121 Android (19/4.4.2; 480dpi; 1152x1920; Meizu; MX4; mx4; mt6595; en_US)'
headers = {}
data = {}
guid1 = str(uuid.uuid4())
guid2 =  str(uuid.uuid4())
device_id = generate_device_id(hex_digest(username, password))
results = {}
rloops = 0
sloops = 0
reloops = 0

class scop:

    def __init__(self):
        self.buffer = bytes()
        self.client = None
        self.firstReq = time.time()
        self.firstRes = time.time()

    def socke(self):

        target_host = "i.instagram.com" 
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        target_port = 443  # create a socket object 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client = context.wrap_socket(s, server_hostname=target_host) 

        body = f'ig_sig_key_version=4&signed_body=503bf1bc1f6d6d176003451330b3ae08c43ac43548beae987cc46d15cea142c1.{{"phone_id": "bed5b6c0-7526-4625-91ce-0ba5a34a8a27", "_csrftoken": "missing", "username": "{randomStringWithChar(15)}", "password": "what???!@", "device_id": "android-485bf80eec6f65c4", "guid": "801e56b0-68bd-4f71-b8d0-552f712fdb6a", "login_attempt_count": "0"}}'

        btsio = BytesIO()
        g = gzip.GzipFile(fileobj=btsio, mode='w')
        g.write(bytes(body, 'utf8'))
        g.close()
        gzipped_body = btsio.getvalue()

        '''  Edit postData use just username to be fast, not email checks etc.. '''

        
        request = f'POST /api/v1/accounts/login/ HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\r\nAccept-Language: en-US\r\nX-IG-Connection-Type: WIFI\r\nX-FB-HTTP-Engine: Liger\r\nConnection: Keep-Alive\r\nHost: i.instagram.com\r\nUser-Agent: Instagram 107.0.0.27.121 Android (19/4.4.2; 480dpi; 1152x1920; Meizu; MX4; mx4; mt6595; en_US)\r\nAccept: */*\r\nCookie2: $Version=1\r\nContent-Length: {len(gzipped_body)}\r\n\r\n'
        #request = f'POST /api/v1/accounts/login/ HTTP/1.1\r\nHost: i.instagram.com\r\nContent-Encoding: gzip\r\nCookie2: $Version=1\r\nAccept-Language: en-US\r\nAccept-Encoding: gzip, deflate\r\nUser-Agent: Instagram 107.0.0.27.121 Android (19/4.4.2; 480dpi; 1152x1920; Meizu; MX4; mx4; mt6595; en_US)\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\r\nX-IG-Connection-Type: WIFI\r\nX-FB-HTTP-Engine: Liger\r\nConnection: Keep-Alive\r\nContent-Length: {len(gzipped_body)}\r\n\r\n'
        #request = f'GET /api/v1/accounts/login/ HTTP/1.1\r\nHost: i.instagram.com\r\n\r\n'
        payloadBuffer = bytes(request, 'utf8') + gzipped_body

        #_r = f'POST /api/v1/accounts/login/ HTTP/1.1\r\nHost: i.instagram.com\r\nCookie2: $Version=1\r\nAccept-Language: en-US\r\nAccept-Encoding: gzip, deflate\r\nUser-Agent: Instagram 107.0.0.27.121 Android (19/4.4.2; 480dpi; 1152x1920; Meizu; MX4; mx4; mt6595; en_US)\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\r\nX-IG-Connection-Type: WIFI\r\nX-FB-HTTP-Engine: Liger\r\nConnection: Keep-Alive\r\nContent-Length: 350\r\n\r\n{body}'

        self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # connect the client 
        self.client.connect((target_host,target_port)) 
        #client.settimeout()
        self.client.setblocking(0)
        

        started_time = time.time()

        #client.settimeout(0.7)
        
        threads = []
        for i in range(sloops):
            try:
                self.client.write(payloadBuffer)
            except Exception as ex:
                pass
            # while True:
            #     try:
            #         client.send(payloadBuffer)
            #         break
            #     except socket.timeout as e:
            #         continue
            
            if i == 0: self.firstReq = time.time()
        
        t = Thread(target=self.listener)
        t.daemon = True
        t.start()

        print(f'time to writing/sending all requests: {time.time() - started_time}')
        t.join()
        print(f'Arrived at: {self.firstRes - self.firstReq}')
        print(f'time took all to arrive: {time.time() - started_time}')

    def listener(self):
        global counter
        lap = 0
        started_time = time.time()
        lastRes = time.time()

        while True:
            if lap == reloops:
                self.client.close()
                print(f'done:', time.time() - self.firstReq, '\n')
                results[0] = time.time() - self.firstReq
                return
            try:
                try:
                    self.buffer += self.client.read(4096)
                except Exception as ex: pass
                res = self.buffer.decode()
                if 'bad_password' in res or 'rate_limit' in res or 'invalid_user' in res or 'Content-Length' in res or '5xx Server Error' in res or 'account_created' in res or '</html>' in res: 
                    counter += 1  
                    print(res[:12], counter)
                    if lap == 0:
                        self.firstRes = time.time()
                        #print(f'elapsed {lap}:', time.time() - firstReq, '\n')
                        lastRes = self.firstRes
                    else:
                        #print(f'elapsed {lap}:', time.time() - lastRes, '\n')
                        lastRes = time.time()
                    lap += 1
                    self.buffer = bytes()
            except ssl.SSLWantReadError as ex:
                pass

counter = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    headers['User-Agent'] = USERAGENT
    headers['Accept'] = '*/*'
    headers['Cookie2'] = '$Version=1'
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    headers['X-IG-Connection-Type'] = 'WIFI'
    headers['Accept-Language'] = 'en-US'
    headers['X-FB-HTTP-Engine'] = 'Liger'
    headers['Accept-Encoding'] = 'gzip, deflate'
    headers['Connection'] = 'Keep-Alive'

    SignedBody = {}
    SignedBody['phone_id'] = guid1
    SignedBody['_csrftoken'] = 'missing'
    SignedBody['username'] = username
    SignedBody['password'] = password
    SignedBody['device_id'] = device_id
    SignedBody['guid'] = guid2
    SignedBody['login_attempt_count'] = '0'
    Message = json.dumps(SignedBody)
    _SignedBody = '{}.{}'.format(hmacsha256(KEY, Message), Message)
    payload = {}
    payload['ig_sig_key_version'] = '4'
    payload['signed_body'] = _SignedBody
    data = payload
    _data = f'ig_sig_key_version={data["ig_sig_key_version"]}&signed_body={data["signed_body"]}'

    reloops = int(input(bcolors.OKGREEN + 'r v loops: ' + bcolors.ENDC))
    #rloops = int(input(bcolors.OKGREEN + 'req fu loops: ' + bcolors.ENDC))
    sloops = int(input(bcolors.OKGREEN + 'secret loops: ' + bcolors.ENDC))

    print(bcolors.OKGREEN + 'secret: ' + bcolors.ENDC)
    print()

    ss = time.time()
    s = scop()
    s.socke()

    # threads = []
    # for i in range(threads):
    #     s = scop()
    #     t = Thread(target=s.socke)
    #     threads.append(t)
    #     t.setDaemon(1)
    #     time.sleep(0.1)
    #     t.start()
    # for i in threads: i.join()

    print('final sss: ', time.time() - ss, 's')

    print()
