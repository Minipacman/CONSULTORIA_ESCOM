import os
import re
import subprocess
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

PL_FILENAME = 'proyecto.pl'

def ejecutar_consulta_prolog_simple(query):
    try:
        cmd = ['swipl', '-s', PL_FILENAME, '-g', f"findall(X, ({query}), L), write_canonical(L), nl.", '-t', 'halt']
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out = resultado.stdout.strip()
        elementos = re.findall(r"'([^']+)'", out)
        if not elementos:
            elementos = re.findall(r"\b([A-Za-z0-9_]+)\b", out)
        return set(elementos)
    except Exception:
        return set()

def cargar_datos_con_prolog():
    materias = []
    if not os.path.exists(PL_FILENAME):
        return materias
    
    with open(PL_FILENAME, 'r', encoding='utf-8') as f:
        content = f.read()
    
    profesores_multiturno = ejecutar_consulta_prolog_simple("profesor_multiturno(P)")
    materias_alta_demanda = ejecutar_consulta_prolog_simple("materia_alta_demanda(M)")
    grupos_matutino_puro = ejecutar_consulta_prolog_simple("grupo_turno_matutino_puro(G)")
    
    patron = r"materia\((\d+),\s*'([^']+)',\s*'([^']+)',\s*(\w+),\s*'([^']+)'\)"
    matches = re.findall(patron, content)
    
    for idx, (semestre, profe, materia, turno, grupo) in enumerate(matches, 1):
        mat_upper = materia.upper()
        if any(k in mat_upper for k in ['PROGRAMACION', 'ALGORITMOS', 'DATOS', 'INTELIGENCIA', 'WEB', 'SOFTWARE', 'COMPUTO', 'REDES NEURONALES', 'BIG DATA', 'VOZ', 'MAQUINA']):
            academia = "Programacion"
        elif any(k in mat_upper for k in ['CALCULO', 'ALGEBRA', 'DISCRETAS', 'ESTADISTICA', 'MATEMATICAS', 'ECUACIONES', 'TEORIA']):
            academia = "Matematicas"
        elif any(k in mat_upper for k in ['MECANICA', 'DISENO DIGITAL', 'SENALES', 'VISION', 'EMBEBIDOS', 'ROBOTS']):
            academia = "Electronica"
        else:
            academia = "Ciencias Sociales"

        materias.append({
            "id": idx,
            "semestre": int(semestre),
            "profesor": profe,
            "materia": materia,
            "turno": turno,
            "grupo": grupo,
            "academia": academia,
            "es_multiturno": profe in profesores_multiturno,
            "es_alta_demanda": materia in materias_alta_demanda,
            "es_matutino_puro": grupo in grupos_matutino_puro
        })
    return materias

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Académico Inteligente - Prolog & Flask</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">

    <header class="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center space-x-3">
                <div class="bg-indigo-600 p-2.5 rounded-xl text-white shadow-lg shadow-indigo-600/30">
                    <i class="fa-solid fa-graduation-cap text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-wide">Consulta de materias de ESCOM-IA</h1>
                    <p class="text-xs text-slate-400"></p>
                </div>
            </div>
            <div class="flex gap-2">
                <button onclick="cambiarVista('buscador')" id="btnBuscador" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white transition">MATERIAS</button>
                <button onclick="cambiarVista('horario')" id="btnHorario" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">Borrador de horario(<span id="contadorBorrador">0</span>)</button>
                <button onclick="cambiarVista('seriadas')" id="btnSeriadas" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition">Materias seriadas</button>
            </div>
        </div>
    </header>

    <main class="flex-grow max-w-7xl w-full mx-auto px-4 py-8">
        
        <!-- VISTA 1: MATERIAS-->
        <section id="vistaBuscador" class="space-y-6">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-xl flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div class="relative md:col-span-1">
                        <i class="fa-solid fa-magnifying-glass absolute left-3 top-3.5 text-slate-400"></i>
                        <input type="text" id="inputBusqueda" onkeyup="filtrarMaterias()" placeholder="Buscar materia o profesor..." 
                            class="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500">
                    </div>
                    <div>
                        <select id="selectSemestre" onchange="filtrarMaterias()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500">
                            <option value="Todos">Todos los Semestres</option>
                            <option value="1">1º Semestre</option>
                            <option value="2">2º Semestre</option>
                            <option value="3">3º Semestre</option>
                            <option value="4">4º Semestre</option>
                            <option value="5">5º Semestre</option>
                            <option value="6">6º Semestre</option>
                            <option value="7">7º Semestre</option>
                            <option value="8">8º Semestre</option>
                        </select>
                    </div>
                    <div>
                        <select id="selectTurno" onchange="filtrarMaterias()" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500">
                            <option value="Todos">Todos los Turnos</option>
                            <option value="matutino">Matutino</option>
                            <option value="vespertino">Vespertino</option>
                        </select>
                    </div>
                    <div>
                        <select id="selectRegla" onchange="filtrarMaterias()" class="w-full bg-slate-900 border border-emerald-600/60 rounded-lg px-3 py-2 text-sm text-emerald-300 focus:outline-none focus:border-emerald-500">
                            <option value="Todos">Mas filtros</option>
                            <option value="multiturno">Profesores Multiturno</option>
                            <option value="alta_demanda">Materias de Alta Demanda</option>
                            <option value="matutino_puro">Grupos exclusivos Matutinos</option>
                            <option value="matutino_puro">Grupos exclusivos Vespertinos</option>
                        </select>
                    </div>
                </div>
                
                <div class="flex flex-wrap gap-2 pt-3 border-t border-slate-700/60" id="botonesAcademias">
                    <button onclick="filtrarAcademia('Todas')" id="acad-Todas" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white transition">Todas las Academias</button>
                    <button onclick="filtrarAcademia('Programacion')" id="acad-Programacion" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 text-slate-300 hover:bg-slate-600 transition">Programación</button>
                    <button onclick="filtrarAcademia('Matematicas')" id="acad-Matematicas" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 text-slate-300 hover:bg-slate-600 transition">Matemáticas</button>
                    <button onclick="filtrarAcademia('Electronica')" id="acad-Electronica" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 text-slate-300 hover:bg-slate-600 transition">Electrónica y Sistemas</button>
                    <button onclick="filtrarAcademia('Ciencias Sociales')" id="acad-Ciencias Sociales" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 text-slate-300 hover:bg-slate-600 transition">Ciencias Sociales y Admin</button>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="contenedorBusqueda"></div>
        </section>

        <!-- VISTA 2: HORARIO-->
        <section id="vistaHorario" class="space-y-6 hidden">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                <div class="flex justify-between items-center border-b border-slate-700 pb-4 mb-4">
                    <h2 class="text-lg font-semibold text-slate-200"><i class="fa-solid fa-calendar-days text-indigo-400 mr-2"></i> Tu Horario Personalizado</h2>
                    <button onclick="limpiarHorario()" class="text-xs bg-rose-500/20 text-rose-400 hover:bg-rose-500 hover:text-white px-3 py-1.5 rounded-lg border border-rose-500/30 transition">Vaciar Borrador</button>
                </div>
                <div id="contenedorBorrador" class="space-y-3">
                    <p class="text-xs text-slate-400 py-6">Aún no has agregado materias a tu borrador.</p>
                </div>
            </div>
        </section>

        <!-- VISTA 3: MATERIAS SERIADAS -->
        <section id="vistaSeriadas" class="space-y-6 hidden">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-700 pb-4">
                    <div>
                        <h2 class="text-lg font-semibold text-slate-200"><i class="fa-solid fa-route text-indigo-400 mr-2"></i> Rutas y Seriación Curricular</h2>
                        <p class="text-xs text-slate-400 mt-1">Selecciona una línea de especialidad para visualizar su orden consecutivo.</p>
                    </div>
                    <div class="w-full sm:w-72">
                        <select id="selectFiltroSeriada" onchange="renderRutaSeriada()" class="w-full bg-slate-900 border border-indigo-500 rounded-lg px-3 py-2 text-sm text-indigo-300 focus:outline-none">
                            <option value="programacion">1. Ruta de Programación</option>
                            <option value="calculo">2. Ruta de Cálculo</option>
                            <option value="electronica">3. Ruta de Electrónica / Discretas</option>
                        </select>
                    </div>
                </div>
                <div class="relative border-l-2 border-indigo-500/40 ml-4 pl-6 space-y-6" id="contenedorRutaSeriada">
                    <!-- Dinámico -->
                </div>
            </div>
        </section>

    </main>

    <script>
        let baseDatos = [];
        let borrador = [];
        let academiaActual = 'Todas';

        // Definición de las líneas seriadas exactas ordenadas por secuencia lógica
        const RUTAS_SERIADAS = {
            programacion: [
                "FUNDAMENTOS DE PROGRAMACION",
                "ALGORITMOS Y ESTRUCTURAS DE DATOS",
                "ANALISIS Y DISEÑO DE ALGORITMOS",
                "PARADIGMAS DE PROGRAMACION",
                "ANALISIS Y DISEÑO DE SISTEMAS",
                "TEORIA DE LA COMPUTACION",
                "INGENIERIA DE SOFTWARE PARA SISTEMAS INTELIGENTES",
                "COMPUTO PARALELO"
            ],
            calculo: [
                "CALCULO",
                "CALCULO MULTIVARIABLE",
                "ECUACIONES DIFERENCIALES",
                "MATEMATICAS AVANZADAS PARA LA INGENIERIA",
                "PROBABILIDAD Y ESTADISTICA"
            ],
            electronica: [
                "MATEMATICAS DISCRETAS",
                "FUNDAMENTOS DE DISEÑO DIGITAL",
                "DISEÑO DE SISTEMAS DIGITALES",
                "PROCESAMIENTO DIGITAL DE IMAGENES"
            ]
        };

        async function init() {
            let res = await fetch('/api/datos');
            baseDatos = await res.json();
            filtrarMaterias();
            renderRutaSeriada();
        }

        function cambiarVista(vista) {
            ['buscador', 'horario', 'seriadas'].forEach(v => {
                document.getElementById('vista' + v.charAt(0).toUpperCase() + v.slice(1)).classList.add('hidden');
                document.getElementById('btn' + v.charAt(0).toUpperCase() + v.slice(1)).className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition";
            });

            document.getElementById('vista' + vista.charAt(0).toUpperCase() + vista.slice(1)).classList.remove('hidden');
            let btnActivo = document.getElementById('btn' + vista.charAt(0).toUpperCase() + vista.slice(1));
            btnActivo.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white transition";

            if(vista === 'horario') renderBorrador();
            if(vista === 'seriadas') renderRutaSeriada();
        }

        function filtrarAcademia(academia) {
            academiaActual = academia;
            ['Todas', 'Programacion', 'Matematicas', 'Electronica', 'Ciencias Sociales'].forEach(ac => {
                let btn = document.getElementById('acad-' + ac);
                if(btn) {
                    btn.className = ac === academia ? "px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white transition" : "px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 text-slate-300 hover:bg-slate-600 transition";
                }
            });
            filtrarMaterias();
        }

        function mostrarBusqueda(datos) {
            let cont = document.getElementById('contenedorBusqueda');
            cont.innerHTML = '';
            if(datos.length === 0) {
                cont.innerHTML = `<p class="text-xs text-slate-400 col-span-full py-4 text-center">No se encontraron materias con esos criterios.</p>`;
                return;
            }
            datos.forEach(item => {
                let agregado = borrador.some(b => b.id === item.id);
                let badges = '';
                if(item.es_multiturno) badges += `<span class="text-[9px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 font-semibold"><i class="fa-solid fa-bolt mr-1"></i>Multiturno</span>`;
                if(item.es_alta_demanda) badges += `<span class="text-[9px] bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30 font-semibold"><i class="fa-solid fa-fire mr-1"></i>Alta Demanda</span>`;

                cont.innerHTML += `
                    <div class="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col justify-between shadow-lg">
                        <div>
                            <div class="flex justify-between items-center">
                                <span class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">${item.grupo} • Turno ${item.turno}</span>
                                <span class="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded">${item.academia}</span>
                            </div>
                            <h3 class="font-bold text-slate-100 text-sm mt-1">${item.materia}</h3>
                            <p class="text-xs text-slate-400 mt-1"><i class="fa-regular fa-user mr-1"></i> Prof. ${item.profesor}</p>
                            <div class="flex flex-wrap gap-1 mt-2">${badges}</div>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-700 flex justify-between items-center">
                            <span class="text-xs text-slate-400">${item.semestre}º Semestre</span>
                            <button onclick="toggleBorrador(${item.id})" class="px-3 py-1.5 rounded-lg text-xs font-medium ${agregado ? 'bg-rose-600/20 text-rose-400 border border-rose-500/30' : 'bg-indigo-600 text-white hover:bg-indigo-500'} transition">
                                ${agregado ? '<i class="fa-solid fa-check mr-1"></i> En Borrador' : '<i class="fa-solid fa-plus mr-1"></i> Agregar'}
                            </button>
                        </div>
                    </div>`;
            });
        }

        function filtrarMaterias() {
            let query = document.getElementById('inputBusqueda').value.toLowerCase();
            let semestreSeleccionado = document.getElementById('selectSemestre').value;
            let turnoSeleccionado = document.getElementById('selectTurno').value;
            let reglaSeleccionada = document.getElementById('selectRegla').value;

            let filtrados = baseDatos.filter(item => {
                let cumpleAcademia = (academiaActual === 'Todas' || item.academia === academiaActual);
                let cumpleSemestre = (semestreSeleccionado === 'Todos' || item.semestre.toString() === semestreSeleccionado);
                let cumpleTurno = (turnoSeleccionado === 'Todos' || item.turno === turnoSeleccionado);
                let cumpleRegla = true;
                if(reglaSeleccionada === 'multiturno') cumpleRegla = item.es_multiturno;
                else if(reglaSeleccionada === 'alta_demanda') cumpleRegla = item.es_alta_demanda;
                else if(reglaSeleccionada === 'matutino_puro') cumpleRegla = item.es_matutino_puro;

                let cumpleTexto = (item.materia.toLowerCase().includes(query) || item.profesor.toLowerCase().includes(query) || item.grupo.toLowerCase().includes(query));
                return cumpleAcademia && cumpleSemestre && cumpleTurno && cumpleRegla && cumpleTexto;
            });
            mostrarBusqueda(filtrados);
        }

        function renderRutaSeriada() {
            let tipo = document.getElementById('selectFiltroSeriada').value;
            let secuencia = RUTAS_SERIADAS[tipo];
            let cont = document.getElementById('contenedorRutaSeriada');
            cont.innerHTML = '';

            secuencia.forEach((nombreMateria, index) => {
                // Buscar registros reales en la base de datos para esta materia
                let registros = baseDatos.filter(b => b.materia.toUpperCase().includes(nombreMateria));
                let semestreRef = registros.length > 0 ? registros[0].semestre : 'N/A';
                let academiaRef = registros.length > 0 ? registros[0].academia : 'Especialidad';

                cont.innerHTML += `
                    <div class="relative">
                        <span class="absolute -left-[35px] top-0 bg-indigo-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shadow">${index + 1}</span>
                        <div class="bg-slate-900 border border-slate-700/80 p-4 rounded-xl shadow">
                            <div class="flex justify-between items-center">
                                <h4 class="font-bold text-sm text-indigo-300">${nombreMateria}</h4>
                                <span class="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">Semestre ${semestreRef}</span>
                            </div>
                            <p class="text-xs text-slate-400 mt-2">
                                <i class="fa-solid fa-chalkboard-user mr-1"></i> Profesores impartiendo en plan actual: 
                                <span class="text-slate-200 font-medium">${registros.length > 0 ? [...new Set(registros.map(r => r.profesor))].join(', ') : 'Pendiente de asignación'}</span>
                            </p>
                        </div>
                    </div>`;
            });
        }

        function toggleBorrador(id) {
            let item = baseDatos.find(b => b.id === id);
            let index = borrador.findIndex(b => b.id === id);
            if(index > -1) { borrador.splice(index, 1); } else { borrador.push(item); }
            document.getElementById('contadorBorrador').innerText = borrador.length;
            filtrarMaterias();
        }

        function renderBorrador() {
            let cont = document.getElementById('contenedorBorrador');
            if(borrador.length === 0) {
                cont.innerHTML = `<p class="text-xs text-slate-400 py-4">Aún no has agregado materias a tu borrador.</p>`;
                return;
            }
            cont.innerHTML = '';
            borrador.forEach(item => {
                cont.innerHTML += `
                    <div class="bg-slate-900 border border-slate-700 p-4 rounded-lg flex justify-between items-center">
                        <div>
                            <span class="text-xs font-bold text-indigo-400">${item.grupo} • ${item.turno}</span>
                            <h4 class="font-bold text-sm text-slate-100">${item.materia}</h4>
                            <p class="text-xs text-slate-400">Prof. ${item.profesor} (${item.semestre}º Semestre)</p>
                        </div>
                        <button onclick="toggleBorrador(${item.id}); renderBorrador();" class="text-xs text-rose-400 hover:text-rose-300 p-2"><i class="fa-solid fa-trash"></i></button>
                    </div>`;
            });
        }

        function limpiarHorario() {
            borrador = [];
            document.getElementById('contadorBorrador').innerText = 0;
            renderBorrador();
            filtrarMaterias();
        }

        init();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/datos', methods=['GET'])
def get_datos():
    return jsonify(cargar_datos_con_prolog())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)