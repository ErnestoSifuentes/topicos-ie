"""Servidor local opcional para el tutor IA de INTERFAZ-IA.
Uso: python servidor_tutor_ia.py
Dependencias para el tutor generativo: pip install openai
Variable de entorno: OPENAI_API_KEY. Jamás introduzca claves API en HTML.
Si no se configura la clave, sirve igualmente el curso web sin IA remota.
"""
import http.server
import json
import mimetypes
import os
from pathlib import Path
import socketserver
import webbrowser

BASE = Path(__file__).resolve().parent
PORT = int(os.environ.get('INTERFAZ_PORT', '8765'))
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5.5')
CONTEXT = {
    'medicion': 'Medir, mensurando, medición directa/indirecta, media, s muestral, k*s y unidades.',
    'cadena': 'Cadena de medida sensor–microcontrolador, funciones de los bloques y sensores.',
    'adc': 'ADC ideal, q=Vref/2^N, código cero-based y uno-based, muestreo, cuantificación.',
    'experimento': 'Nueve lecturas de mesa, quince de distancia, veinte de voltaje, diez voltajes de ejemplo; análisis sin fabricación de datos.',
    'diseno': 'Metodología, especificaciones, exactitud, resolución, incertidumbre y validación.',
}
PROMPT = '''Eres tutor académico de Tópicos de Ingeniería Eléctrica II, UACJ, Semana 1. Enseñas con método socrático y rigor metrológico.
Limítate al contexto proporcionado, pregunta para diagnosticar, ofrece pistas graduadas y explica fundamentos con unidades.
No redactes soluciones completas de tareas evaluadas, no inventes datos, y distingue demostraciones teóricas de resultados experimentales.
Distingue banda descriptiva k*s de incertidumbre expandida de la media: la primera NO sustituye el análisis metrológico formal.
Si el estudiante presenta un cálculo, revisa dimensiones, procedimiento y posibles errores. Responde en español, claro y conciso.'''


class Server(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def do_POST(self):
        if self.path != '/api/tutor':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 6500:
                self.send_json(413, {'error': 'Consulta vacía o excesivamente larga.'})
                return
            req = json.loads(self.rfile.read(length))
            topic = str(req.get('tema', 'medicion'))
            question = str(req.get('pregunta', '')).strip()[:2200]
            if topic not in CONTEXT:
                self.send_json(400, {'error': 'Tema no autorizado para esta lección.'})
                return
            if not question:
                self.send_json(400, {'error': 'Escriba primero su pregunta para el tutor.'})
                return
            if not os.environ.get('OPENAI_API_KEY'):
                self.send_json(503, {'error': 'Se requiere OPENAI_API_KEY en el servidor.'})
                return
            try:
                from openai import OpenAI
            except ImportError:
                self.send_json(503, {'error': 'Instale la dependencia con: pip install openai'})
                return
            client = OpenAI(timeout=28.0, max_retries=0)
            response = client.responses.create(
                model=MODEL,
                instructions=PROMPT,
                input=f'Tema y alcance de la semana: {CONTEXT[topic]}\nPregunta del estudiante: {question}',
                max_output_tokens=620,
                store=False,
            )
            self.send_json(200, {'answer': response.output_text or 'El tutor no devolvió texto.'})
        except Exception:
            self.send_json(502, {'error': 'No fue posible consultar el modelo. Revise configuración, conectividad y acceso a API.'})

    def send_json(self, status, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


if __name__ == '__main__':
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Server) as srv:
        url = f'http://127.0.0.1:{PORT}/INTERFAZ-IA_Inicio_Topicos_IE_II.html'
        print('INTERFAZ-IA:', url)
        print('Tutor IA:', 'configurado' if os.environ.get('OPENAI_API_KEY') else 'sin clave; puede usar copiar consulta')
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\nServidor cerrado')
