# Sistema de Gestión E-Learning.
# Gestionar cursos, estudiantes y materiales didácticos.

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

ruta_json = os.path.join(data_folder, "elearning_datos.json")

# Clase que implementa una estructura de datos tipo pila (LIFO).
class Pila:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self):
        self.items = []

# Verifica si la estructura está vacía.
    def esta_vacia(self):
        return len(self.items) == 0

# Agrega un elemento al tope de la pila.
    def apilar(self, item):
        self.items.append(item)

# Elimina y retorna el elemento del tope de la pila.
    def desapilar(self):
        if not self.esta_vacia():
            return self.items.pop()
        return None

    def ver_tope(self):
        if not self.esta_vacia():
            return self.items[-1]
        return None

    def tamaño(self):
        return len(self.items)

# Clase que implementa una estructura de datos tipo cola (FIFO).
class Cola:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self):
        self.items = []

# Verifica si la estructura está vacía.
    def esta_vacia(self):
        return len(self.items) == 0

# Agrega un elemento al final de la cola.
    def encolar(self, item):
        self.items.insert(0, item)

# Elimina y retorna el primer elemento de la cola.
    def desencolar(self):
        if not self.esta_vacia():
            return self.items.pop()
        return None

    def ver_frente(self):
        if not self.esta_vacia():
            return self.items[-1]
        return None

    def tamaño(self):
        return len(self.items)

# Nodo para el árbol binario de búsqueda, almacena clave, valor y referencias izquierda/derecha.
class NodoArbol:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izquierdo = None
        self.derecho = None

# Clase para un árbol binario de búsqueda de cursos, usado en búsquedas por tema y nivel.
class ArbolBusqueda:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self):
        self.raiz = None

    def insertar(self, clave, valor):
        if not self.raiz:
            self.raiz = NodoArbol(clave, valor)
        else:
            self._insertar_recursivo(self.raiz, clave, valor)

    def _insertar_recursivo(self, nodo, clave, valor):
        if clave < nodo.clave:
            if nodo.izquierdo is None:
                nodo.izquierdo = NodoArbol(clave, valor)
            else:
                self._insertar_recursivo(nodo.izquierdo, clave, valor)
        else:
            if nodo.derecho is None:
                nodo.derecho = NodoArbol(clave, valor)
            else:
                self._insertar_recursivo(nodo.derecho, clave, valor)

# Busca cursos en el árbol que coincidan con un tema y nivel específico.
    def buscar_por_tema_nivel(self, tema, nivel):
        resultados = []
        self._buscar_tema_nivel_recursivo(self.raiz, tema, nivel, resultados)
        return resultados

    def _buscar_tema_nivel_recursivo(self, nodo, tema, nivel, resultados):
        if nodo is None:
            return
        curso = nodo.valor
        if tema.lower() in curso.nombre.lower() and (nivel == "Todos" or curso.nivel == nivel):
            resultados.append(curso)
        self._buscar_tema_nivel_recursivo(nodo.izquierdo, tema, nivel, resultados)
        self._buscar_tema_nivel_recursivo(nodo.derecho, tema, nivel, resultados)

# Clase que representa un grafo dirigido para modelar cursos y sus prerequisitos.
class Grafo:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self):
        self.vertices = {}
        self.aristas = {}

# Agrega un curso como vértice al grafo.
    def agregar_vertice(self, curso):
        self.vertices[curso.id] = curso
        if curso.id not in self.aristas:
            self.aristas[curso.id] = []

# Establece una relación de prerequisito entre dos cursos en el grafo.
    def agregar_arista(self, curso_id, prerequisito_id):
        if curso_id in self.aristas and prerequisito_id in self.vertices:
            if prerequisito_id not in self.aristas[curso_id]:
                self.aristas[curso_id].append(prerequisito_id)

# Verifica si un estudiante cumple con todos los prerequisitos de un curso.
    def verificar_cumple_prerequisitos(self, estudiante, curso_id):
        if curso_id not in self.vertices:
            return False

        prerequisitos_necesarios = self.aristas.get(curso_id, [])

        cursos_completados = {curso.id for curso in estudiante.cursos}

        print(f"DEBUG: Verificando prerequisitos para curso {curso_id}")
        print(f"DEBUG: Prerequisitos necesarios: {prerequisitos_necesarios}")
        print(f"DEBUG: Cursos completados por estudiante: {cursos_completados}")

        for prereq_id in prerequisitos_necesarios:
            if prereq_id not in cursos_completados:
                print(f"DEBUG: Falta prerequisito {prereq_id}")
                return False

        return True

# Recomienda una ruta de cursos necesarios para alcanzar un curso objetivo.
    def recomendar_ruta_aprendizaje(self, curso_objetivo_id):
        if curso_objetivo_id not in self.vertices:
            return []

        def obtener_ruta_con_orden_topologico(curso_id, visitados=None, ruta_actual=None):
            if visitados is None:
                visitados = set()
            if ruta_actual is None:
                ruta_actual = []

            if curso_id in visitados:
                return []

            visitados.add(curso_id)

            prerequisitos = self.aristas.get(curso_id, [])

            for prereq_id in prerequisitos:
                if prereq_id not in [c.id for c in ruta_actual]:
                    ruta_prereq = obtener_ruta_con_orden_topologico(
                        prereq_id, visitados.copy(), ruta_actual.copy()
                    )
                    for curso in ruta_prereq:
                        if curso.id not in [c.id for c in ruta_actual]:
                            ruta_actual.append(curso)

            if curso_id not in [c.id for c in ruta_actual]:
                ruta_actual.append(self.vertices[curso_id])

            return ruta_actual

        return obtener_ruta_con_orden_topologico(curso_objetivo_id)

# Clase que representa un curso con sus atributos, materiales y prerequisitos.
class Curso:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self, id, nombre, descripcion, nivel):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.nivel = nivel
        self.materiales = []
        self.estudiantes = []
        self.prerequisitos = []

# Agrega material a un curso específico.
    def agregar_material(self, material):
        self.materiales.append(material)

    def __str__(self):
        return f"Curso: {self.nombre} (Nivel: {self.nivel})"

# Clase que representa un material educativo asociado a un curso.
class Material:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self, id, nombre, tipo, url):
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.url = url

    def __str__(self):
        return f"Material: {self.nombre} ({self.tipo})"

# Clase que representa un estudiante con sus datos y cursos inscritos.
class Estudiante:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.cursos = []

    def __str__(self):
        return f"Estudiante: {self.nombre} ({self.email})"

# Clase principal que gestiona toda la lógica del sistema e-learning (estudiantes, cursos, materiales, etc.).
class SistemaELearning:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self):
        self.estudiantes = {}
        self.cursos = {}
        self.cursos_eliminados = {}
        self.materiales_eliminados = {}
        self.prerequisitos_eliminados = {}
        self.historial_cambios = Pila()
        self.lista_espera = {}
        self.arbol_cursos = ArbolBusqueda()
        self.grafo_cursos = Grafo()
        self.ruta_json = ruta_json
        self.cargar_desde_json()

    def crear_curso(self, id, nombre, descripcion, nivel):
        if id not in self.cursos:
            nuevo_curso = Curso(id, nombre, descripcion, nivel)
            self.cursos[id] = nuevo_curso
            self.grafo_cursos.agregar_vertice(nuevo_curso)
            clave = f"{nombre.lower()}_{nivel}"
            self.arbol_cursos.insertar(clave, nuevo_curso)
            self.lista_espera[id] = Cola()
            self.guardar_en_json()
            return nuevo_curso
        return None

    def registrar_estudiante(self, id, nombre, email):
        if id not in self.estudiantes:
            nuevo_estudiante = Estudiante(id, nombre, email)
            self.estudiantes[id] = nuevo_estudiante
            self.guardar_en_json()
            return nuevo_estudiante
        return None

# Guarda el estado actual del sistema en un archivo JSON.
    def guardar_en_json(self):
        datos = {
            "estudiantes": [
                {
                    "id": e.id,
                    "nombre": e.nombre,
                    "email": e.email,
                    "cursos": [curso.id for curso in e.cursos]
                }
                for e in self.estudiantes.values()
            ],
            "cursos": [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "descripcion": c.descripcion,
                    "nivel": c.nivel,
                    "materiales": [
                        {
                            "id": m.id,
                            "nombre": m.nombre,
                            "tipo": m.tipo,
                            "url": m.url
                        }
                        for m in c.materiales
                    ],
                    "estudiantes": [estudiante.id for estudiante in c.estudiantes],
                    "prerequisitos": c.prerequisitos
                }
                for c in self.cursos.values()
            ],
            "cursos_eliminados": [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "descripcion": c.descripcion,
                    "nivel": c.nivel,
                    "materiales": [
                        {
                            "id": m.id,
                            "nombre": m.nombre,
                            "tipo": m.tipo,
                            "url": m.url
                        }
                        for m in c.materiales
                    ],
                    "estudiantes": [estudiante.id for estudiante in c.estudiantes],
                    "prerequisitos": c.prerequisitos
                }
                for c in self.cursos_eliminados.values()
            ],
            "materiales_eliminados": [
                {
                    "id": m.id,
                    "nombre": m.nombre,
                    "tipo": m.tipo,
                    "url": m.url
                }
                for m in self.materiales_eliminados.values()
            ],
            "prerequisitos_eliminados": self.prerequisitos_eliminados
        }

        print(f"DEBUG: Guardando datos en JSON...")
        print(f"DEBUG: Cursos con prerequisitos:")
        for curso in datos["cursos"]:
            if curso["prerequisitos"]:
                print(f"  Curso {curso['id']} ({curso['nombre']}) -> prerequisitos: {curso['prerequisitos']}")

        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

# Carga los datos del sistema desde un archivo JSON, incluyendo estudiantes y cursos.
    def cargar_desde_json(self):
        if os.path.exists(self.ruta_json):
            try:
                with open(self.ruta_json, "r", encoding="utf-8") as f:
                    datos = json.load(f)

                print("DEBUG: Cargando datos desde JSON...")

                self.estudiantes.clear()
                self.cursos.clear()
                self.grafo_cursos = Grafo()
                self.arbol_cursos = ArbolBusqueda()
                self.lista_espera.clear()

                for est in datos.get("estudiantes", []):
                    estudiante = self.registrar_estudiante(est["id"], est["nombre"], est["email"])
                    if estudiante:
                        estudiante.cursos = []

                for cur in datos.get("cursos", []):
                    curso = self.crear_curso(cur["id"], cur["nombre"], cur["descripcion"], cur["nivel"])
                    if curso:
                        curso.materiales = [
                            Material(m["id"], m["nombre"], m["tipo"], m["url"])
                            for m in cur.get("materiales", [])
                        ]
                        curso.estudiantes = []
                        curso.prerequisitos = cur.get("prerequisitos", [])

                print("DEBUG: Cursos creados, estableciendo prerequisitos...")

                for cur in datos.get("cursos", []):
                    curso_id = cur["id"]
                    prerequisitos = cur.get("prerequisitos", [])
                    print(f"DEBUG: Procesando prerequisitos para curso {curso_id}: {prerequisitos}")

                    for prerequisito_id in prerequisitos:
                        if prerequisito_id in self.cursos:
                            self.grafo_cursos.agregar_arista(curso_id, prerequisito_id)
                            print(f"DEBUG: Prerequisito establecido: {curso_id} -> {prerequisito_id}")
                        else:
                            print(f"DEBUG: WARNING - Prerequisito {prerequisito_id} no encontrado para curso {curso_id}")

                for cur in datos.get("cursos", []):
                    if cur["id"] in self.cursos:
                        curso = self.cursos[cur["id"]]
                        for estudiante_id in cur.get("estudiantes", []):
                            if estudiante_id in self.estudiantes:
                                estudiante = self.estudiantes[estudiante_id]
                                estudiante.cursos.append(curso)
                                curso.estudiantes.append(estudiante)

                for cur in datos.get("cursos_eliminados", []):
                    curso = Curso(cur["id"], cur["nombre"], cur["descripcion"], cur["nivel"])
                    curso.materiales = [
                        Material(m["id"], m["nombre"], m["tipo"], m["url"])
                        for m in cur.get("materiales", [])
                    ]
                    curso.estudiantes = []
                    curso.prerequisitos = cur.get("prerequisitos", [])
                    self.cursos_eliminados[cur["id"]] = curso

                for mat in datos.get("materiales_eliminados", []):
                    material = Material(mat["id"], mat["nombre"], mat["tipo"], mat["url"])
                    self.materiales_eliminados[mat["id"]] = material

                self.prerequisitos_eliminados = datos.get("prerequisitos_eliminados", {})

                print("DEBUG: Estado final del grafo de prerequisitos:")
                for curso_id, prerequisitos in self.grafo_cursos.aristas.items():
                    if prerequisitos:
                        print(f"  Curso {curso_id}: prerequisitos {prerequisitos}")

            except Exception as e:
                print(f"DEBUG: Error cargando JSON: {e}")
                self._crear_datos_ejemplo()
        else:
            print("DEBUG: Archivo JSON no existe, creando datos de ejemplo...")
            self._crear_datos_ejemplo()

    def _crear_datos_ejemplo(self):
        datos = {
            "estudiantes": [
                {"id": 1, "nombre": "Ana Gómez", "email": "ana@example.com", "cursos": []},
                {"id": 2, "nombre": "Carlos López", "email": "carlos@example.com", "cursos": []},
                {"id": 3, "nombre": "María Pérez", "email": "maria@example.com", "cursos": []}
            ],
            "cursos": [
                {"id": 101, "nombre": "Python Básico", "descripcion": "Introducción a Python", "nivel": "Básico", "materiales": [], "estudiantes": [], "prerequisitos": []},
                {"id": 102, "nombre": "Python Intermedio", "descripcion": "Conceptos avanzados de Python", "nivel": "Intermedio", "materiales": [], "estudiantes": [], "prerequisitos": [101]},
                {"id": 103, "nombre": "Python Avanzado", "descripcion": "Programación avanzada con Python", "nivel": "Avanzado", "materiales": [], "estudiantes": [], "prerequisitos": [102]},
                {"id": 201, "nombre": "Bases de Datos Básico", "descripcion": "Introducción a las bases de datos", "nivel": "Básico", "materiales": [], "estudiantes": [], "prerequisitos": []},
                {"id": 202, "nombre": "Bases de Datos Avanzado", "descripcion": "Diseño avanzado de bases de datos", "nivel": "Avanzado", "materiales": [], "estudiantes": [], "prerequisitos": [201]},
                {"id": 301, "nombre": "Web Development", "descripcion": "Desarrollo web completo", "nivel": "Avanzado", "materiales": [], "estudiantes": [], "prerequisitos": [102, 201]}
            ],
            "cursos_eliminados": [],
            "materiales_eliminados": [],
            "prerequisitos_eliminados": {}
        }

        with open(self.ruta_json, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        self.cargar_desde_json()

# Inscribe a un estudiante en un curso si cumple con los prerequisitos y hay cupo.
    def inscribir_estudiante(self, estudiante_id, curso_id, capacidad_maxima=30):
        if estudiante_id in self.estudiantes and curso_id in self.cursos:
            estudiante = self.estudiantes[estudiante_id]
            curso = self.cursos[curso_id]

            if curso in estudiante.cursos:
                return "ya_inscrito"

            if not self.grafo_cursos.verificar_cumple_prerequisitos(estudiante, curso_id):
                return "prerequisitos_faltantes"

            if len(curso.estudiantes) < capacidad_maxima:
                estudiante.cursos.append(curso)
                curso.estudiantes.append(estudiante)
                accion = {
                    "tipo": "inscripcion",
                    "estudiante_id": estudiante_id,
                    "curso_id": curso_id
                }
                self.historial_cambios.apilar(accion)
                self.guardar_en_json()
                return True
            else:
                self.lista_espera[curso_id].encolar(estudiante)
                return "lista_espera"
        return False

# Cancela la inscripción de un estudiante en un curso y maneja la lista de espera.
    def cancelar_inscripcion(self, estudiante_id, curso_id):
        if estudiante_id in self.estudiantes and curso_id in self.cursos:
            estudiante = self.estudiantes[estudiante_id]
            curso = self.cursos[curso_id]
            if curso in estudiante.cursos:
                estudiante.cursos.remove(curso)
                curso.estudiantes.remove(estudiante)
                accion = {
                    "tipo": "cancelacion",
                    "estudiante_id": estudiante_id,
                    "curso_id": curso_id
                }
                self.historial_cambios.apilar(accion)
                self.guardar_en_json()
                if not self.lista_espera[curso_id].esta_vacia():
                    estudiante_espera = self.lista_espera[curso_id].desencolar()
                    self.inscribir_estudiante(estudiante_espera.id, curso_id)
                return True
        return False

# Deshace la última inscripción o cancelación de curso realizada.
    def deshacer_ultima_accion(self):
        if not self.historial_cambios.esta_vacia():
            ultima_accion = self.historial_cambios.desapilar()
            estudiante_id = ultima_accion["estudiante_id"]
            curso_id = ultima_accion["curso_id"]
            if ultima_accion["tipo"] == "inscripcion":
                estudiante = self.estudiantes[estudiante_id]
                curso = self.cursos[curso_id]
                estudiante.cursos.remove(curso)
                curso.estudiantes.remove(estudiante)
                self.guardar_en_json()
                return True
            elif ultima_accion["tipo"] == "cancelacion":
                estudiante = self.estudiantes[estudiante_id]
                curso = self.cursos[curso_id]
                estudiante.cursos.append(curso)
                curso.estudiantes.append(estudiante)
                self.guardar_en_json()
                return True
        return False

# Busca cursos por tema y opcionalmente por nivel.
    def buscar_cursos(self, tema, nivel="Todos"):
        return self.arbol_cursos.buscar_por_tema_nivel(tema, nivel)

# Devuelve una lista de cursos recomendados en orden para alcanzar uno específico.
    def recomendar_cursos(self, curso_objetivo_id):
        return self.grafo_cursos.recomendar_ruta_aprendizaje(curso_objetivo_id)

# Establece un curso como prerequisito de otro curso.
    def establecer_prerequisito(self, curso_id, prerequisito_id):
        if curso_id in self.cursos and prerequisito_id in self.cursos:
            if curso_id == prerequisito_id:
                return False

            if prerequisito_id in self.cursos[curso_id].prerequisitos:
                return False

            self.cursos[curso_id].prerequisitos.append(prerequisito_id)
            self.grafo_cursos.agregar_arista(curso_id, prerequisito_id)

            print(f"DEBUG: Prerequisito establecido - Curso {curso_id} ahora requiere {prerequisito_id}")
            print(f"DEBUG: Prerequisitos del curso {curso_id}: {self.cursos[curso_id].prerequisitos}")
            print(f"DEBUG: Aristas del grafo para curso {curso_id}: {self.grafo_cursos.aristas.get(curso_id, [])}")

            self.guardar_en_json()
            return True
        return False

# Agrega material a un curso específico.
    def agregar_material(self, curso_id, material):
        if curso_id in self.cursos:
            self.cursos[curso_id].agregar_material(material)
            self.guardar_en_json()
            return True
        return False

    def eliminar_prerequisito(self, curso_id, prerequisito_id):
        if curso_id in self.cursos and prerequisito_id in self.cursos[curso_id].prerequisitos:
            self.cursos[curso_id].prerequisitos.remove(prerequisito_id)
            if curso_id in self.grafo_cursos.aristas and prerequisito_id in self.grafo_cursos.aristas[curso_id]:
                self.grafo_cursos.aristas[curso_id].remove(prerequisito_id)
            self.guardar_en_json()
            return True
        return False

# Elimina un material de un curso y lo guarda como eliminado.
    def eliminar_material(self, curso_id, material_id):
        if curso_id in self.cursos:
            curso = self.cursos[curso_id]
            for material in curso.materiales:
                if material.id == material_id:
                    curso.materiales.remove(material)
                    self.materiales_eliminados[material_id] = material
                    self.guardar_en_json()
                    return True
        return False

# Elimina un curso del sistema y lo guarda como eliminado.
    def eliminar_curso(self, curso_id):
        if curso_id in self.cursos:
            curso = self.cursos.pop(curso_id)
            self.cursos_eliminados[curso_id] = curso
            for c in self.cursos.values():
                if curso_id in c.prerequisitos:
                    c.prerequisitos.remove(curso_id)
            if curso_id in self.grafo_cursos.aristas:
                del self.grafo_cursos.aristas[curso_id]
            if curso_id in self.grafo_cursos.vertices:
                del self.grafo_cursos.vertices[curso_id]
            self.guardar_en_json()
            return True
        return False

# Elimina un estudiante del sistema.
    def eliminar_estudiante(self, estudiante_id):
        if estudiante_id in self.estudiantes:
            estudiante = self.estudiantes.pop(estudiante_id)
            for curso in self.cursos.values():
                if estudiante in curso.estudiantes:
                    curso.estudiantes.remove(estudiante)
            self.guardar_en_json()
            return True
        return False

# Restaura un curso eliminado previamente.
    def restaurar_curso(self, curso_id):
        if curso_id in self.cursos_eliminados:
            curso = self.cursos_eliminados.pop(curso_id)
            self.cursos[curso_id] = curso
            self.grafo_cursos.agregar_vertice(curso)
            for prereq_id in curso.prerequisitos:
                if prereq_id in self.cursos:
                    self.grafo_cursos.agregar_arista(curso_id, prereq_id)
            self.guardar_en_json()
            return True
        return False

    def restaurar_material(self, material_id):
        if material_id in self.materiales_eliminados:
            material = self.materiales_eliminados.pop(material_id)
            self.guardar_en_json()
            return True
        return False

    def restaurar_prerequisito(self, prerequisito):
        if prerequisito in self.prerequisitos_eliminados:
            self.prerequisitos_eliminados.pop(prerequisito)
            self.guardar_en_json()
            return True
        return False

# Clase principal que gestiona toda la lógica del sistema e-learning (estudiantes, cursos, materiales, etc.).
class SistemaELearningGUI:
# Método constructor que inicializa los atributos de la clase.
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión E-Learning")
        self.sistema = SistemaELearning()

        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc", font=("Arial", 10))
        self.style.map("TButton", background=[("active", "#aaa")])

        self.menu_principal()

        self.root.protocol("WM_DELETE_WINDOW", self.salir)

    def menu_principal(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="===== SISTEMA DE GESTIÓN E-LEARNING =====", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

        ttk.Button(frame, text="Gestión de Estudiantes", command=self.menu_estudiantes, width=30).pack(pady=5)
        ttk.Button(frame, text="Gestión de Cursos", command=self.menu_cursos, width=30).pack(pady=5)
        ttk.Button(frame, text="Inscripciones", command=self.menu_inscripciones, width=30).pack(pady=5)
        ttk.Button(frame, text="Búsquedas", command=self.menu_busquedas, width=30).pack(pady=5)
        ttk.Button(frame, text="Salir", command=self.salir, width=30).pack(pady=5)

    def menu_estudiantes(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="===== GESTIÓN DE ESTUDIANTES =====", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

        ttk.Button(frame, text="Registrar nuevo estudiante", command=self.registrar_estudiante, width=30).pack(pady=5)
        ttk.Button(frame, text="Ver lista de estudiantes", command=self.ver_estudiantes, width=30).pack(pady=5)
        ttk.Button(frame, text="Eliminar estudiante", command=self.eliminar_estudiante, width=30).pack(pady=5)
        ttk.Button(frame, text="Ver cursos de un estudiante", command=self.ver_cursos_estudiante, width=30).pack(pady=5)
        ttk.Button(frame, text="Volver al menú principal", command=self.menu_principal, width=30).pack(pady=5)

    def menu_cursos(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="===== GESTIÓN DE CURSOS =====", font=("Arial", 16), bg="#f0f0f0").pack(pady=5)

        ttk.Button(frame, text="Crear nuevo curso", command=self.crear_curso, width=30).pack(pady=3)
        ttk.Button(frame, text="Ver lista de cursos", command=self.ver_cursos, width=30).pack(pady=3)
        ttk.Button(frame, text="Agregar material a curso", command=self.agregar_material, width=30).pack(pady=3)
        ttk.Button(frame, text="Eliminar material de curso", command=self.eliminar_material, width=30).pack(pady=3)
        ttk.Button(frame, text="Establecer prerequisito", command=self.establecer_prerequisito, width=30).pack(pady=3)
        ttk.Button(frame, text="Eliminar prerequisito", command=self.eliminar_prerequisito, width=30).pack(pady=3)
        ttk.Button(frame, text="Eliminar curso", command=self.eliminar_curso, width=30).pack(pady=3)
        ttk.Button(frame, text="Restaurar curso eliminado", command=self.restaurar_curso, width=30).pack(pady=3)
        ttk.Button(frame, text="Ver materiales de curso", command=self.ver_materiales, width=30).pack(pady=5)
        ttk.Button(frame, text="Volver al menú principal", command=self.menu_principal, width=30).pack(pady=5)

    def menu_inscripciones(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="===== INSCRIPCIONES =====", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

        ttk.Button(frame, text="Inscribir estudiante en curso", command=self.inscribir_estudiante, width=30).pack(pady=5)
        ttk.Button(frame, text="Cancelar inscripción", command=self.cancelar_inscripcion, width=30).pack(pady=5)
        ttk.Button(frame, text="Deshacer última acción", command=self.deshacer_ultima_accion, width=30).pack(pady=5)
        ttk.Button(frame, text="Volver al menú principal", command=self.menu_principal, width=30).pack(pady=5)

    def menu_busquedas(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="===== BÚSQUEDAS =====", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

        ttk.Button(frame, text="Buscar cursos por tema", command=self.buscar_cursos_tema, width=30).pack(pady=5)
        ttk.Button(frame, text="Buscar cursos por tema y nivel", command=self.buscar_cursos_tema_nivel, width=30).pack(pady=5)
        ttk.Button(frame, text="Recomendar ruta de aprendizaje", command=self.recomendar_ruta, width=30).pack(pady=5)
        ttk.Button(frame, text="Volver al menú principal", command=self.menu_principal, width=30).pack(pady=5)

    def salir(self):
        self.sistema.guardar_en_json()
        self.root.destroy()

    def registrar_estudiante(self):
        def guardar_estudiante():
            try:
                id = int(entry_id.get())
                nombre = entry_nombre.get()
                email = entry_email.get()

                if not all([id, nombre]):
                    raise ValueError("El ID y el nombre son campos obligatorios.")

                estudiante = self.sistema.registrar_estudiante(id, nombre, email)
                if estudiante:
                    messagebox.showinfo("Éxito", f"Estudiante {nombre} registrado correctamente!")
                else:
                    messagebox.showerror("Error", "Ya existe un estudiante con ese ID.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Estudiante")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del estudiante:", bg="#f0f0f0").pack(pady=5)
        entry_id = tk.Entry(ventana)
        entry_id.pack(pady=5)

        tk.Label(ventana, text="Nombre completo:", bg="#f0f0f0").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)

        tk.Label(ventana, text="Correo electrónico:", bg="#f0f0f0").pack(pady=5)
        entry_email = tk.Entry(ventana)
        entry_email.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_estudiante).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_estudiante())

    def ver_estudiantes(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Lista de Estudiantes")
        ventana.configure(bg="#f0f0f0")

        if not self.sistema.estudiantes:
            tk.Label(ventana, text="No hay estudiantes registrados.", bg="#f0f0f0").pack(pady=10)
        else:
            tk.Label(ventana, text="LISTA DE ESTUDIANTES:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)

            frame = tk.Frame(ventana)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame, bg="#f0f0f0")
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            for id, estudiante in self.sistema.estudiantes.items():
                tk.Label(scrollable_frame, text=f"ID: {id} | Nombre: {estudiante.nombre} | Email: {estudiante.email}", bg="#f0f0f0").pack(pady=5)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

# Elimina un estudiante del sistema.
    def eliminar_estudiante(self):
        def confirmar_eliminar_estudiante():
            estudiante_id = int(entry_estudiante_id.get())
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este estudiante?"):
                if self.sistema.eliminar_estudiante(estudiante_id):
                    messagebox.showinfo("Éxito", "Estudiante eliminado correctamente!")
                else:
                    messagebox.showerror("Error", "Error al eliminar estudiante. Verifique el ID.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Estudiante")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del estudiante:", bg="#f0f0f0").pack(pady=5)
        entry_estudiante_id = tk.Entry(ventana)
        entry_estudiante_id.pack(pady=5)

        ttk.Button(ventana, text="Eliminar", command=confirmar_eliminar_estudiante).pack(pady=10)
        ventana.bind('<Return>', lambda event: confirmar_eliminar_estudiante())

    def ver_cursos_estudiante(self):
# Busca cursos por tema y opcionalmente por nivel.
        def buscar_cursos():
            id = int(entry_id.get())
            if id in self.sistema.estudiantes:
                estudiante = self.sistema.estudiantes[id]
                ventana_cursos = tk.Toplevel(ventana)
                ventana_cursos.title(f"Cursos de {estudiante.nombre}")
                ventana_cursos.configure(bg="#f0f0f0")

                if not estudiante.cursos:
                    tk.Label(ventana_cursos, text="No está inscrito en ningún curso.", bg="#f0f0f0").pack(pady=10)
                else:
                    tk.Label(ventana_cursos, text=f"Cursos de {estudiante.nombre}:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
                    for curso in estudiante.cursos:
                        tk.Label(ventana_cursos, text=f"- {curso.nombre} (Nivel: {curso.nivel})", bg="#f0f0f0").pack(pady=5)
            else:
                messagebox.showerror("Error", "Estudiante no encontrado.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Ver Cursos de un Estudiante")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del estudiante:", bg="#f0f0f0").pack(pady=5)
        entry_id = tk.Entry(ventana)
        entry_id.pack(pady=5)

        ttk.Button(ventana, text="Buscar", command=buscar_cursos).pack(pady=10)
        ventana.bind('<Return>', lambda event: buscar_cursos())

    def crear_curso(self):
        def guardar_curso():
            try:
                id = int(entry_id.get())
                nombre = entry_nombre.get()
                descripcion = entry_descripcion.get()
                nivel = entry_nivel.get()

                if not all([id, nombre, descripcion, nivel]):
                    raise ValueError("Todos los campos son obligatorios.")

                curso = self.sistema.crear_curso(id, nombre, descripcion, nivel)
                if curso:
                    messagebox.showinfo("Éxito", f"Curso '{nombre}' creado correctamente!")
                else:
                    messagebox.showerror("Error", "Ya existe un curso con ese ID.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ventana = tk.Toplevel(self.root)
        ventana.title("Crear Curso")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_id = tk.Entry(ventana)
        entry_id.pack(pady=5)

        tk.Label(ventana, text="Nombre del curso:", bg="#f0f0f0").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)

        tk.Label(ventana, text="Descripción:", bg="#f0f0f0").pack(pady=5)
        entry_descripcion = tk.Entry(ventana)
        entry_descripcion.pack(pady=5)

        tk.Label(ventana, text="Nivel del curso:", bg="#f0f0f0").pack(pady=5)
        entry_nivel = tk.Entry(ventana)
        entry_nivel.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_curso).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_curso())

    def ver_cursos(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Lista de Cursos")
        ventana.configure(bg="#f0f0f0")

        if not self.sistema.cursos:
            tk.Label(ventana, text="No hay cursos registrados.", bg="#f0f0f0").pack(pady=10)
        else:
            tk.Label(ventana, text="LISTA DE CURSOS:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)

            frame = tk.Frame(ventana)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame, bg="#f0f0f0")
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            for id, curso in self.sistema.cursos.items():
                tk.Label(scrollable_frame, text=f"ID: {id} | Nombre: {curso.nombre} | Nivel: {curso.nivel}", bg="#f0f0f0").pack(pady=5)
                tk.Label(scrollable_frame, text=f"  Descripción: {curso.descripcion}", bg="#f0f0f0").pack(pady=2)
                tk.Label(scrollable_frame, text=f"  Estudiantes: {len(curso.estudiantes)} | Materiales: {len(curso.materiales)}", bg="#f0f0f0").pack(pady=2)
                if curso.prerequisitos:
                    prerequisitos = ", ".join(self.sistema.cursos[pre_id].nombre for pre_id in curso.prerequisitos)
                    tk.Label(scrollable_frame, text=f"  Prerequisitos: {prerequisitos}", bg="#f0f0f0").pack(pady=2)
                tk.Label(scrollable_frame, text="", bg="#f0f0f0").pack(pady=5)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

# Agrega material a un curso específico.
    def agregar_material(self):
        def guardar_material():
            try:
                curso_id = int(entry_curso_id.get())
                material_id = int(entry_material_id.get())
                nombre = entry_nombre.get()
                tipo = entry_tipo.get()
                url = entry_url.get()

                if not all([curso_id, material_id, nombre, tipo, url]):
                    raise ValueError("Todos los campos deben estar llenos.")

                if curso_id in self.sistema.cursos:
                    material = Material(material_id, nombre, tipo, url)
                    if self.sistema.agregar_material(curso_id, material):
                        messagebox.showinfo("Éxito", f"Material agregado al curso {self.sistema.cursos[curso_id].nombre}!")
                else:
                    messagebox.showerror("Error", "Curso no encontrado.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Material a Curso")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        tk.Label(ventana, text="ID del material:", bg="#f0f0f0").pack(pady=5)
        entry_material_id = tk.Entry(ventana)
        entry_material_id.pack(pady=5)

        tk.Label(ventana, text="Nombre del material:", bg="#f0f0f0").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)

        tk.Label(ventana, text="Tipo (PDF, Video, Cuestionario):", bg="#f0f0f0").pack(pady=5)
        entry_tipo = tk.Entry(ventana)
        entry_tipo.pack(pady=5)

        tk.Label(ventana, text="URL o ruta:", bg="#f0f0f0").pack(pady=5)
        entry_url = tk.Entry(ventana)
        entry_url.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_material).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_material())

# Elimina un material de un curso y lo guarda como eliminado.
    def eliminar_material(self):
        def guardar_eliminar_material():
            curso_id = int(entry_curso_id.get())
            material_id = int(entry_material_id.get())
            if self.sistema.eliminar_material(curso_id, material_id):
                messagebox.showinfo("Éxito", "Material eliminado correctamente!")
            else:
                messagebox.showerror("Error", "Error al eliminar material. Verifique los IDs.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Material de Curso")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        tk.Label(ventana, text="ID del material:", bg="#f0f0f0").pack(pady=5)
        entry_material_id = tk.Entry(ventana)
        entry_material_id.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_eliminar_material).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_eliminar_material())

# Elimina un curso del sistema y lo guarda como eliminado.
    def eliminar_curso(self):
        def confirmar_eliminar_curso():
            curso_id = int(entry_curso_id.get())
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este curso?"):
                if self.sistema.eliminar_curso(curso_id):
                    messagebox.showinfo("Éxito", "Curso eliminado correctamente!")
                else:
                    messagebox.showerror("Error", "Error al eliminar curso. Verifique el ID.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Curso")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        ttk.Button(ventana, text="Eliminar", command=confirmar_eliminar_curso).pack(pady=10)
        ventana.bind('<Return>', lambda event: confirmar_eliminar_curso())

# Restaura un curso eliminado previamente.
    def restaurar_curso(self):
        def confirmar_restaurar_curso():
            curso_id = int(entry_curso_id.get())
            if self.sistema.restaurar_curso(curso_id):
                messagebox.showinfo("Éxito", "Curso restaurado correctamente!")
            else:
                messagebox.showerror("Error", "Error al restaurar curso. Verifique el ID.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Restaurar Curso Eliminado")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        ttk.Button(ventana, text="Restaurar", command=confirmar_restaurar_curso).pack(pady=10)
        ventana.bind('<Return>', lambda event: confirmar_restaurar_curso())

    def ver_materiales(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Ver Materiales de Cursos")
        ventana.configure(bg="#f0f0f0")

        if not self.sistema.cursos:
            tk.Label(ventana, text="No hay cursos registrados.", bg="#f0f0f0").pack(pady=10)
        else:
            tk.Label(ventana, text="LISTA DE MATERIALES:", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)

            frame = tk.Frame(ventana)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame, bg="#f0f0f0")
            scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
            scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

            for curso in self.sistema.cursos.values():
                for material in curso.materiales:
                    tk.Label(scrollable_frame, text=f"ID Material: {material.id} | Nombre: {material.nombre} | Tipo: {material.tipo}", bg="#f0f0f0").pack(pady=5)
                    tk.Label(scrollable_frame, text=f"  URL: {material.url}", bg="#f0f0f0").pack(pady=2)
                    tk.Label(scrollable_frame, text=f"  Curso: {curso.nombre}", bg="#f0f0f0").pack(pady=2)
                    tk.Label(scrollable_frame, text="", bg="#f0f0f0").pack(pady=5)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_y.pack(side="right", fill="y")
            scrollbar_x.pack(side="bottom", fill="x")

# Establece un curso como prerequisito de otro curso.
    def establecer_prerequisito(self):
        def guardar_prerequisito():
            curso_id = int(entry_curso_id.get())
            prerequisito_id = int(entry_prerequisito_id.get())
            if curso_id == prerequisito_id:
                messagebox.showerror("Error", "Un curso no puede ser prerequisito de sí mismo.")
            elif self.sistema.establecer_prerequisito(curso_id, prerequisito_id):
                messagebox.showinfo("Éxito", "Prerequisito establecido correctamente!")
            else:
                messagebox.showerror("Error", "Error al establecer prerequisito. Verifique los IDs.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Establecer Prerequisito")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso principal:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        tk.Label(ventana, text="ID del curso prerequisito:", bg="#f0f0f0").pack(pady=5)
        entry_prerequisito_id = tk.Entry(ventana)
        entry_prerequisito_id.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_prerequisito).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_prerequisito())

    def eliminar_prerequisito(self):
        def guardar_eliminar_prerequisito():
            curso_id = int(entry_curso_id.get())
            prerequisito_id = int(entry_prerequisito_id.get())
            if self.sistema.eliminar_prerequisito(curso_id, prerequisito_id):
                messagebox.showinfo("Éxito", "Prerequisito eliminado correctamente!")
            else:
                messagebox.showerror("Error", "Error al eliminar prerequisito. Verifique los IDs.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar Prerequisito")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso principal:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        tk.Label(ventana, text="ID del curso prerequisito:", bg="#f0f0f0").pack(pady=5)
        entry_prerequisito_id = tk.Entry(ventana)
        entry_prerequisito_id.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_eliminar_prerequisito).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_eliminar_prerequisito())

# Inscribe a un estudiante en un curso si cumple con los prerequisitos y hay cupo.
    def inscribir_estudiante(self):
        def guardar_inscripcion():
            try:
                estudiante_id = int(entry_estudiante_id.get())
                curso_id = int(entry_curso_id.get())
                resultado = self.sistema.inscribir_estudiante(estudiante_id, curso_id)

                if resultado == True:
                    messagebox.showinfo("Éxito", "Inscripción exitosa!")
                elif resultado == "lista_espera":
                    messagebox.showinfo("Información", "Curso lleno. Estudiante agregado a la lista de espera.")
                elif resultado == "ya_inscrito":
                    messagebox.showwarning("Advertencia", "El estudiante ya está inscrito en este curso.")
                elif resultado == "prerequisitos_faltantes":
                    estudiante = self.sistema.estudiantes[estudiante_id]
                    curso = self.sistema.cursos[curso_id]
                    prerequisitos_necesarios = self.sistema.grafo_cursos.aristas.get(curso_id, [])
                    cursos_estudiante = [c.id for c in estudiante.cursos]

                    prerequisitos_faltantes = []
                    for prereq_id in prerequisitos_necesarios:
                        if prereq_id not in cursos_estudiante:
                            if prereq_id in self.sistema.cursos:
                                prerequisitos_faltantes.append(self.sistema.cursos[prereq_id].nombre)

                    mensaje_error = f"El estudiante {estudiante.nombre} no puede inscribirse en {curso.nombre}.\n\n"
                    mensaje_error += f"Prerequisitos faltantes:\n"
                    for prereq in prerequisitos_faltantes:
                        mensaje_error += f"• {prereq}\n"

                    messagebox.showerror("Error - Prerequisitos Faltantes", mensaje_error)
                else:
                    messagebox.showerror("Error", "Error al inscribir estudiante. Verifique los datos.")
            except ValueError:
                messagebox.showerror("Error", "Por favor ingrese IDs válidos (números enteros).")
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {str(e)}")

        ventana = tk.Toplevel(self.root)
        ventana.title("Inscribir Estudiante en Curso")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del estudiante:", bg="#f0f0f0").pack(pady=5)
        entry_estudiante_id = tk.Entry(ventana)
        entry_estudiante_id.pack(pady=5)

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_inscripcion).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_inscripcion())

# Cancela la inscripción de un estudiante en un curso y maneja la lista de espera.
    def cancelar_inscripcion(self):
        def guardar_cancelacion():
            estudiante_id = int(entry_estudiante_id.get())
            curso_id = int(entry_curso_id.get())
            if self.sistema.cancelar_inscripcion(estudiante_id, curso_id):
                messagebox.showinfo("Éxito", "Inscripción cancelada correctamente.")
            else:
                messagebox.showerror("Error", "Error al cancelar inscripción. Verifique los datos.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Cancelar Inscripción")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del estudiante:", bg="#f0f0f0").pack(pady=5)
        entry_estudiante_id = tk.Entry(ventana)
        entry_estudiante_id.pack(pady=5)

        tk.Label(ventana, text="ID del curso:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        ttk.Button(ventana, text="Guardar", command=guardar_cancelacion).pack(pady=10)
        ventana.bind('<Return>', lambda event: guardar_cancelacion())

# Deshace la última inscripción o cancelación de curso realizada.
    def deshacer_ultima_accion(self):
        if self.sistema.deshacer_ultima_accion():
            messagebox.showinfo("Éxito", "Se ha deshecho la última acción.")
        else:
            messagebox.showerror("Error", "No hay acciones para deshacer.")

# Busca cursos por tema y opcionalmente por nivel.
    def buscar_cursos_tema(self):
        def buscar():
            tema = entry_tema.get()
            resultados = self.sistema.buscar_cursos(tema)
            if resultados:
                ventana_resultados = tk.Toplevel(ventana)
                ventana_resultados.title(f"Cursos relacionados con '{tema}'")
                ventana_resultados.configure(bg="#f0f0f0")

                tk.Label(ventana_resultados, text=f"Cursos relacionados con '{tema}':", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
                for curso in resultados:
                    tk.Label(ventana_resultados, text=f"- {curso.nombre} (Nivel: {curso.nivel})", bg="#f0f0f0").pack(pady=5)
            else:
                messagebox.showinfo("Información", f"No se encontraron cursos relacionados con '{tema}'.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Buscar Cursos por Tema")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="Tema a buscar:", bg="#f0f0f0").pack(pady=5)
        entry_tema = tk.Entry(ventana)
        entry_tema.pack(pady=5)

        ttk.Button(ventana, text="Buscar", command=buscar).pack(pady=10)
        ventana.bind('<Return>', lambda event: buscar())

# Busca cursos por tema y opcionalmente por nivel.
    def buscar_cursos_tema_nivel(self):
        def buscar():
            tema = entry_tema.get()
            nivel = entry_nivel.get()
            resultados = self.sistema.buscar_cursos(tema, nivel)
            if resultados:
                ventana_resultados = tk.Toplevel(ventana)
                ventana_resultados.title(f"Cursos de nivel '{nivel}' relacionados con '{tema}'")
                ventana_resultados.configure(bg="#f0f0f0")

                tk.Label(ventana_resultados, text=f"Cursos de nivel '{nivel}' relacionados con '{tema}':", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
                for curso in resultados:
                    tk.Label(ventana_resultados, text=f"- {curso.nombre} (Nivel: {curso.nivel})", bg="#f0f0f0").pack(pady=5)
            else:
                messagebox.showinfo("Información", f"No se encontraron cursos de nivel '{nivel}' relacionados con '{tema}'.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Buscar Cursos por Tema y Nivel")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="Tema a buscar:", bg="#f0f0f0").pack(pady=5)
        entry_tema = tk.Entry(ventana)
        entry_tema.pack(pady=5)

        tk.Label(ventana, text="Nivel:", bg="#f0f0f0").pack(pady=5)
        entry_nivel = tk.Entry(ventana)
        entry_nivel.pack(pady=5)

        ttk.Button(ventana, text="Buscar", command=buscar).pack(pady=10)
        ventana.bind('<Return>', lambda event: buscar())

    def recomendar_ruta(self):
        def buscar_ruta():
            curso_id = int(entry_curso_id.get())
            if curso_id in self.sistema.cursos:
                ruta = self.sistema.recomendar_cursos(curso_id)
                if ruta:
                    ventana_ruta = tk.Toplevel(ventana)
                    ventana_ruta.title(f"Ruta de aprendizaje para '{self.sistema.cursos[curso_id].nombre}'")
                    ventana_ruta.configure(bg="#f0f0f0")

                    tk.Label(ventana_ruta, text=f"Ruta de aprendizaje para '{self.sistema.cursos[curso_id].nombre}':", font=("Arial", 12), bg="#f0f0f0").pack(pady=10)
                    for i, curso in enumerate(ruta, 1):
                        tk.Label(ventana_ruta, text=f"{i}. {curso.nombre} (Nivel: {curso.nivel})", bg="#f0f0f0").pack(pady=5)
                else:
                    messagebox.showinfo("Información", "No se pudo determinar una ruta de aprendizaje.")
            else:
                messagebox.showerror("Error", "Curso no encontrado.")

        ventana = tk.Toplevel(self.root)
        ventana.title("Recomendar Ruta de Aprendizaje")
        ventana.configure(bg="#f0f0f0")

        tk.Label(ventana, text="ID del curso objetivo:", bg="#f0f0f0").pack(pady=5)
        entry_curso_id = tk.Entry(ventana)
        entry_curso_id.pack(pady=5)

        ttk.Button(ventana, text="Buscar", command=buscar_ruta).pack(pady=10)
        ventana.bind('<Return>', lambda event: buscar_ruta())

# Función principal que inicia la aplicación de la interfaz gráfica.
def main():
    root = tk.Tk()
    app = SistemaELearningGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()