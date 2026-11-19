# INTERFAZ-IA | Tópicos de Ingeniería Eléctrica II

**Curso interactivo de Ingeniería Eléctrica · Universidad Autónoma de Ciudad Juárez (UACJ)**  
**Profesor responsable:** Dr. Ernesto Sifuentes de la Hoya  
**Modalidad:** materiales digitales, actividades de programación, simulación y experimentación  
**Organización:** 16 semanas, tres unidades y proyectos de integración  
**Acceso al curso:** https://ernestosifuentes.github.io/topicos-ie/

---

## Presentación

**INTERFAZ-IA** es un entorno educativo para estudiar y desarrollar sistemas electrónicos de medición, adquisición de datos, supervisión y control. Integra contenidos teóricos, actividades de ingeniería, programas ejecutables, simulaciones y prácticas con microcontroladores. El curso está organizado como un recorrido progresivo: de la medición y la programación al diseño de sistemas instrumentados y el control automático.

Su orientación didáctica es **comprender los fundamentos, desarrollar los modelos, construir los sistemas, experimentar, analizar resultados y generar conocimiento**. La inteligencia artificial se integra como apoyo para el razonamiento y el aprendizaje, sin sustituir la justificación técnica, las mediciones ni la validación experimental.

El sitio permite consultar las lecciones desde el navegador y descargar los materiales de trabajo. Las actividades con dispositivos físicos, y determinados scripts y notebooks, requieren las herramientas y el hardware correspondientes.

## Objetivos formativos

Al desarrollar las actividades del curso, se busca que el estudiante sea capaz de:

- Explicar la arquitectura de una cadena de medición y sus principales fuentes de error.
- Programar microcontroladores ESP32 y adquirir señales analógicas y digitales.
- Procesar, visualizar, registrar e interpretar datos mediante Python.
- Analizar e implementar etapas de sensado y acondicionamiento de señal.
- Desarrollar aplicaciones de supervisión local e IoT.
- Formular modelos dinámicos, identificar parámetros y evaluar respuestas de sistemas térmicos.
- Implementar y comparar estrategias de control P, PI y PID discretas.
- Documentar resultados con criterios de reproducibilidad, seguridad y análisis crítico.

## Estructura académica: 16 semanas

### Unidad I. Sensores, microcontroladores y adquisición de datos (semanas 1–10)

| Semana | Tema | Acceso |
|:--:|---|---|
| 1 | Introducción a los sistemas electrónicos de medida: sensor–microcontrolador | [Lección 1](Semana_01/Leccion_01.html) |
| 2A | Introducción a Python para ingeniería | [Lección 2A](Semana_02/Leccion_02.html) |
| 2B | Adquisición de datos: comunicación serial y registro | [Lección 2B](Semana_02/Leccion_02B.html) |
| 3 | ESP32: programación y entradas/salidas digitales | [Lección 3](Semana_03/Leccion_03.html) |
| 4 | ESP32: conversión analógico-digital y medición | [Lección 4](Semana_04/Leccion_04.html) |
| 5 | ESP32 y adquisición de datos con Python | [Lección 5](Semana_05/Leccion_05.html) |
| 6 | Etapa de sensado | [Lección 6](Semana_06/Leccion_06.html) |
| 7 | Desarrollo de la cadena de señal | [Lección 7](Semana_07/Leccion_07.html) |
| 8 | Práctica 2: termómetro Pt2000 con divisor de voltaje | [Lección 8](Semana_08/Leccion_08.html) |
| 9 | Práctica 3: termómetro Pt2000 con puente de Wheatstone | [Lección 9](Semana_09/Leccion_09.html) |
| 10 | Proyecto 1: termostato digital con TMP36 y ESP32 | [Lección 10](Semana_10/Leccion_10.html) |

### Unidad II. Supervisión industrial, SCADA e IoT (semanas 11–12)

| Semana | Tema | Acceso |
|:--:|---|---|
| 11 | Supervisión industrial: fundamentos SCADA e IoT con ESP32 | [Lección 11](Semana_11/Leccion_11.html) |
| 12 | Proyecto 2: monitor de aceleración con supervisión local/IoT | [Lección 12](Semana_12/Leccion_12.html) |

### Unidad III. Modelado y control de sistemas embebidos (semanas 13–16)

| Semana | Tema | Acceso |
|:--:|---|---|
| 13 | Fundamentos de control automático y TCLab | [Lección 13](Semana_13/Leccion_13.html) |
| 14 | Modelado dinámico e identificación FOPDT | [Lección 14](Semana_14/Leccion_14.html) |
| 15 | Controladores P, PI y PID discretos | [Lección 15](Semana_15/Leccion_15.html) |
| 16 | Proyecto 3: control térmico con TCLab | [Lección 16](Semana_16/Leccion_16.html) |

## Recursos disponibles

Según la lección, el repositorio incluye páginas HTML, explicaciones y ejemplos, ilustraciones, guías PDF, documentos editables, cuadernos Jupyter (`.ipynb`), programas Python (`.py`), sketches Arduino (`.ino`), datos CSV, simuladores y recursos para las prácticas. La carpeta `Unidad_III_Recursos/` reúne scripts y datos para modelado y control de TCLab.

> **Importante:** algunos materiales incorporan contenido preexistente o de terceros. Su presencia en el repositorio no significa que estén cubiertos por las licencias de los materiales originales de INTERFAZ-IA. Consulte [Licenciamiento y derechos de terceros](#licenciamiento-y-derechos-de-terceros).

## Cómo utilizar el curso

1. Abra **[la página de inicio del curso](https://ernestosifuentes.github.io/topicos-ie/)**.
2. Revise la presentación, la organización por unidades y el calendario.
3. Seleccione la semana correspondiente y estudie su lección.
4. Descargue los programas, datos, guías o cuadernos indicados en cada actividad.
5. Realice las simulaciones o prácticas correspondientes; cuando se requiera hardware, verifique conexiones y condiciones de operación antes de energizar.
6. Registre resultados, compare teoría y medición, explique discrepancias y elabore la evidencia solicitada.

Los parámetros administrativos (año, días, horario y salón) se gestionan en la página de inicio del curso. Consulte el syllabus y las instrucciones docentes para la evaluación formal.

## Herramientas y requisitos

- **Navegador web actual:** para visualizar el sitio y sus recursos HTML.
- **Python 3 y bibliotecas pertinentes:** para ejecutar los scripts de adquisición, análisis, GUI y control cuando así se requiera; cada práctica puede tener dependencias específicas.
- **Jupyter o Google Colab:** para trabajar con cuadernos `.ipynb`, según la práctica.
- **Arduino IDE y ESP32:** para las actividades con microcontroladores y firmware.
- **Hardware experimental:** sensores, circuitos, fuente de alimentación e interfaces requeridas por cada práctica; para la Unidad III, una plataforma TCLab compatible cuando se efectúe experimentación física.
- **Conexión a internet:** necesaria para acceder al sitio y a servicios externos; las actividades locales pueden funcionar sin conexión según sus dependencias.

Los archivos ejecutables de Windows (`.bat`) no se ejecutan dentro de GitHub Pages. Se descargan y utilizan únicamente en un equipo compatible, bajo supervisión y después de revisar su contenido.

### Sobre las simulaciones y la validación experimental

Los datos y escenarios marcados como **simulados** son recursos educativos y no constituyen resultados de una validación física. Las conclusiones experimentales requieren montaje, calibración, instrumentos de referencia y condiciones de medición documentadas. Respete los límites eléctricos y las recomendaciones de seguridad de cada práctica.

## Tutor de inteligencia artificial

Las actividades del curso pueden incluir consignas para consultar un asistente de IA. El repositorio conserva un archivo `servidor_tutor_ia.py`, que implementa una modalidad de tutor generativo para un entorno con servidor y una clave de API configurada como variable de entorno. **GitHub Pages no ejecuta ese servidor Python ni proporciona por sí mismo respuestas generativas.** Nunca publique claves de API, credenciales de redes ni información personal de estudiantes en este repositorio.

## Organización del repositorio

```text
topicos-ie/
├── index.html
├── INTERFAZ-IA_Inicio_Topicos_IE_II.html
├── INTERFAZ-IA_Calendario_16_Semanas.csv
├── Semana_01/ ... Semana_16/
│   ├── Leccion_XX.html
│   └── recursos, materiales, imágenes y códigos según la semana
├── Unidad_III_Recursos/
├── Syllabus_Oficial_2026-II.pdf
├── servidor_tutor_ia.py
├── README.md
├── LICENSE.md
└── LICENSE-APACHE-2.0.txt
```

Los nombres detallados de archivos y subcarpetas pueden variar por semana. Se recomienda mantener las rutas originales para no romper enlaces del sitio.

## Publicación y mantenimiento

El repositorio se publica mediante **GitHub Pages**, desde la rama `main` y la carpeta raíz (`/(root)`). El archivo `index.html` es la puerta de entrada. Las modificaciones al curso deben probarse antes de compartirse con los estudiantes: navegación, enlaces, descargas, simuladores y visualización en dispositivos móviles.

**Repositorio:** https://github.com/ErnestoSifuentes/topicos-ie  
**Sitio público:** https://ernestosifuentes.github.io/topicos-ie/

## Licenciamiento y derechos de terceros

El repositorio utiliza el mismo criterio dual de licencias empleado para el curso de Electrónica II:

- **Contenido educativo original** creado por el titular de los derechos para este proyecto (redacción propia, explicaciones, figuras y materiales originales, cuando corresponda): [Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](LICENSE.md).
- **Software original** cuyos derechos correspondan al titular del proyecto (scripts Python, código de microcontroladores y otros componentes propios identificables): [Apache License, Version 2.0](LICENSE-APACHE-2.0.txt).
- **Materiales de terceros**, como documentos fuente, presentaciones, fotografías, videos, bibliotecas o archivos incorporados con derechos ajenos: **no quedan relicenciados** por estos documentos; se aplican sus propios avisos, autorizaciones y condiciones.

La disponibilidad pública del repositorio no equivale a una cesión universal de derechos. Si un recurso ajeno no cuenta con permiso para redistribución pública, corresponde sustituirlo por un enlace autorizado o retirarlo del repositorio antes de difundirlo.

## Créditos institucionales

**Responsable académico:** Dr. Ernesto Sifuentes de la Hoya  
**Institución:** Universidad Autónoma de Ciudad Juárez (UACJ)  
**Proyecto educativo:** INTERFAZ-IA  

La mención institucional identifica el contexto académico del curso; no implica que la universidad otorgue derechos sobre materiales de terceros ni que avale usos externos del repositorio.
