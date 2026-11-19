#!/usr/bin/env python3
"""INTERFAZ-IA | Semana 10 | Proyecto 1: TMP36 + ESP32 clásico + Python.
Modo simulación disponible. Los actuadores físicos son SOLO LEDs de baja tensión.
"""
import csv
import math
import time
from datetime import datetime
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tmp36_modelo import CadenaTMP36, Control, Estado

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None

NAVY = '#183044'
TEAL = '#0f6e72'
GRAY = '#57717c'

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('INTERFAZ-IA · Proyecto 1 · Termostato TMP36')
        self.geometry('1250x790')
        self.minsize(970, 640)
        self.protocol('WM_DELETE_WINDOW', self.salir)
        self.ser = None
        self.conectado = False
        self.adquiriendo = False
        self.muestras = []
        self.errores = 0
        self.t0 = time.monotonic()
        self.x = deque(maxlen=500)
        self.y = deque(maxlen=500)
        self.model = CadenaTMP36()
        self.control = Control()
        self.modo = tk.StringVar(value='SIMULACIÓN')
        self.puerto = tk.StringVar(value='COM3')
        self.salidas = tk.BooleanVar(value=False)
        self.lim_inf = tk.StringVar(value='35')
        self.lim_sup = tk.StringVar(value='45')
        self.histeresis = tk.StringVar(value='1.0')
        self.g = tk.StringVar(value='2.49')
        self.vref_resta = tk.StringVar(value='0.500')
        self.offset_sensor = tk.StringVar(value='0.500')
        self.sens = tk.StringVar(value='0.010')
        self.lectura = tk.StringVar(value='— °C')
        self.detalles = tk.StringVar(value='Vs — V   |   V* — V   |   Vo — V   |   ADC —')
        self.estado = tk.StringVar(value='APAGADO')
        self.estadisticas = tk.StringVar(value='N = 0   |   Media —   |   Desviación —')
        self.aviso = tk.StringVar(value='Desconectado · GPIO22 y GPIO23 apagados')
        self._ui()
        self.after(100, self._paso)

    def _ui(self):
        style = ttk.Style(self)
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('Main.TButton', font=('Segoe UI', 10, 'bold'), padding=(12, 11))
        style.configure('TButton', padding=(8, 7))
        head = ttk.Frame(self, padding=(18, 15))
        head.pack(fill='x')
        ttk.Label(head, text='TERMOSTATO DIGITAL  ·  TMP36', font=('Segoe UI', 21, 'bold'), foreground=NAVY).pack(side='left')
        ttk.Label(head, text='PROYECTO 1  /  SEMANA 10', foreground=TEAL, font=('Segoe UI', 10, 'bold')).pack(side='right')
        settings = ttk.LabelFrame(self, text='Conexión y parámetros del termostato', padding=11)
        settings.pack(fill='x', padx=17, pady=4)
        top = ttk.Frame(settings)
        top.pack(fill='x')
        for label, var, width in [('Modo', self.modo, 14), ('Puerto', self.puerto, 10),
                                  ('Límite inferior (°C)', self.lim_inf, 8), ('Límite superior (°C)', self.lim_sup, 8),
                                  ('Histéresis (°C)', self.histeresis, 8)]:
            cell = ttk.Frame(top)
            cell.pack(side='left', padx=(0, 16))
            ttk.Label(cell, text=label).pack(anchor='w')
            if label == 'Modo':
                ttk.Combobox(cell, textvariable=var, values=['SIMULACIÓN', 'USB'], state='readonly', width=width).pack()
            else:
                ttk.Entry(cell, textvariable=var, width=width).pack()
        ttk.Button(top, text='Buscar puertos', command=self.buscar).pack(side='right')
        ttk.Checkbutton(settings, text='Habilitar salidas de laboratorio (SOLO dos LEDs: GPIO22 frío / GPIO23 calor)',
                        variable=self.salidas, command=self._armar).pack(anchor='w', pady=(12, 2))
        actions = ttk.Frame(self, padding=(17, 8))
        actions.pack(fill='x')
        for label, action in [('Conectar', self.conectar), ('Adquirir', self.adquirir),
                              ('Procesar', self.procesar), ('Guardar', self.guardar), ('Salir', self.salir)]:
            ttk.Button(actions, text=label, command=action, style='Main.TButton').pack(side='left', padx=(0, 8))
        ttk.Button(actions, text='Detener / salidas OFF', command=self.detener).pack(side='right')
        params = ttk.LabelFrame(self, text='Cadena de señal · editar según valores reales medidos', padding=10)
        params.pack(fill='x', padx=17, pady=3)
        for col, (label, var) in enumerate([('Ganancia G', self.g), ('Referencia restada (V)', self.vref_resta),
                                           ('Offset sensor (V)', self.offset_sensor), ('Sensibilidad (V/°C)', self.sens)]):
            cell = ttk.Frame(params)
            cell.grid(row=0, column=col, padx=(0, 23), sticky='w')
            ttk.Label(cell, text=label).pack(anchor='w')
            ttk.Entry(cell, textvariable=var, width=17).pack()
        mid = ttk.Frame(self, padding=(17, 7))
        mid.pack(fill='both', expand=True)
        plot = ttk.Frame(mid)
        plot.pack(side='left', fill='both', expand=True)
        row = ttk.Frame(plot)
        row.pack(fill='x')
        ttk.Label(row, textvariable=self.lectura, font=('Segoe UI', 30, 'bold'), foreground=TEAL).pack(side='left')
        self.indicador = tk.Label(row, textvariable=self.estado, font=('Segoe UI', 12, 'bold'),
                                  bg='#e1eaec', fg=NAVY, width=17, pady=10)
        self.indicador.pack(side='right', padx=8)
        ttk.Label(plot, textvariable=self.detalles, foreground=GRAY).pack(anchor='w')
        ttk.Label(plot, textvariable=self.estadisticas, foreground=GRAY).pack(anchor='w')
        ttk.Label(plot, textvariable=self.aviso, foreground=GRAY, wraplength=700).pack(anchor='w', pady=7)
        fig = Figure(figsize=(7.2, 4.3), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel('Tiempo de adquisición (s)')
        self.ax.set_ylabel('Temperatura (°C)')
        self.ax.set_title('Historial de temperatura')
        self.ax.grid(True, alpha=.24)
        self.line, = self.ax.plot([], [], color='#116f72', lw=2, label='Temperatura estimada')
        self.line_inf = self.ax.axhline(35, color='#275c83', linestyle='--', label='Límite inferior')
        self.line_sup = self.ax.axhline(45, color='#9a6330', linestyle='--', label='Límite superior')
        self.ax.legend(loc='upper left', fontsize=8)
        self.canvas = FigureCanvasTkAgg(fig, master=plot)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        side = ttk.LabelFrame(mid, text='Registro de datos', padding=7)
        side.pack(side='right', fill='y', padx=(12, 0))
        self.lista = ttk.Treeview(side, columns=('t', 'D', 'Vo', 'T', 'S'), show='headings', height=19)
        for key, label, width in [('t', 't (s)', 69), ('D', 'ADC', 65), ('Vo', 'Vo (V)', 74),
                                  ('T', 'T (°C)', 76), ('S', 'Estado', 100)]:
            self.lista.heading(key, text=label)
            self.lista.column(key, width=width, anchor='center')
        scrollbar = ttk.Scrollbar(side, orient='vertical', command=self.lista.yview)
        self.lista.configure(yscroll=scrollbar.set)
        self.lista.pack(side='left', fill='y')
        scrollbar.pack(side='left', fill='y')
        ttk.Label(self, text='Seguridad: demostración únicamente con LEDs y resistencias a 3.3 V. No conectar relevadores de red, calefactores ni compresores.',
                  foreground='#925133', padding=(19, 10)).pack(anchor='w')

    @staticmethod
    def _num(s):
        return float(s.get().strip().replace(',', '.'))

    def _configurar(self):
        m = CadenaTMP36(sensibilidad=self._num(self.sens), offset_sensor=self._num(self.offset_sensor),
                        referencia_resta=self._num(self.vref_resta), ganancia=self._num(self.g))
        m.validar()
        c = Control(self._num(self.lim_inf), self._num(self.lim_sup), self._num(self.histeresis))
        return m, c

    def buscar(self):
        if list_ports is None:
            messagebox.showwarning('Dependencias', 'Instale pyserial con: pip install -r requirements.txt')
            return
        ports = [p.device for p in list_ports.comports()]
        if ports:
            self.puerto.set(ports[0])
        messagebox.showinfo('Puertos disponibles', '\n'.join(ports) if ports else 'Sin puertos detectados')

    def _write(self, command):
        if self.ser:
            try:
                self.ser.write((command + '\n').encode('ascii'))
                return True
            except (OSError, Exception):
                self.aviso.set('Error de comunicación. Salidas desactivadas por vigilancia del ESP32.')
                self.detener()
        return False

    def _apagar(self):
        if self.ser:
            try:
                self.ser.write(b'N\n')
            except Exception:
                pass
        self.control.apagar()
        self._indicador(Estado.APAGADO)

    def _indicador(self, state):
        self.estado.set(state.value)
        pal = {Estado.APAGADO: '#e1eaec', Estado.CALEFACCION: '#f2dfd8', Estado.ENFRIAMIENTO: '#d5eaf0'}
        self.indicador.config(bg=pal[state])

    def _armar(self):
        if not self.salidas.get():
            self._apagar()

    def conectar(self):
        self.detener()
        self._cerrar()
        try:
            self.model, self.control = self._configurar()
        except Exception as error:
            messagebox.showerror('Parámetros inválidos', str(error))
            return
        if self.modo.get() == 'USB':
            if serial is None:
                messagebox.showerror('PySerial', 'Instale los paquetes de requirements.txt')
                return
            try:
                self.ser = serial.Serial(self.puerto.get().strip(), 115200, timeout=.35, write_timeout=.5)
                time.sleep(1.4)  # placas ESP32 suelen reiniciar al abrir el puerto
                self.ser.reset_input_buffer()
                self.ser.write(b'N\n')
            except Exception as err:
                self._cerrar()
                messagebox.showerror('Comunicación USB', str(err))
                return
        self.conectado = True
        self.t0 = time.monotonic()
        self.aviso.set(f'Conectado: {self.modo.get()}. Pulse Adquirir. Salidas físicas apagadas.')

    def adquirir(self):
        if not self.conectado:
            messagebox.showwarning('Conexión', 'Primero pulse Conectar')
            return
        try:
            self.model, config = self._configurar()
        except Exception as err:
            messagebox.showerror('Parámetros inválidos', str(err))
            return
        config.estado = self.control.estado
        self.control = config
        self.adquiriendo = True
        self.aviso.set('Adquiriendo una muestra por segundo. Datos USB o simulación claramente diferenciados.')

    def _muestra_usb(self):
        if not self._write('R'):
            return None
        for _ in range(5):
            raw = self.ser.readline().decode('ascii', errors='replace').strip()
            if not raw.startswith('DATA,'):
                continue
            parts = raw.split(',')
            if len(parts) != 3:
                continue
            try:
                code, mv = int(parts[1]), int(parts[2])
            except ValueError:
                continue
            if 0 <= code <= 4095 and 0 <= mv <= 3300:
                return code, mv / 1000.0
        return None

    def _muestra_simulada(self):
        t = time.monotonic() - self.t0
        # Recorre los dos límites para verificar los estados en modo simulación.
        temp = 40 + 17 * math.sin(2 * math.pi * t / 95)
        row = self.model.salida(temp)
        voltage = row['vo'] + .0014 * math.sin(t * 3.7)
        return row['adc_ideal'], voltage

    def _paso(self):
        if self.adquiriendo and self.conectado:
            try:
                sample = self._muestra_usb() if self.modo.get() == 'USB' else self._muestra_simulada()
                if sample is None:
                    self.errores += 1
                    self._apagar()
                    self.aviso.set(f'Sin trama válida (intentos fallidos: {self.errores}). Salidas OFF.')
                    if self.errores >= 3:
                        self.detener()
                else:
                    self.errores = 0
                    raw, vo = sample
                    temp = self.model.temperatura(vo)
                    if not math.isfinite(temp) or temp < -45 or temp > 150:
                        self._apagar()
                        self.aviso.set('Temperatura fuera de rango plausible. Salidas OFF; revise el circuito.')
                    else:
                        state = self.control.calcular(temp)
                        if self.modo.get() == 'USB':
                            self._write(('C' if state == Estado.CALEFACCION else 'F' if state == Estado.ENFRIAMIENTO else 'N')
                                        if self.salidas.get() else 'N')
                        self._indicador(state)
                        timestamp = time.monotonic() - self.t0
                        vals = self.model.salida(temp)
                        self.muestras.append((datetime.now().isoformat(timespec='seconds'), round(timestamp, 3),
                                              self.modo.get(), raw, round(vo, 6), round(vals['diferencial'], 6),
                                              round(vals['vs'], 6), round(temp, 5), state.value,
                                              'SI' if self.salidas.get() else 'NO'))
                        self.x.append(timestamp)
                        self.y.append(temp)
                        self.lectura.set(f'{temp:.2f} °C')
                        self.detalles.set(f'Vs {vals["vs"]:.4f} V   |   Vs − Vref {vals["diferencial"]:.4f} V   |   Vo {vo:.4f} V   |   ADC {raw}')
                        self.lista.insert('', 0, values=(f'{timestamp:.1f}', raw, f'{vo:.3f}', f'{temp:.2f}', state.value))
                        if len(self.lista.get_children()) > 160:
                            self.lista.delete(self.lista.get_children()[-1])
                        self.line.set_data(list(self.x), list(self.y))
                        self.line_inf.set_ydata([self.control.inferior] * 2)
                        self.line_sup.set_ydata([self.control.superior] * 2)
                        self.ax.relim()
                        self.ax.autoscale_view()
                        self.canvas.draw_idle()
            except Exception as err:
                self._apagar()
                self.detener()
                self.aviso.set('Fallo en adquisición: ' + str(err))
        self.after(1000, self._paso)

    def procesar(self):
        if not self.muestras:
            messagebox.showinfo('Procesar', 'No hay muestras. Conecte e inicie la adquisición.')
            return
        values = np.array([r[7] for r in self.muestras], dtype=float)
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        self.estadisticas.set(f'N = {len(values)}  |  Media {np.mean(values):.3f} °C  |  s {std:.3f} °C  |  Mín {values.min():.2f}  |  Máx {values.max():.2f}')

    def guardar(self):
        if not self.muestras:
            messagebox.showinfo('Guardar', 'No hay datos que guardar.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')],
                                            initialfile='Proyecto1_TMP36_mediciones.csv')
        if not path:
            return
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['fecha_hora', 'tiempo_s', 'modo', 'adc_raw', 'vo_v', 'vs_menos_ref_v',
                        'vs_tmp36_v', 'temperatura_c', 'estado_logico', 'salidas_habilitadas'])
            w.writerows(self.muestras)
        self.aviso.set(f'Se exportaron {len(self.muestras)} muestras a {path}')

    def detener(self):
        self.adquiriendo = False
        self._apagar()
        self.aviso.set('Adquisición detenida. Salidas OFF.')

    def _cerrar(self):
        if self.ser:
            try:
                self.ser.write(b'N\n')
            except Exception:
                pass
            try:
                self.ser.close()
            except Exception:
                pass
        self.ser = None
        self.conectado = False

    def salir(self):
        self.detener()
        self._cerrar()
        self.destroy()

if __name__ == '__main__':
    App().mainloop()
