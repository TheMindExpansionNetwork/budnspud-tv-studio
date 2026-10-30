#!/usr/bin/env python3
"""Loopback-only studio and explicitly configured loopback ComfyUI bridge."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from email.parser import BytesParser
from email.policy import default
import argparse, http.client, json, re, uuid

ROOT = Path(__file__).resolve().parent
REFS = [('start','137','image'), ('end','149','image'), ('background','150','image'), ('voice','151','audio'), ('music','152','audio')]
MAX_BODY = 100 * 1024 * 1024

def endpoint_port(value):
    try:
        url = urlsplit(value)
        port = url.port
    except ValueError:
        raise ValueError('Invalid ComfyUI endpoint.')
    if (url.scheme != 'http' or url.hostname not in ('localhost','127.0.0.1') or
        url.username is not None or url.password is not None or url.path not in ('','/') or
        url.query or url.fragment or not port or not 1 <= port <= 65535):
        raise ValueError('Use an HTTP loopback endpoint with an explicit port, such as http://127.0.0.1:8188.')
    return port

def comfy_post(port, path, data, content_type):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=30)
    try:
        conn.request('POST', path, body=data, headers={'Content-Type':content_type})
        response=conn.getresponse(); body=response.read(2*1024*1024+1)
        if response.status != 200 or len(body)>2*1024*1024:
            raise ValueError(f'ComfyUI {path} returned HTTP {response.status}. Check its logs and node configuration.')
        return json.loads(body)
    finally: conn.close()

def upload(port, filename, data):
    ext = Path(filename).suffix.lower()
    if not re.fullmatch(r'\.[a-z0-9]{1,8}', ext): ext = '.bin'
    filename = 'budnspud-' + uuid.uuid4().hex + ext
    boundary = '----budnspud' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + data +
            f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\ninput\r\n--{boundary}--\r\n'.encode())
    result=comfy_post(port,'/upload/image',body,'multipart/form-data; boundary='+boundary)
    name=result.get('name'); folder=result.get('subfolder','')
    if not isinstance(name,str) or not name or not isinstance(folder,str) or result.get('type','input') != 'input' or '/' in name or '\\' in name or name in ('.','..') or any(p in ('.','..') for p in folder.replace('\\','/').split('/') if p):
        raise ValueError('ComfyUI returned an invalid upload filename.')
    return f'{folder}/{name}' if folder else name

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' blob: data:; media-src 'self' blob:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    def do_POST(self):
        try:
            expected = f'127.0.0.1:{self.server.server_port}'
            host = self.headers.get('Host','')
            if host not in (expected, f'localhost:{self.server.server_port}') or self.headers.get('Origin') != 'http://'+host:
                raise ValueError('Invalid request origin.')
            if self.path != '/api/submit': raise ValueError('Unknown request.')
            length=int(self.headers.get('Content-Length','0'))
            content_type=self.headers.get('Content-Type','')
            if not 0 < length <= MAX_BODY or not content_type.startswith('multipart/form-data;'):
                raise ValueError('Invalid request or files exceed 100 MB total.')
            message=BytesParser(policy=default).parsebytes(b'Content-Type: '+content_type.encode()+b'\r\nMIME-Version: 1.0\r\n\r\n'+self.rfile.read(length))
            if not message.is_multipart(): raise ValueError('Invalid form data.')
            parts={}
            for part in message.iter_parts():
                key=part.get_param('name',header='content-disposition')
                if not key or key in parts: raise ValueError('Invalid form fields.')
                parts[key]=part
            def text(key): return parts[key].get_payload(decode=True).decode('utf-8')
            port=endpoint_port(text('endpoint')); prompt=text('prompt').strip()
            duration=int(text('duration')); seed=int(text('seed'))
            if not prompt or len(prompt)>100000 or not 1<=duration<=30 or not 0<=seed<=9007199254740991: raise ValueError('Invalid prompt, duration or seed.')
            files=[]
            for key,_,_ in REFS:
                p=parts[key]; name=p.get_filename(); data=p.get_payload(decode=True)
                if not name or not data: raise ValueError('All five reference files are required.')
                files.append((name,data))
            graph=json.loads((ROOT/'workflow.json').read_text())
            for (key,node,input_name),(name,data) in zip(REFS,files): graph[node]['inputs'][input_name]=upload(port,name,data)
            graph['138']['inputs']['value']=prompt; graph['132']['inputs']['value']=duration; graph['129']['inputs']['noise_seed']=seed
            result=comfy_post(port,'/prompt',json.dumps({'prompt':graph}).encode(),'application/json')
            if not isinstance(result.get('prompt_id'),str) or not result['prompt_id']: raise ValueError('ComfyUI did not return a prompt ID.')
            self.respond(200,{'prompt_id':result['prompt_id']})
        except (KeyError, ValueError, UnicodeError, json.JSONDecodeError) as e:
            self.respond(400,{'error':str(e) or 'Invalid request.'})
        except (OSError, http.client.HTTPException):
            self.respond(502,{'error':'Could not reach the local ComfyUI server. Check that it is running.'})
    def respond(self,status,data):
        body=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765); args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    print(f'Bud n Spud Studio: http://127.0.0.1:{server.server_port}/',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
