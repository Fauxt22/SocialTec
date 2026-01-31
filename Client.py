# Client.py - VERSIÓN SIMPLIFICADA PARA IMÁGENES
import socket
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import base64
from PIL import Image, ImageTk
import io
import os
import hashlib

class SocialTecClient:
    def __init__(self, root):
        self.root = root
        self.root.title("SocialTec - Red Social")
        self.root.geometry("900x700")
        
        self.server_host = "127.0.0.1"
        self.server_port = 5000
        self.current_user = None
        
        # Conectar al servidor
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.server_host, self.server_port))
            self.file_obj = self.sock.makefile("r", encoding="utf-8")
        except:
            messagebox.showerror("Error", "No se pudo conectar al servidor")
            self.root.destroy()
            return
        
        self.create_gui()
        self.show_login()
    
    def do_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        # HASH SHA-256 ANTES DE ENVIAR
        password_hashed = hashlib.sha256(password.encode()).hexdigest()
        
        request = {
            "type": "login",
            "username": username,
            "password": password_hashed  # Enviar hash, no texto plano
        }
    
    def send_request(self, request):
        """Enviar petición al servidor"""
        try:
            data = (json.dumps(request) + "\n").encode("utf-8")
            self.sock.sendall(data)
            response = self.file_obj.readline()
            if not response:
                return None
            return json.loads(response)
        except Exception as e:
            messagebox.showerror("Error", f"Error de comunicación: {str(e)}")
            return None
    
    def create_gui(self):
        """Crear interfaz gráfica"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Crear pestañas
        self.login_tab = self.create_login_tab()
        self.register_tab = self.create_register_tab()
        self.profile_tab = self.create_profile_tab()
        self.search_tab = self.create_search_tab()
        self.requests_tab = self.create_requests_tab()
        self.explore_tab = self.create_explore_tab()
    
    def show_login(self):
        """Mostrar pestaña de login"""
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)
        
        self.notebook.add(self.login_tab, text="🔐 Login")
        self.notebook.add(self.register_tab, text="📝 Registro")
    
    def show_register(self):
        """Mostrar pestaña de registro"""
        self.notebook.select(self.register_tab)
    
    def show_main_tabs(self):
        """Mostrar todas las pestañas principales después del login"""
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)
        
        self.notebook.add(self.profile_tab, text="👤 Perfil")
        self.notebook.add(self.search_tab, text="🔍 Buscar")
        self.notebook.add(self.requests_tab, text="📨 Solicitudes")
        self.notebook.add(self.explore_tab, text="🌍 Explorar")
        
        self.load_profile()
        self.load_friend_requests()
        self.load_all_users()
    
    # ============================================
    # SECCIÓN CRÍTICA: SOLUCIÓN SIMPLE PARA IMÁGENES
    # ============================================
    
    def load_profile(self):
        """Cargar perfil del usuario - VERSIÓN SIMPLE"""
        if not self.current_user:
            return
        
        request = {
            "type": "get_profile",
            "username": self.current_user
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            profile = response.get("profile", {})
            
            # Actualizar título
            self.profile_title.config(
                text=f"{profile.get('nombre')} {profile.get('apellido')}"
            )
            
            # **SIMPLE: Mostrar foto o texto "Sin foto"**
            foto = profile.get("foto", "")
            
            # LIMPIAR siempre la imagen anterior
            self.profile_photo_label.config(image='', text='')
            
            if foto:
                try:
                    img_data = base64.b64decode(foto)
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((120, 120))
                    photo_img = ImageTk.PhotoImage(img)
                    self.profile_photo_label.config(image=photo_img)
                    self.profile_photo_label.image = photo_img  # Guardar referencia
                except Exception as e:
                    # Si falla, mostrar texto
                    self.profile_photo_label.config(
                        text="❌\nError foto", 
                        font=("Arial", 10),
                        fg="red"
                    )
            else:
                # Sin foto - mostrar texto simple
                self.profile_photo_label.config(
                    text="📷\nSin foto", 
                    font=("Arial", 12),
                    fg="gray",
                    bg="#f0f0f0",
                    width=15,
                    height=8
                )
            
            # Mostrar información
            info_text = f"👤 Usuario: {profile.get('username')}\n\n"
            info_text += f"📝 {profile.get('bio', '')}\n\n"
            info_text += f"🤝 Amigos: {profile.get('friends_count', 0)}"
            
            self.profile_info.config(text=info_text)
            
            # Mostrar lista de amigos
            self.friends_listbox.delete(0, tk.END)
            for friend in profile.get("amigos", []):
                self.friends_listbox.insert(tk.END, f"• {friend}")
    
    def view_searched_profile(self):
        """Ver perfil del usuario seleccionado - VERSIÓN SIMPLE"""
        selection = self.search_results.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.search_results.get(selection[0])
        username = item.split(" - ")[0]
        
        request = {
            "type": "get_profile",
            "username": username
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            profile = response.get("profile", {})
            
            # Crear ventana emergente SIMPLE
            profile_window = tk.Toplevel(self.root)
            profile_window.title(f"Perfil de {username}")
            profile_window.geometry("400x400")
            
            # Foto o texto simple
            foto_frame = tk.Frame(profile_window)
            foto_frame.pack(pady=20)
            
            foto_label = tk.Label(foto_frame, width=15, height=8)
            foto = profile.get("foto", "")
            
            if foto:
                try:
                    img_data = base64.b64decode(foto)
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((120, 120))
                    photo_img = ImageTk.PhotoImage(img)
                    foto_label.config(image=photo_img)
                    foto_label.image = photo_img
                except:
                    foto_label.config(text="📷\nFoto error", font=("Arial", 10), fg="red")
            else:
                foto_label.config(
                    text="📷\nSin foto", 
                    font=("Arial", 12),
                    fg="gray",
                    bg="#f0f0f0"
                )
            
            foto_label.pack()
            
            # Información
            info = f"👤 {profile.get('nombre')} {profile.get('apellido')}\n\n"
            info += f"📝 {profile.get('bio', 'Sin biografía')}\n\n"
            info += f"🤝 {profile.get('friends_count', 0)} amigos\n"
            info += f"📧 Usuario: {profile.get('username')}"
            
            info_label = tk.Label(profile_window, text=info, font=("Arial", 11), justify="left")
            info_label.pack(pady=20)
            
            # Botón cerrar
            tk.Button(profile_window, text="Cerrar", 
                     command=profile_window.destroy).pack(pady=10)
    
    # ============================================
    # EL RESTO DEL CÓDIGO SE MANTIENE IGUAL
    # ============================================
    
    def create_login_tab(self):
        """Crear pestaña de login"""
        frame = tk.Frame(self.notebook, bg="white")
        
        tk.Label(frame, text="SocialTec", font=("Arial", 24, "bold"),
                 bg="white").pack(pady=40)
        
        tk.Label(frame, text="Iniciar Sesión", font=("Arial", 16),
                 bg="white").pack(pady=10)
        
        form_frame = tk.Frame(frame, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Usuario:", bg="white", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.login_username = tk.Entry(form_frame, font=("Arial", 10), width=25)
        self.login_username.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(form_frame, text="Contraseña:", bg="white",
                 font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.login_password = tk.Entry(form_frame, show="•", 
                                      font=("Arial", 10), width=25)
        self.login_password.grid(row=1, column=1, pady=5, padx=5)
        
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=30)
        
        tk.Button(btn_frame, text="Iniciar Sesión", font=("Arial", 11, "bold"),
                 bg="#2196F3", fg="white", padx=20, pady=5,
                 command=self.do_login).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Registrarse", font=("Arial", 11),
                 bg="#4CAF50", fg="white", padx=20, pady=5,
                 command=self.show_register).pack(side="left", padx=5)
        
        return frame
    
    def do_login(self):
        """Realizar login - ENVÍO TEXTO PLANO (PASSLIB LO HASHEA)"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
            return
        
        request = {
            "type": "login",
            "username": username,
            "password": password  # TEXTO PLANO - PASSLIB LO HASHEA EN EL SERVER
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            self.current_user = username
            messagebox.showinfo("Éxito", f"¡Bienvenido {response.get('nombre')}!")
            self.show_main_tabs()
        else:
            messagebox.showerror("Error", response.get("msg", "Error desconocido"))
    
    def create_register_tab(self):
        """Crear pestaña de registro"""
        frame = tk.Frame(self.notebook, bg="white")
        
        tk.Label(frame, text="Registrarse", font=("Arial", 18, "bold"),
                 bg="white").pack(pady=20)
        
        form_frame = tk.Frame(frame, bg="white")
        form_frame.pack(pady=10)
        
        self.reg_fields = {}
        
        campos = [
            ("Usuario:", "username", False),
            ("Contraseña:", "password", True),
            ("Confirmar Contraseña:", "confirm", True),
            ("Nombre:", "nombre", False),
            ("Apellido:", "apellido", False)
        ]
        
        for i, (texto, nombre, es_password) in enumerate(campos):
            tk.Label(form_frame, text=texto, bg="white", 
                    font=("Arial", 10)).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if es_password:
                entry = tk.Entry(form_frame, show="•", font=("Arial", 10), width=25)
            else:
                entry = tk.Entry(form_frame, font=("Arial", 10), width=25)
            
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.reg_fields[nombre] = entry
        
        tk.Label(form_frame, text="Foto (opcional):", bg="white",
                font=("Arial", 10)).grid(row=len(campos), column=0, sticky="w", pady=5, padx=5)
        
        self.reg_photo = None
        photo_frame = tk.Frame(form_frame, bg="white")
        photo_frame.grid(row=len(campos), column=1, sticky="w", pady=5, padx=5)
        
        self.photo_label = tk.Label(photo_frame, text="Sin foto", 
                                   font=("Arial", 9), fg="gray", bg="white")
        self.photo_label.pack(side="left")
        
        tk.Button(photo_frame, text="Seleccionar", font=("Arial", 9),
                 command=self.select_photo).pack(side="left", padx=5)
        
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Registrar", font=("Arial", 11, "bold"),
                 bg="#4CAF50", fg="white", padx=20, pady=5,
                 command=self.do_register).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Volver", font=("Arial", 11),
                 command=self.show_login).pack(side="left", padx=5)
        
        return frame
    
    def select_photo(self):
        """Seleccionar foto de perfil"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if filepath:
            try:
                img = Image.open(filepath)
                img.thumbnail((150, 150))
                
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                self.reg_photo = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                photo_img = ImageTk.PhotoImage(img)
                self.photo_label.config(image=photo_img, text="")
                self.photo_label.image = photo_img
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def do_register(self):
        """Realizar registro - ENVÍO TEXTO PLANO"""
        username = self.reg_fields["username"].get().strip()
        password = self.reg_fields["password"].get().strip()
        confirm_password = self.reg_fields["confirm"].get().strip()
        nombre = self.reg_fields["nombre"].get().strip()
        apellido = self.reg_fields["apellido"].get().strip()
        foto = self.reg_photo if self.reg_photo else ""
        
        if not all([username, password, confirm_password, nombre, apellido]):
            messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        request = {
            "type": "register",
            "username": username,
            "password": password,  # TEXTO PLANO - PASSLIB LO HASHEA EN EL SERVER
            "nombre": nombre,
            "apellido": apellido,
            "foto": foto
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            messagebox.showinfo("Éxito", "¡Cuenta creada exitosamente!")
            
            for entry in self.reg_fields.values():
                entry.delete(0, tk.END)
            
            self.photo_label.config(image=None, text="Sin foto")
            self.reg_photo = None
            
            self.show_login()
        else:
            messagebox.showerror("Error", response.get("msg", "Error desconocido"))
    
    def create_profile_tab(self):
        """Crear pestaña de perfil"""
        frame = tk.Frame(self.notebook)
        
        header_frame = tk.Frame(frame, bg="#2196F3", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        self.profile_title = tk.Label(header_frame, text="", font=("Arial", 20, "bold"),
                                     fg="white", bg="#2196F3")
        self.profile_title.pack(expand=True)
        
        content_frame = tk.Frame(frame, padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        info_frame = tk.Frame(content_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        # LABEL PARA FOTO - CONFIGURADO PARA MOSTRAR TEXTO SI NO HAY IMAGEN
        self.profile_photo_label = tk.Label(info_frame, 
                                           relief="solid", 
                                           borderwidth=1,
                                           bg="#f5f5f5")
        self.profile_photo_label.pack(side="left", padx=(0, 20))
        
        self.profile_info = tk.Label(info_frame, text="", font=("Arial", 11),
                                    justify="left", anchor="w")
        self.profile_info.pack(side="left", fill="both", expand=True)
        
        tk.Label(content_frame, text="Mis Amigos", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        friends_frame = tk.Frame(content_frame)
        friends_frame.pack(fill="both", expand=True)
        
        self.friends_listbox = tk.Listbox(friends_frame, font=("Arial", 11), height=12)
        scrollbar = tk.Scrollbar(friends_frame, orient="vertical", command=self.friends_listbox.yview)
        self.friends_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.friends_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(content_frame, text="🔄 Actualizar Perfil", font=("Arial", 11),
                 command=self.load_profile).pack(pady=10)
        
        return frame
    
    def create_search_tab(self):
        """Crear pestaña de búsqueda"""
        frame = tk.Frame(self.notebook)
        
        search_frame = tk.Frame(frame, padx=20, pady=20)
        search_frame.pack(fill="x")
        
        tk.Label(search_frame, text="Buscar Usuarios:", 
                font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side="left", padx=(0, 10))
        
        tk.Button(search_frame, text="🔍 Buscar", font=("Arial", 11),
                 command=self.do_search).pack(side="left")
        
        results_frame = tk.Frame(frame)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.search_results = tk.Listbox(results_frame, font=("Arial", 11), height=15)
        scrollbar = tk.Scrollbar(results_frame, orient="vertical", command=self.search_results.yview)
        self.search_results.configure(yscrollcommand=scrollbar.set)
        
        self.search_results.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        action_frame = tk.Frame(frame)
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="👤 Ver Perfil", font=("Arial", 11),
                 command=self.view_searched_profile).pack(side="left", padx=5)
        
        tk.Button(action_frame, text="➕ Enviar Solicitud", font=("Arial", 11),
                 command=self.send_friend_request_to_selected,
                 bg="#4CAF50", fg="white").pack(side="left", padx=5)
        
        tk.Button(action_frame, text="❌ Eliminar Amigo", font=("Arial", 11),
                 command=self.remove_friend_from_selected,
                 bg="#f44336", fg="white").pack(side="left", padx=5)
        
        return frame
    
    def do_search(self):
        """Realizar búsqueda"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return
        
        request = {
            "type": "search_users",
            "query": query,
            "searcher": self.current_user
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            results = response.get("results", [])
            self.search_results.delete(0, tk.END)
            
            for user in results:
                status = "✓ Amigos" if user["are_friends"] else "○ No amigos"
                self.search_results.insert(
                    tk.END, 
                    f"{user['username']} - {user['nombre']} {user['apellido']} [{status}]"
                )
    
    def send_friend_request_to_selected(self):
        """Enviar solicitud de amistad al usuario seleccionado"""
        selection = self.search_results.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario de la lista")
            return
        
        try:
            item = self.search_results.get(selection[0])
            parts = item.split(" - ")
            if len(parts) < 1:
                messagebox.showerror("Error", "No se pudo obtener el usuario")
                return
            
            username = parts[0].strip()
            
            if "[✓ Amigos]" in item:
                messagebox.showinfo("Información", f"Ya eres amigo de {username}")
                return
            
            request = {
                "type": "send_friend_request",
                "from": self.current_user,
                "to": username
            }
            
            response = self.send_request(request)
            if response and response.get("status") == "ok":
                messagebox.showinfo("Éxito", f"Solicitud enviada a {username}")
                self.do_search()
            else:
                messagebox.showerror("Error", response.get("msg", "Error al enviar solicitud"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def remove_friend_from_selected(self):
        """Eliminar amigo seleccionado"""
        selection = self.search_results.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.search_results.get(selection[0])
        friend = item.split(" - ")[0]
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar a {friend} de tus amigos?"):
            return
        
        request = {
            "type": "remove_friend",
            "a": self.current_user,
            "b": friend
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            messagebox.showinfo("Éxito", "Amigo eliminado")
            self.load_profile()
            self.do_search()
        else:
            messagebox.showerror("Error", response.get("msg", "Error al eliminar"))
    
    def create_requests_tab(self):
        """Crear pestaña de solicitudes"""
        frame = tk.Frame(self.notebook)
        
        tk.Label(frame, text="Solicitudes de Amistad", 
                font=("Arial", 16, "bold")).pack(pady=20)
        
        self.requests_listbox = tk.Listbox(frame, font=("Arial", 11), height=15)
        self.requests_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Actualizar", font=("Arial", 11),
                 command=self.load_friend_requests).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="✅ Aceptar", font=("Arial", 11),
                 command=self.accept_request,
                 bg="#4CAF50", fg="white").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="❌ Rechazar", font=("Arial", 11),
                 command=self.reject_request,
                 bg="#f44336", fg="white").pack(side="left", padx=5)
        
        return frame
    
    def load_friend_requests(self):
        """Cargar solicitudes de amistad"""
        if not self.current_user:
            return
        
        request = {
            "type": "get_friend_requests",
            "username": self.current_user
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            requests = response.get("requests", [])
            self.requests_listbox.delete(0, tk.END)
            
            for req in requests:
                self.requests_listbox.insert(
                    tk.END, 
                    f"{req['username']} - {req['nombre']} {req['apellido']}"
                )
    
    def accept_request(self):
        """Aceptar solicitud seleccionada"""
        selection = self.requests_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return
        
        item = self.requests_listbox.get(selection[0])
        requester = item.split(" - ")[0]
        
        request = {
            "type": "accept_friend_request",
            "username": self.current_user,
            "requester": requester
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            messagebox.showinfo("Éxito", "Solicitud aceptada")
            self.load_friend_requests()
            self.load_profile()
        else:
            messagebox.showerror("Error", response.get("msg", "Error al aceptar"))
    
    def reject_request(self):
        """Rechazar solicitud seleccionada"""
        selection = self.requests_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una solicitud")
            return
        
        item = self.requests_listbox.get(selection[0])
        requester = item.split(" - ")[0]
        
        request = {
            "type": "reject_friend_request",
            "username": self.current_user,
            "requester": requester
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            messagebox.showinfo("Éxito", "Solicitud rechazada")
            self.load_friend_requests()
        else:
            messagebox.showerror("Error", response.get("msg", "Error al rechazar"))
    
    def create_explore_tab(self):
        """Crear pestaña para explorar todos los usuarios"""
        frame = tk.Frame(self.notebook)
        
        tk.Label(frame, text="Explorar Usuarios", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Todos los usuarios registrados en SocialTec",
                font=("Arial", 10)).pack(pady=5)
        
        main_frame = tk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side="left", fill="both", expand=True)
        
        self.all_users_listbox = tk.Listbox(list_frame, font=("Arial", 11), height=20)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.all_users_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.all_users_listbox.yview)
        
        self.all_users_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        action_frame = tk.Frame(main_frame)
        action_frame.pack(side="right", padx=(10, 0))
        
        tk.Button(action_frame, text="🔄 Actualizar", font=("Arial", 11),
                 command=self.load_all_users, width=15).pack(pady=5)
        
        tk.Button(action_frame, text="👤 Ver Perfil", font=("Arial", 11),
                 command=self.view_explore_profile, width=15).pack(pady=5)
        
        tk.Button(action_frame, text="➕ Enviar Solicitud", font=("Arial", 11),
                 command=self.send_request_to_all_selected, 
                 bg="#4CAF50", fg="white", width=15).pack(pady=5)
        
        self.explore_status = tk.Label(frame, text="", font=("Arial", 10), fg="gray")
        self.explore_status.pack(pady=5)
        
        return frame
    
    def view_explore_profile(self):
        """Ver perfil del usuario seleccionado en explorar"""
        selection = self.all_users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.all_users_listbox.get(selection[0])
        username = item.split(" - ")[0]
        
        request = {
            "type": "get_profile",
            "username": username
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            profile = response.get("profile", {})
            
            info = f"👤 {profile.get('nombre')} {profile.get('apellido')}\n\n"
            info += f"📝 {profile.get('bio', 'Sin biografía')}\n\n"
            info += f"🤝 {profile.get('friends_count', 0)} amigos\n\n"
            info += f"📧 Usuario: {profile.get('username')}"
            
            messagebox.showinfo("Perfil de Usuario", info)
    
    def load_all_users(self):
        """Cargar todos los usuarios"""
        request = {
            "type": "get_all_users"
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            users = response.get("users", [])
            self.all_users_listbox.delete(0, tk.END)
            
            for user in users:
                if user['username'] != self.current_user:
                    self.all_users_listbox.insert(
                        tk.END, 
                        f"{user['username']} - {user['nombre']} {user['apellido']}"
                    )
            
            self.explore_status.config(text=f"Mostrando {len(users)} usuarios")
        else:
            self.explore_status.config(text="Error al cargar usuarios")
    
    def send_request_to_all_selected(self):
        """Enviar solicitud al usuario seleccionado en explorar"""
        selection = self.all_users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.all_users_listbox.get(selection[0])
        to_user = item.split(" - ")[0]
        
        request = {
            "type": "send_friend_request",
            "from": self.current_user,
            "to": to_user
        }
        
        response = self.send_request(request)
        if response and response.get("status") == "ok":
            messagebox.showinfo("Éxito", f"Solicitud enviada a {to_user}")
        else:
            messagebox.showerror("Error", response.get("msg", "Error al enviar solicitud"))
    
    def __del__(self):
        """Destructor para cerrar conexión"""
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SocialTecClient(root)
    root.mainloop()