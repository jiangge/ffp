# -*- coding: utf-8 -*-
from flask import Flask, Response, abort, send_from_directory, redirect, request
from mimetypes import MimeTypes
import requests, os, re

app = Flask(__name__)
app.debug = False
CHUNK_SIZE = 1024*1024
mime = MimeTypes()


@app.route('/<path:url>')
def proxy(url):
    r = requests.get(url, stream=True,params=request.args)
    if r.status_code != 200:
        abort(r.status_code)
    mime_type = mime.guess_type(url)
    def generate():
        for chunk in r.iter_content(CHUNK_SIZE):
            yield chunk
    responseHeaders=[]
    try:
        responseHeaders.append(('Content-Length',dict(r.raw.headers.items())['Content-Length']))
    except:
        pass
    try:
        responseHeaders.append(('Content-Type',dict(r.raw.headers.items())['Content-Type']))
    except:
        pass
    return Response(generate(),headers=responseHeaders,mimetype=mime_type[0])

@app.route('/r/<path:url>')
def replace(url):
    r = requests.get(url,params=request.args)
    responseHeaders=r.raw.headers.items()
    if r.status_code != 200:
        abort(r.status_code)
    mime_type = mime.guess_type(url)
    requestHeaders=request.headers
    host=requestHeaders["Host"]
    pattern = re.compile(r'http(s:\/\/|:\/\/)')
    postRegex=re.sub(pattern,"https://"+host+"/http"+r'\1', r.text)
    return Response(postRegex,headers=responseHeaders, mimetype=mime_type[0])

@app.route('/')
def index():
    return redirect('https://github.com/YUX-IO/ffp', code=302)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.errorhandler(500)
def internal_server_rror(e):
	return redirect('https://github.com/YUX-IO/ffp', code=302)

@app.errorhandler(400)
def internal_server_rror(e):
	return redirect('https://github.com/YUX-IO/ffp', code=302)

if __name__ == '__main__':
    app.run()