import re
import socket

from pathlib import Path
from typing import List

HOME_DIR = str(Path.cwd())
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000


def is_x_extension(name: str, extension: str = "html") -> bool:
    java_script_regex = fr".*?(?=\.{extension})"
    return bool(re.findall(java_script_regex, name))


def read_and_respond_code(name: str, http_get_response: str, visitor: socket.socket) -> None:
    if Path(f"{HOME_DIR}/htdocs{name}").exists():
        with open(f"{HOME_DIR}/htdocs{name}") as fs:
            fs_data = fs.read()
        http_get_response += f"Content-Length: {len(fs_data)}\r\n\r\n{fs_data}"
        visitor.sendall(http_get_response.encode())
    else:
        send_404_error(visitor)


def read_and_respond_media(name: str, http_get_response: str, visitor: socket.socket) -> None:
    if Path(f"{HOME_DIR}/htdocs{name}").exists():
        with open(f"{HOME_DIR}/htdocs{name}", "rb") as fs:
            fs_data = fs.read()
        http_get_response += f"Content-Type: image/x-icon\r\nContent-Length: {len(fs_data)}\r\n\r\n"
        http_get_response = http_get_response.encode() + fs_data
        visitor.sendall(http_get_response)
    else:
        send_404_error(visitor)


def send_404_error(visitor: socket.socket) -> None:
    resp = 'HTTP/1.1 404 Not Found\r\nFile Not Found'
    visitor.sendall(resp.encode())


def send_501_error(visitor: socket.socket) -> None:
    resp = 'HTTP/1.1 501 Not Implemented To implement this type add it in the code line 77\r\n'
    visitor.send(resp.encode())


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
parsed_text_extensions = parse_csv_files("assets/text.csv")

if __name__ == '__main__':
    while True:
        client_connection, client_address = server_socket.accept()

        request = client_connection.recv(1024).decode()
        print(request)

        response = 'HTTP/1.1 200 OK\r\n'

        headers = request.split('\n')
        filename = headers[0].split()[1]

        if filename == '/':
            filename = '/index.html'

        # for text/
        if filename.split(".")[-1] in parsed_text_extensions:
            if is_x_extension(filename):
                response += "Content-Type: text/html\r\n"
                read_and_respond_code(filename, response, client_connection)
            elif is_x_extension(filename, extension="css"):
                response += "Content-Type: text/css\r\n"
                read_and_respond_code(filename, response, client_connection)
            elif is_x_extension(filename, extension="js"):
                response += "Content-Type: text/js\r\n"
                read_and_respond_code(filename, response, client_connection)
            elif is_x_extension(filename, extension="csv"):
                response += "Content-Type: text/csv\r\n"
                read_and_respond_code(filename, response, client_connection)
            elif is_x_extension(filename, extension="txt"):
                response += "Content-Type: text/plain\r\n"
                read_and_respond_code(filename, response, client_connection)
            elif is_x_extension(filename, extension="xml"):
                response += "Content-Type: text/xml\r\n"
                read_and_respond_code(filename, response, client_connection)
            else:
                send_501_error(client_connection)
        # for image/
        elif filename.split(".")[-1] in parsed_image_extensions:
            if is_x_extension(filename, extension="ico"):
                response += "Content-Type: image/x-icon\r\n"
                read_and_respond_media(filename, response, client_connection)
            elif is_x_extension(filename, extension="jpeg"):
                response += "Content-Type: image/jpeg\r\n"
                read_and_respond_media(filename, response, client_connection)
            elif is_x_extension(filename, extension="png"):
                response += "Content-Type: image/png\r\n"
                read_and_respond_media(filename, response, client_connection)
            elif is_x_extension(filename, extension="gif"):
                response += "Content-Type: image/gif\r\n"
                read_and_respond_media(filename, response, client_connection)
            else:
                send_501_error(client_connection)
        else:
            send_404_error(client_connection)
        client_connection.close()
