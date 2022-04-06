import re
import socket

from pathlib import Path
from typing import List

from webserver import WebServer

HOME_DIR = str(Path.cwd())
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

def parse_csv_files(file_dir: str) -> List[str]:
    with open(file_dir, "r") as f:
        un_parsed_all_media_types = f.readlines()

    parsed_media_extensions = [un_parsed_media_type.split(',')[0] for un_parsed_media_type
                               in un_parsed_all_media_types][1:]

    return parsed_media_extensions


# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

parsed_image_extensions = parse_csv_files("assets/image.csv")
parsed_image_extensions.append("ico")
parsed_text_extensions = parse_csv_files("assets/text.csv")
parsed_video_extensions = parse_csv_files("assets/video.csv")
parsed_audio_extensions = parse_csv_files("assets/audio.csv")
parsed_audio_extensions.append("mp3")

if __name__ == '__main__':
    while True:
        client_connection, client_address = server_socket.accept()

        request = client_connection.recv(1024).decode()
        webserver = WebServer(client_connection)
        print(request)

        headers = request.split('\n')
        filename = headers[0].split()[1]

        if filename == '/':
            filename = '/index.html'
        # for text/
        if filename.split(".")[-1] in parsed_text_extensions:
            webserver.load(filename, "text")
        # for image/
        elif filename.split(".")[-1] in parsed_image_extensions:
            webserver.load(filename, "image")
        # for video/
        elif filename.split(".")[-1] in parsed_video_extensions:
            webserver.load(filename, "video")
        # for audio/
        elif filename.split(".")[-1] in parsed_audio_extensions:
            webserver.load(filename, "audio")
        else:
            webserver.send_406_error()
        client_connection.close()
