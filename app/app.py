import json
import os
import uuid
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler, \
    SimpleHTTPRequestHandler
from os import listdir
from os.path import isfile, join

from loguru import logger

SERVER_ADDRESS = ('0.0.0.0', 8000)
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')
ALLOWED_LENGTH = (5 * 1024 * 1024)

logger.add('logs/app.log', format="[{time: YYYY-MM-DD HH:mm:ss}] | {level} | {message}")


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'Image Hosting Server/0.1'

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        if self.path in get_routes:
            get_routes[self.path](self)
        else:
            logger.warning(f'GET 404 {self.path}')
            self.send_response(404, 'Not Found')

    def get_index(self):
        logger.info(f'GET {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(open('static/index.html', 'rb').read())

    def get_images(self):
        logger.info(f'GET {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        images = [f for f in listdir('./images') if isfile(join('./images', f))]
        self.wfile.write(json.dumps({'images': images}).encode('utf-8'))

    def get_upload(self):
        logger.info(f'GET {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(open('static/upload.html', 'rb').read())

    def do_POST(self):
        if self.path in post_routes:
            post_routes[self.path](self)
        else:
            logger.warning(f'POST 404 {self.path}')
            self.send_response(405, 'Method Not Allowed')

    def post_upload(self):
        logger.info(f'POST {self.path}')
        content_length = int(self.headers.get('Content-Length'))
        if content_length > ALLOWED_LENGTH:
            logger.error('Payload Too Large')
            self.send_response(413, 'Payload Too Large')
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        data = form['image'].file

        _, ext = os.path.splitext(form['image'].filename)

        if ext not in ALLOWED_EXTENSIONS:
            logger.error('File type not allowed')
            self.send_response(400, 'File type not allowed')
            return

        image_id = uuid.uuid4()
        with open(f'images/{image_id}{ext}', 'wb') as f:
            f.write(data.read())

        logger.info(f'Upload success: {image_id}{ext}')
        self.send_response(301)
        self.send_header('Location', f'/images/{image_id}{ext}')
        self.end_headers()


get_routes = {
        '/': ImageHostingHandler.get_index,
        '/index.html': ImageHostingHandler.get_index,
        '/upload': ImageHostingHandler.get_upload,
        '/images': ImageHostingHandler.get_images,
        }

post_routes = {
    '/upload': ImageHostingHandler.post_upload,
}

def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)
    try:
        logger.info(f'Serving at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}')
        httpd.serve_forever()
    except Exception:
        pass
    finally:
        logger.info('Server stopped')
        httpd.server_close()


if __name__ == "__main__":
    run()
