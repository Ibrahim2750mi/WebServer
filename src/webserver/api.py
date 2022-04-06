from pathlib import Path
import warnings

class WebServer:
    def __init__(self, client_connection, htdocs=""):
        self.client_connection = client_connection

        index_of_project = str(Path.cwd()).split("/").index("Webserver")

        self.HTDOCS_DIR = htdocs or '/'.join(str(Path.cwd()).split("/")[0: index_of_project + 1])

        self.response = 'HTTP/1.1 200 OK\r\n'

    def _send_404_error(self, filename: str) -> None:
        resp = 'HTTP/1.1 404 Not Found\r\nFile Not Found'
        self.client_connection.sendall(resp.encode())
        warnings.warn(f"404 File Not Found: {filename}")

    def send_406_error(self) -> None:
        resp = "HTTP/1.1 406 Type not supported\r\n"
        self.client_connection.send(resp.encode())
        warnings.warn("406 Type not supported")

    def _read_and_respond_media(self, filename: str) -> None:
        if not Path(f"{self.HTDOCS_DIR}/htdocs{filename}").exists():
            self._send_404_error(filename)
            return

        with open(f"{self.HTDOCS_DIR}/htdocs{filename}", "rb") as fs:
            fs_data = fs.read()
        self.response += f"Content-Type: image/x-icon\r\nContent-Length: {len(fs_data)}\r\n\r\n"
        self.response = self.response.encode() + fs_data
        self.client_connection.sendall(self.response)

    def _read_and_respond_text(self, filename: str) -> None:
        if not Path(f"{self.HTDOCS_DIR}/htdocs{filename}").exists():
            self._send_404_error(filename)
            return
        with open(f"{self.HTDOCS_DIR}/htdocs{filename}") as fs:
            fs_data = fs.read()
        self.response += f"Content-Length: {len(fs_data)}\r\n\r\n{fs_data}"

        self.client_connection.sendall(self.response.encode())


    def load(self, filename: str, request_type: str ="text") -> None:
        extension = Path(filename).suffix[1:]
        if request_type == "image":
            self.load_img(filename, extension)
        elif request_type == "text":
            self.load_text(filename, extension)
        elif request_type == "audio":
            self.load_audio(filename, extension)
        else:
            self.load_video(filename, extension)

    def load_img(self, filename: str, extension: str) -> None:
        if extension == "ico":
            extension = "x-icon"
        self.response += f"Content-Type: image/{extension}\r\n"
        self._read_and_respond_media(filename)

    def load_text(self, filename: str, extension: str) -> None:
        if extension == "txt":
            extension = "plain"
        self.response += f"Content-Type: text/{extension}\r\n"
        self._read_and_respond_text(filename)

    def load_video(self, filename: str, extension: str) -> None:
        self.response += f"Content-Type: video/{extension}\r\n"
        self._read_and_respond_media(filename)

    def load_audio(self, filename: str, extension: str) -> None:
        if extension == "mp3":
            extension = "mpeg"
        self.response += f"Content-Type: audio/{extension}\r\n"
        self._read_and_respond_media(filename)
