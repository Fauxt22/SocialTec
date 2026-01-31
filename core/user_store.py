import pickle
import os
from passlib.hash import sha256_crypt

class UserStore:
    def __init__(self):
        self.users = {}
        self.friend_requests = {}  # Para usuario: [solicitudes recibidas]
        self._load()
    
    def _load(self):
        # Crear directorio data si no existe
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists("data/users.dat"):
            try:
                with open("data/users.dat", "rb") as f:
                    data = pickle.load(f)
                    self.users = data.get('users', {})
                    self.friend_requests = data.get('friend_requests', {})
            except Exception as e:
                print(f"Error cargando datos: {e}")
                self.users = {}
                self.friend_requests = {}
        else:
            self.users = {}
            self.friend_requests = {}
    
    def _save(self):
        # Crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        data = {
            'users': self.users,
            'friend_requests': self.friend_requests
        }
        with open("data/users.dat", "wb") as f:
            pickle.dump(data, f)
    
    def register(self, username, nombre, apellido, foto, password):
        username = username.strip()
        if not username or not password:
            return False, "Faltan datos"
        
        if username in self.users:
            return False, "Usuario ya existe"
        
        hashed = sha256_crypt.hash(password)
        
        self.users[username] = {
            "username": username,
            "nombre": nombre,
            "apellido": apellido,
            "foto": foto,
            "password": hashed,
            "bio": "¡Hola! Soy nuevo en SocialTec 🌟",
            "created_at": "2024"
        }
        
        self.friend_requests[username] = []
        
        self._save()
        return True, None
    
    def login(self, username, password):
        username = username.strip()
        
        if username not in self.users:
            return False, "Usuario no existe"
        
        if not sha256_crypt.verify(password, self.users[username]["password"]):
            return False, "Contraseña incorrecta"
        
        return True, None
    
    def exists(self, username):
        return username in self.users
    
    def get_profile(self, username):
        return self.users.get(username)
    
    def all_usernames(self):
        return list(self.users.keys())
    
    def send_friend_request(self, from_user, to_user):
        if from_user not in self.users or to_user not in self.users:
            return False, "Usuario no existe"
        
        if from_user == to_user:
            return False, "No puedes enviarte solicitud a ti mismo"
        
        if to_user not in self.friend_requests:
            self.friend_requests[to_user] = []
        
        # Verificar si ya hay solicitud pendiente
        if from_user in self.friend_requests[to_user]:
            return False, "Ya enviaste una solicitud"
        
        self.friend_requests[to_user].append(from_user)
        self._save()
        return True, "Solicitud enviada"
    
    def get_friend_requests(self, username):
        return self.friend_requests.get(username, [])
    
    def accept_friend_request(self, user, requester):
        if user not in self.friend_requests:
            return False, "No hay solicitudes"
        
        if requester not in self.friend_requests[user]:
            return False, "Solicitud no encontrada"
        
        self.friend_requests[user].remove(requester)
        self._save()
        return True, "Solicitud aceptada"
    
    def reject_friend_request(self, user, requester):
        if user in self.friend_requests and requester in self.friend_requests[user]:
            self.friend_requests[user].remove(requester)
            self._save()
            return True, "Solicitud rechazada"
        return False, "Solicitud no encontrada"
    
    def update_bio(self, username, bio):
        if username in self.users:
            self.users[username]["bio"] = bio
            self._save()
            return True
        return False