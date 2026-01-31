# server.py - VERSIÓN COMPLETA CORREGIDA CON ESTADÍSTICAS ACTUALIZABLES
import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from datetime import datetime
import hashlib

from core.user_store import UserStore
from core.social_graph import SocialGraph
from core.MergeSort import MergeSorter
from core.Protocol import JsonLineProtocol

HOST = "127.0.0.1"
PORT = 5000

class SocialTecServer:
    def __init__(self):
        self.users = UserStore()
        self.graph = SocialGraph()
        self.sorter = MergeSorter()
        self.lock = threading.Lock()
        
        self._create_sample_data()
        self.create_gui()
        
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()
        
        self.root.mainloop()
    
    def _create_sample_data(self):
        """Crear datos de ejemplo"""
        print("Inicializando datos de muestra...")
        
        sample_users = [
            ("ana", "Ana", "Lopez", "", "ana123", "Me encanta viajar ✈️"),
            ("luis", "Luis", "Perez", "", "luis456", "Programador y músico 🎸"),
            ("carlos", "Carlos", "Garcia", "", "carlos789", "Amante del deporte ⚽"),
            ("maria", "Maria", "Torres", "", "maria000", "Fotógrafa profesional 📷"),
            ("juan", "Juan", "Rodriguez", "", "juan111", "Estudiante de ingeniería 🎓"),
        ]
        
        for user, nom, ape, foto, pwd, bio in sample_users:
            if not self.users.exists(user):
                print(f"Creando usuario: {user}")
                # Hashear la contraseña de ejemplo
                password_hash = hashlib.sha256(pwd.encode()).hexdigest()
                ok, err = self.users.register(user, nom, ape, foto, password_hash)
                if ok:
                    user_data = self.users.get_profile(user)
                    if user_data:
                        user_data["bio"] = bio
        
        for username in self.users.all_usernames():
            self.graph.ensure_user(username)
        
        friendships = [
            ("ana", "luis"),
            ("luis", "carlos"),
            ("carlos", "maria"),
            ("ana", "juan"),
        ]
        
        for a, b in friendships:
            if self.users.exists(a) and self.users.exists(b):
                print(f"Creando amistad: {a} <-> {b}")
                self.graph.add_friendship(a, b)
        
        print("\n=== VERIFICACIÓN DEL GRAFO ===")
        for user in sorted(self.graph.adj.keys()):
            amigos = sorted(self.graph.adj.get(user, set()))
            print(f"  {user}: {amigos}")
        print("==============================\n")
    
    def run_server(self):
        """Ejecutar servidor TCP"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        
        print("=" * 60)
        print("🚀 SOCIALTEC SERVER")
        print("=" * 60)
        print(f"📡 Servidor: {HOST}:{PORT}")
        print(f"👥 Usuarios: {len(self.users.all_usernames())}")
        print(f"🤝 Amistades: {sum(len(v) for v in self.graph.adj.values()) // 2}")
        print("\n📋 Usuarios de prueba:")
        for user in ["ana", "luis", "carlos", "maria", "juan"]:
            if user in self.users.all_usernames():
                print(f"   • {user} / {user}123")
        print("=" * 60)
        
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
            thread.start()
    
    def handle_client(self, conn, addr):
        """Manejar cliente conectado usando Protocol"""
        try:
            protocol = JsonLineProtocol()
            
            while True:
                try:
                    req = protocol.recv(conn.makefile("r", encoding="utf-8"))
                    if not req:
                        break
                    
                    with self.lock:
                        resp = self.handle_request(req)
                    
                    protocol.send(conn, resp)
                    
                except Exception as e:
                    error_resp = {"status": "error", "msg": f"Error interno: {str(e)}"}
                    protocol.send(conn, error_resp)
                    break
                    
        except Exception as e:
            print(f"Error con cliente {addr}: {e}")
        finally:
            try:
                conn.close()
            except:
                pass
    
    def handle_request(self, req):
        """Procesar petición del cliente"""
        tipo = req.get("type")
        
        if tipo == "ping":
            return {"status": "ok", "msg": "Servidor activo"}
        
        elif tipo == "register":
            return self.handle_register(req)
        
        elif tipo == "login":
            return self.handle_login(req)
        
        elif tipo == "get_profile":
            return self.handle_get_profile(req)
        
        elif tipo == "search_users":
            return self.handle_search_users(req)
        
        elif tipo == "send_friend_request":
            return self.handle_send_friend_request(req)
        
        elif tipo == "get_friend_requests":
            return self.handle_get_friend_requests(req)
        
        elif tipo == "accept_friend_request":
            return self.handle_accept_friend_request(req)
        
        elif tipo == "reject_friend_request":
            return self.handle_reject_friend_request(req)
        
        elif tipo == "remove_friend":
            return self.handle_remove_friend(req)
        
        elif tipo == "get_path":
            return self.handle_get_path(req)
        
        elif tipo == "get_stats":
            return self.handle_get_stats(req)
        
        elif tipo == "get_all_users":
            return self.handle_get_all_users(req)
        
        else:
            return {"status": "error", "msg": f"Tipo desconocido: {tipo}"}
    
    def handle_register(self, req):
        """Manejar registro de usuario"""
        ok, err = self.users.register(
            req.get("username"),
            req.get("nombre"),
            req.get("apellido"),
            req.get("foto", ""),
            req.get("password")  # Ya viene hasheado del cliente
        )
        if ok:
            self.graph.ensure_user(req.get("username"))
            return {"status": "ok", "username": req.get("username")}
        return {"status": "error", "msg": err}
    
    def handle_login(self, req):
        """Manejar inicio de sesión - VERIFICACIÓN CON PASSLIB"""
        username = req.get("username")
        password_hash = req.get("password")  # Recibir hash del cliente
        
        ok, err = self.users.login(username, password_hash)
        if ok:
            user_data = self.users.get_profile(username)
            return {
                "status": "ok", 
                "username": username,
                "nombre": user_data["nombre"],
                "apellido": user_data["apellido"],
                "foto": user_data["foto"],
                "bio": user_data.get("bio", "")
            }
        return {"status": "error", "msg": err}
    
    def handle_get_profile(self, req):
        """Obtener perfil de usuario"""
        username = req.get("username")
        user = self.users.get_profile(username)
        
        if not user:
            return {"status": "error", "msg": "Usuario no existe"}
        
        friends = self.graph.friends_of(username)
        friends_sorted = self.sorter.sort(friends)
        
        return {
            "status": "ok",
            "profile": {
                "username": user["username"],
                "nombre": user["nombre"],
                "apellido": user["apellido"],
                "foto": user["foto"],
                "bio": user.get("bio", ""),
                "amigos": friends_sorted,
                "friends_count": len(friends)
            }
        }
    
    def handle_search_users(self, req):
        """Buscar usuarios"""
        query = req.get("query", "").lower()
        searcher = req.get("searcher", "")
        
        results = []
        for username in self.users.all_usernames():
            user_data = self.users.get_profile(username)
            if (query in username.lower() or 
                query in user_data["nombre"].lower() or 
                query in user_data["apellido"].lower()):
                
                are_friends = username in self.graph.adj.get(searcher, set())
                
                results.append({
                    "username": username,
                    "nombre": user_data["nombre"],
                    "apellido": user_data["apellido"],
                    "bio": user_data.get("bio", ""),
                    "are_friends": are_friends
                })
        
        return {"status": "ok", "results": results}
    
    def handle_send_friend_request(self, req):
        """Enviar solicitud de amistad"""
        ok, err = self.users.send_friend_request(
            req.get("from"),
            req.get("to")
        )
        if ok:
            return {"status": "ok", "msg": err}
        return {"status": "error", "msg": err}
    
    def handle_get_friend_requests(self, req):
        """Obtener solicitudes de amistad"""
        username = req.get("username")
        requests = self.users.get_friend_requests(username)
        
        requests_info = []
        for requester in requests:
            user_data = self.users.get_profile(requester)
            if user_data:
                requests_info.append({
                    "username": requester,
                    "nombre": user_data["nombre"],
                    "apellido": user_data["apellido"],
                    "bio": user_data.get("bio", "")
                })
        
        return {"status": "ok", "requests": requests_info}
    
    def handle_accept_friend_request(self, req):
        """Aceptar solicitud de amistad"""
        user = req.get("username")
        requester = req.get("requester")
        
        ok, err = self.users.accept_friend_request(user, requester)
        if not ok:
            return {"status": "error", "msg": err}
        
        ok, err = self.graph.add_friendship(user, requester)
        if ok:
            return {"status": "ok", "msg": "Ahora son amigos"}
        return {"status": "error", "msg": err}
    
    def handle_reject_friend_request(self, req):
        """Rechazar solicitud de amistad"""
        ok, err = self.users.reject_friend_request(
            req.get("username"),
            req.get("requester")
        )
        if ok:
            return {"status": "ok", "msg": err}
        return {"status": "error", "msg": err}
    
    def handle_remove_friend(self, req):
        """Eliminar amistad"""
        a = req.get("a")
        b = req.get("b")
        
        if not self.users.exists(a) or not self.users.exists(b):
            return {"status": "error", "msg": "Usuario(s) no existen"}
        
        ok, err = self.graph.remove_friendship(a, b)
        if ok:
            return {"status": "ok", "msg": "Amistad eliminada"}
        return {"status": "error", "msg": err}
    
    def handle_get_path(self, req):
        """Obtener camino entre usuarios"""
        start = req.get("start")
        goal = req.get("goal")
        
        if not self.users.exists(start) or not self.users.exists(goal):
            return {"status": "error", "msg": "Usuario(s) no existen"}
        
        path = self.graph.path_bfs(start, goal)
        
        if path is None:
            return {"status": "ok", "exists": False, "path": []}
        return {"status": "ok", "exists": True, "path": path}
    
    def handle_get_stats(self, req):
        """Obtener estadísticas - VERSIÓN CORREGIDA"""
        stats = self.graph.stats()  # ¡LLAMADA SIN PARÁMETROS!
        return {"status": "ok", "stats": stats}
    
    def handle_get_all_users(self, req):
        """Obtener todos los usuarios"""
        users = []
        for username in self.users.all_usernames():
            user_data = self.users.get_profile(username)
            users.append({
                "username": username,
                "nombre": user_data["nombre"],
                "apellido": user_data["apellido"],
                "bio": user_data.get("bio", "")
            })
        return {"status": "ok", "users": users}
    
    def create_gui(self):
        """Crear interfaz gráfica del servidor"""
        self.root = tk.Tk()
        self.root.title("SocialTec - Panel de Administración")
        self.root.geometry("900x700")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_dashboard = tk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text="📊 Dashboard")
        
        self.tab_graph = tk.Frame(self.notebook)
        self.notebook.add(self.tab_graph, text="🕸️ Grafo Social")
        
        self.tab_users = tk.Frame(self.notebook)
        self.notebook.add(self.tab_users, text="👥 Usuarios")
        
        self.tab_stats = tk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="📈 Estadísticas")
        
        self.tab_path = tk.Frame(self.notebook)
        self.notebook.add(self.tab_path, text="🔍 Buscar Camino")
        
        # Cargar contenido de pestañas
        self.load_dashboard()
        self.load_graph_tab()
        self.load_users_tab()
        self.load_stats_tab()
        self.load_path_tab()
        
        # Enlazar el evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def on_tab_changed(self, event):
        """Evento al cambiar de pestaña"""
        selected_tab = self.notebook.select()
        tab_name = self.notebook.tab(selected_tab, "text")
        
        if tab_name == "📈 Estadísticas":
            self.refresh_stats()
        elif tab_name == "👥 Usuarios":
            self.refresh_users_list()
        elif tab_name == "🕸️ Grafo Social":
            self.show_graph_text()
        # Puedes añadir más pestañas si es necesario
    
    def load_dashboard(self):
        """Cargar dashboard"""
        for widget in self.tab_dashboard.winfo_children():
            widget.destroy()
        
        tk.Label(self.tab_dashboard, text="Dashboard del Servidor",
                font=("Arial", 16, "bold")).pack(pady=20)
        
        stats_frame = tk.Frame(self.tab_dashboard)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        stats = [
            ("👥 Usuarios totales", len(self.users.all_usernames())),
            ("🤝 Amistades totales", sum(len(v) for v in self.graph.adj.values()) // 2),
        ]
        
        for label, value in stats:
            frame = tk.Frame(stats_frame, relief="solid", borderwidth=1)
            frame.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            
            tk.Label(frame, text=label, font=("Arial", 10)).pack(pady=5)
            tk.Label(frame, text=str(value), font=("Arial", 24, "bold")).pack(pady=5)
        
        self.activity_log = scrolledtext.ScrolledText(self.tab_dashboard, height=15)
        self.activity_log.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.log_activity(f"Servidor iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def load_graph_tab(self):
        """Cargar pestaña del grafo"""
        for widget in self.tab_graph.winfo_children():
            widget.destroy()
        
        tk.Label(self.tab_graph, text="Visualización del Grafo Social",
                font=("Arial", 16, "bold")).pack(pady=20)
        
        btn_frame = tk.Frame(self.tab_graph)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="📊 Generar y Mostrar Grafo",
                 command=self.show_graph, width=25, height=2,
                 bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=10)
        
        tk.Button(btn_frame, text="📋 Ver Grafo en Texto",
                 command=self.show_graph_text, width=25, height=2,
                 font=("Arial", 11)).pack(pady=10)
        
        self.graph_info = scrolledtext.ScrolledText(self.tab_graph, height=20)
        self.graph_info.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.show_graph_text()
    
    def show_graph(self):
        """Mostrar grafo con Graphviz"""
        success, result = self.graph.show_graph_with_graphviz()
        
        self.graph_info.delete("1.0", tk.END)
        if success:
            self.graph_info.insert("1.0", f"✅ Grafo generado exitosamente\n")
            self.graph_info.insert("2.0", f"📁 Imagen guardada en: {result}\n")
            self.log_activity("Grafo visualizado con Graphviz")
        else:
            self.graph_info.insert("1.0", f"❌ Error al generar grafo:\n{result}\n")
    
    def show_graph_text(self):
        """Mostrar grafo en texto"""
        text = "🕸️ GRAFO SOCIAL\n"
        text += "=" * 50 + "\n\n"
        
        if not self.graph.adj:
            text += "No hay usuarios conectados\n"
        else:
            for user in sorted(self.graph.adj.keys()):
                friends = sorted(self.graph.adj[user])
                if friends:
                    text += f"👤 {user} → {', '.join(friends)}\n"
                else:
                    text += f"👤 {user} → (sin amigos)\n"
        
        self.graph_info.delete("1.0", tk.END)
        self.graph_info.insert("1.0", text)
    
    def load_users_tab(self):
        """Cargar pestaña de usuarios"""
        for widget in self.tab_users.winfo_children():
            widget.destroy()
        
        tk.Label(self.tab_users, text="Gestión de Usuarios",
                font=("Arial", 16, "bold")).pack(pady=20)
        
        columns = ("Usuario", "Nombre", "Apellido", "Amigos", "Solicitudes")
        self.users_tree = ttk.Treeview(self.tab_users, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=140)
        
        scrollbar = ttk.Scrollbar(self.tab_users, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = tk.Frame(self.tab_users)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Actualizar Lista",
                 command=self.refresh_users_list).pack(side="left", padx=5)
        
        self.refresh_users_list()
    
    def refresh_users_list(self):
        """Actualizar lista de usuarios"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        for username in sorted(self.users.all_usernames()):
            user_data = self.users.get_profile(username)
            friends = len(self.graph.friends_of(username))
            requests = len(self.users.get_friend_requests(username))
            
            self.users_tree.insert("", "end", values=(
                username,
                user_data["nombre"],
                user_data["apellido"],
                friends,
                requests
            ))
    
    def load_stats_tab(self):
        """Cargar pestaña de estadísticas - VERSIÓN MEJORADA CON ACTUALIZACIÓN"""
        # Limpiar el tab
        for widget in self.tab_stats.winfo_children():
            widget.destroy()

        # Frame para el título y botón de actualización
        header_frame = tk.Frame(self.tab_stats)
        header_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(header_frame, text="Estadísticas Detalladas",
                font=("Arial", 16, "bold")).pack(side="left")

        # Botón de actualizar
        tk.Button(header_frame, text="🔄 Actualizar", font=("Arial", 10),
                  command=self.refresh_stats).pack(side="right", padx=10)

        # Área de texto para mostrar las estadísticas
        self.stats_text = scrolledtext.ScrolledText(self.tab_stats, height=20, width=70)
        self.stats_text.pack(fill="both", expand=True, padx=20, pady=10)

        # Cargar las estadísticas
        self.refresh_stats()
    
    def refresh_stats(self):
        """Actualizar el contenido de las estadísticas"""
        stats = self.graph.stats()
        
        self.stats_text.delete("1.0", tk.END)
        
        # Verificar si hay datos
        if not stats["max"]["usernames"]:
            self.stats_text.insert("1.0", "No hay suficientes datos para estadísticas")
            return
        
        # Construir información de estadísticas
        info = "📊 ESTADÍSTICAS DE LA RED SOCIAL\n"
        info += "=" * 40 + "\n\n"
        
        # Usuario(s) más popular(es)
        info += "👑 USUARIO(S) MÁS POPULAR(ES):\n"
        if stats['max']['usernames']:
            for i, username in enumerate(stats['max']['usernames'], 1):
                info += f"   {i}. {username} - {stats['max']['count']} amigos\n"
        else:
            info += "   Ningún usuario tiene amigos\n"
        
        info += "\n"
        
        # Usuario(s) más solitario(s)
        info += "🐣 USUARIO(S) MÁS SOLITARIO(S):\n"
        if stats['min']['usernames']:
            for i, username in enumerate(stats['min']['usernames'], 1):
                info += f"   {i}. {username} - {stats['min']['count']} amigos\n"
        else:
            info += "   Todos los usuarios tienen amigos\n"
        
        info += "\n"
        
        # Promedio
        info += f"📈 PROMEDIO DE AMIGOS:\n"
        info += f"   {stats['avg']:.2f} amigos por usuario\n"
        
        info += "\n"
        
        # Distribución de amigos (información adicional)
        info += "👥 DISTRIBUCIÓN DE AMISTADES:\n"
        users_by_friends = {}
        for username in self.users.all_usernames():
            count = len(self.graph.friends_of(username))
            users_by_friends[count] = users_by_friends.get(count, 0) + 1
        
        # Ordenar de mayor a menor cantidad de amigos
        for count in sorted(users_by_friends.keys(), reverse=True):
            if count > 0:
                info += f"   • {count} amigos: {users_by_friends[count]} usuario(s)\n"
        
        # Usuarios sin amigos
        info += f"   • 0 amigos: {users_by_friends.get(0, 0)} usuario(s)\n"
        
        # Total de usuarios
        info += f"\n📋 TOTAL DE USUARIOS: {len(self.users.all_usernames())}\n"
        
        self.stats_text.insert("1.0", info)
    
    def load_path_tab(self):
        """Cargar pestaña para buscar camino"""
        for widget in self.tab_path.winfo_children():
            widget.destroy()
        
        tk.Label(self.tab_path, text="Buscar Camino entre Usuarios",
                font=("Arial", 16, "bold")).pack(pady=20)
        
        input_frame = tk.Frame(self.tab_path)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Usuario Inicio:").grid(row=0, column=0, padx=5, pady=5)
        self.start_user = tk.Entry(input_frame, width=20)
        self.start_user.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Usuario Destino:").grid(row=1, column=0, padx=5, pady=5)
        self.goal_user = tk.Entry(input_frame, width=20)
        self.goal_user.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(input_frame, text="Buscar Camino", 
                 command=self.find_path).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.path_result = scrolledtext.ScrolledText(self.tab_path, height=10)
        self.path_result.pack(fill="both", expand=True, padx=20, pady=10)
    
    def find_path(self):
        """Buscar camino entre usuarios"""
        start = self.start_user.get().strip()
        goal = self.goal_user.get().strip()
        
        if not start or not goal:
            messagebox.showerror("Error", "Por favor ingrese ambos usuarios")
            return
        
        path = self.graph.path_bfs(start, goal)
        
        self.path_result.delete("1.0", tk.END)
        if path is None:
            self.path_result.insert("1.0", f"❌ No existe un camino entre '{start}' y '{goal}'")
        else:
            self.path_result.insert("1.0", f"✅ Camino encontrado:\n")
            self.path_result.insert("end", f"   {' → '.join(path)}")
    
    def log_activity(self, message):
        """Registrar actividad"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert("end", f"[{timestamp}] {message}\n")
        self.activity_log.see("end")

if __name__ == "__main__":
    print("🚀 Iniciando SocialTec Server...")
    server = SocialTecServer()