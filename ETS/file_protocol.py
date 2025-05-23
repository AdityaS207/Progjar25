import os
import json
import base64

class FileProtocol:
    BASE_DIR = os.path.join(os.getcwd(), "files")

    def __init__(self):
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def list(self):
        files = os.listdir(self.BASE_DIR)
        return dict(status='OK', data=files)

    def get(self, params=[]):
        try:
            filename = params[0]
            filepath = os.path.join(self.BASE_DIR, filename)
            with open(filepath, 'rb') as f:
                content = f.read()
            encoded = base64.b64encode(content).decode()
            return dict(status='OK', data=encoded)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filedata = params[1]
            filepath = os.path.join(self.BASE_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(filedata))
            return dict(status='OK', data='File berhasil diunggah')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            filepath = os.path.join(self.BASE_DIR, filename)
            os.remove(filepath)
            return dict(status='OK', data='File berhasil dihapus')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def proses_string(self, string_request):
        c = string_request.split(" ", 1)
        command = c[0].upper()
        if command == 'LIST':
            return json.dumps(self.list())
        elif command == 'GET':
            return json.dumps(self.get([c[1]]))
        elif command == 'UPLOAD':
            filename, filedata = c[1].split("|||", 1)
            return json.dumps(self.upload([filename, filedata]))
        elif command == 'DELETE':
            return json.dumps(self.delete([c[1]]))
        else:
            return json.dumps(dict(status='ERROR', data='request tidak dikenali'))
