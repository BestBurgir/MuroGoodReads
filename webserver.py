from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
import re
import redis

mappings = [
    (r"^/books/(?P<book_id>\d+)$", "get_book"),
    (r"^/book/(?P<book_id>\d+)$", "get_book"),
    (r"^/$", "index"),
]

r=redis.StrictRedis(host="localhost",port=6379,db=0)

class WebRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.url_mapping_response()

    def url_mapping_response(self):
        for pattern, method in mappings:
            match = self.get_params(pattern, self.path)
            print(match)  # {'book_id': '1'}
            if match is not None:
                md = getattr(self, method)
                md(**match)
                return
            
        self.send_response(404)
        self.end_headers()
        self.wfile.write("Not Found".encode("utf-8"))

    def get_params(self, pattern, path):
        match = re.match(pattern, path)
        if match:
            return match.groupdict()

    def index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        index_page = "<h1>Bienvenidos a los Libros </h1>".encode("utf-8")
        self.wfile.write(index_page)

    def get_book(self, book_id):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        #book_info = f"<h1> Info de Libro {book_id} es correcto </h1>".encode("utf-8")
        book_info = r.get(f"book_id:{book_id}") or "No existe el libro".encode("utf-8")
        self.wfile.write(book_info)

print("Server starting.")
server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
server.serve_forever()
    
