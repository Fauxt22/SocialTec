import json

class JsonLineProtocol:
    def send(self, conn, obj: dict):
        """Enviar objeto como JSON"""
        data = (json.dumps(obj) + "\n").encode("utf-8")
        conn.sendall(data)

    def recv(self, file_obj):
        """Recibir objeto JSON"""
        line = file_obj.readline()
        if not line:
            return None
        return json.loads(line)