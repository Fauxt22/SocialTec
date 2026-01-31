import pickle
import os
from collections import deque

class SocialGraph:
    def __init__(self):
        self.adj = {}  # Grafo de amistades
        self._load()
    
    def _load(self):
        # Crear directorio data si no existe
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists("data/graph.dat"):
            try:
                with open("data/graph.dat", "rb") as f:
                    self.adj = pickle.load(f)
            except Exception as e:
                print(f"Error cargando grafo: {e}")
                self.adj = {}
        else:
            self.adj = {}
    
    def _save(self):
        # Crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        with open("data/graph.dat", "wb") as f:
            pickle.dump(self.adj, f)
    
    def ensure_user(self, username):
        if username not in self.adj:
            self.adj[username] = set()
            self._save()
    
    def add_friendship(self, a, b):
        if a == b:
            return False, "No puedes ser amigo de ti mismo"
        
        self.ensure_user(a)
        self.ensure_user(b)
        
        self.adj[a].add(b)
        self.adj[b].add(a)
        
        self._save()
        return True, None
    
    def remove_friendship(self, a, b):
        if a in self.adj:
            self.adj[a].discard(b)
        if b in self.adj:
            self.adj[b].discard(a)
        
        self._save()
        return True, None
    
    def friends_of(self, username):
        return list(self.adj.get(username, set()))
    
    def path_bfs(self, start, goal):
        """BFS para encontrar camino entre usuarios - IMPLEMENTACIÓN CORRECTA"""
        if start not in self.adj or goal not in self.adj:
            return None
        
        if start == goal:
            return [start]
        
        # Usar deque para BFS eficiente
        queue = deque()
        queue.append(start)
        
        # Diccionario para reconstruir el camino
        came_from = {start: None}
        
        while queue:
            current = queue.popleft()
            
            # Si encontramos el objetivo, reconstruir camino
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Explorar amigos
            for friend in self.adj.get(current, set()):
                if friend not in came_from:
                    came_from[friend] = current
                    queue.append(friend)
        
        return None
    
    def stats(self, users):
        """Obtener estadísticas: usuario con más/menos amigos, promedio - VERSIÓN CORREGIDA"""
        users = list(users or [])
        
        if not users:
            return {"max": {"username": "N/A", "count": 0}, 
                    "min": {"username": "N/A", "count": 0}, 
                    "avg": 0.0}
        
        # Calcular número de amigos para cada usuario
        degrees = {}
        for u in users:
            friends = self.adj.get(u, set())
            degrees[u] = len(friends)
        
        # Encontrar usuario con MÁS amigos
        if degrees:
            max_u = max(degrees.keys(), key=lambda u: degrees[u])
            min_u = min(degrees.keys(), key=lambda u: degrees[u])
        else:
            max_u = min_u = users[0] if users else "N/A"
        
        # Calcular promedio
        total_friends = sum(degrees.values())
        avg_friends = total_friends / len(users) if users else 0
        
        return {
            "max": {"username": max_u, "count": degrees.get(max_u, 0)},
            "min": {"username": min_u, "count": degrees.get(min_u, 0)},
            "avg": round(avg_friends, 2)
        }
        
    def show_graph_with_graphviz(self):
        """Mostrar grafo con Graphviz (requiere instalación)"""
        try:
            import graphviz
            import tempfile
            
            dot = graphviz.Graph('SocialTec', format='png')
            dot.attr(rankdir='LR')
            dot.attr('node', shape='circle', style='filled', fillcolor='lightblue')
            
            # Agregar nodos
            for user in self.adj:
                dot.node(user)
            
            # Agregar conexiones (sin duplicados)
            seen_edges = set()
            for user in self.adj:
                for friend in self.adj[user]:
                    if (user, friend) not in seen_edges and (friend, user) not in seen_edges:
                        dot.edge(user, friend)
                        seen_edges.add((user, friend))
            
            # Guardar y mostrar
            output_path = tempfile.mktemp(suffix='.png')
            dot.render(output_path, view=True, cleanup=False)
            
            return True, output_path
        except ImportError:
            return False, "Graphviz no está instalado. Instala con: pip install graphviz"
        except Exception as e:
            return False, f"Error: {e}"
    
    def get_suggested_friends(self, username, limit=5):
        """Obtener sugerencias de amigos"""
        if username not in self.adj:
            return []
        
        my_friends = self.adj[username]
        suggestions = {}
        
        for friend in my_friends:
            for friend_of_friend in self.adj.get(friend, set()):
                if (friend_of_friend != username and 
                    friend_of_friend not in my_friends):
                    suggestions[friend_of_friend] = suggestions.get(friend_of_friend, 0) + 1
        
        # Ordenar por más común
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return [user for user, count in sorted_suggestions[:limit]]