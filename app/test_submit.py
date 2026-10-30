import json, threading, unittest, urllib.request, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path
import server

class MockComfy(BaseHTTPRequestHandler):
    uploads = []
    graph = None
    def log_message(self, *args): pass
    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        if self.path == '/upload/image':
            self.__class__.uploads.append(body)
            response = {'name': f'ref{len(self.uploads)}.bin', 'subfolder': '', 'type': 'input'}
        elif self.path == '/prompt':
            self.__class__.graph = json.loads(body)['prompt']
            response = {'prompt_id': 'mock-job-123'}
        else:
            self.send_error(404); return
        data = json.dumps(response).encode(); self.send_response(200); self.end_headers(); self.wfile.write(data)

class SubmissionTest(unittest.TestCase):
    def test_endpoint_rejects_remote_and_credentials(self):
        for url in ('http://example.com:8188','http://127.0.0.2:8188','http://user:pass@127.0.0.1:8188','http://127.0.0.1:8188/path','https://127.0.0.1:8188','http://127.0.0.1:8188/?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError): server.endpoint_port(url)
        self.assertEqual(server.endpoint_port('http://localhost:8188'),8188)

    def test_template_matches_executed_graph_connections(self):
        graph=json.loads((Path(__file__).parent/'workflow.json').read_text())
        source=Path('/home/ubuntu/jimsky/projects/budnspud-life-advice-blooper/workflows/executed/video.json')
        if not source.exists(): self.skipTest('Executed source graph is not present on this machine')
        original=json.loads(source.read_text())
        self.assertEqual(set(graph),set(original))
        for node in original:
            self.assertEqual(graph[node]['class_type'],original[node]['class_type'])
            for key,value in original[node]['inputs'].items():
                if isinstance(value,list): self.assertEqual(graph[node]['inputs'][key],value)

    def test_five_uploads_and_prompt(self):
        MockComfy.uploads=[]; MockComfy.graph=None
        comfy=ThreadingHTTPServer(('127.0.0.1',0),MockComfy)
        app=ThreadingHTTPServer(('127.0.0.1',0),partial(server.Handler,directory=str(Path(__file__).parent)))
        for s in (comfy,app): threading.Thread(target=s.serve_forever,daemon=True).start()
        try:
            b='----'+uuid.uuid4().hex; parts=[]
            def field(name,value,filename=None):
                disposition=f'Content-Disposition: form-data; name="{name}"'+(f'; filename="{filename}"' if filename else '')
                parts.append(f'--{b}\r\n{disposition}\r\n\r\n'.encode()+value+b'\r\n')
            field('endpoint',f'http://127.0.0.1:{comfy.server_port}'.encode())
            field('prompt',b'A scene'); field('duration',b'5'); field('seed',b'42')
            for name in ('start','end','background','voice','music'): field(name,name.encode(),name+'.bin')
            data=b''.join(parts)+f'--{b}--\r\n'.encode()
            req=urllib.request.Request(f'http://127.0.0.1:{app.server_port}/api/submit',data,headers={'Content-Type':f'multipart/form-data; boundary={b}','Origin':f'http://127.0.0.1:{app.server_port}'})
            result=json.load(urllib.request.urlopen(req)); self.assertEqual(result['prompt_id'],'mock-job-123')
            self.assertEqual(len(MockComfy.uploads),5)
            graph=MockComfy.graph
            for index,node in enumerate(('137','149','150','151','152'),1):
                self.assertEqual(graph[node]['inputs']['image' if index<=3 else 'audio'],f'ref{index}.bin')
            self.assertEqual(graph['138']['inputs']['value'],'A scene')
            self.assertEqual(graph['132']['inputs']['value'],5)
            self.assertEqual(graph['129']['inputs']['noise_seed'],42)
            self.assertEqual(graph['136']['inputs']['ref_audios.ref_audio_1'],['152',0])
        finally:
            for s in (app,comfy): s.shutdown(); s.server_close()

if __name__ == '__main__': unittest.main()
