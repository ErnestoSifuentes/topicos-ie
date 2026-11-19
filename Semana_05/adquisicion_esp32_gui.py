#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UACJ · Semana 5. Adquisición USB serial ESP32 y registro de datos.

Protocolo CSV: t_ms,adc,voltage (115200 baudios; 10 Hz).
Simulador de baja tensión incluido para practicar sin ESP32.
Requiere: pip install pyserial matplotlib
"""
from __future__ import annotations
import csv
import math
from collections import deque
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BAUD = 115200
REFRESH_MS = 100
MAX_SAMPLES = 20000
VISIBLE = 300

@dataclass(frozen=True)
class Sample:
    t_ms: int
    adc: int
    voltage: float


def parse_line(raw: str) -> Sample | None:
    """Trama válida o None. Ignora mensajes, columnas mal formadas y NaN."""
    s = raw.strip()
    if not s or s.startswith('#') or s.lower() == 't_ms,adc,voltage':
        return None
    parts = s.split(',')
    if len(parts) != 3:
        return None
    try:
        tm = int(parts[0].strip())
        adc = int(parts[1].strip())
        v = float(parts[2].strip())
    except ValueError:
        return None
    if tm < 0 or not 0 <= adc <= 4095 or not math.isfinite(v) or not -0.1 <= v <= 3.5:
        return None
    return Sample(tm, adc, v)


class ControlLabApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title('Tópicos de Ingeniería Eléctrica II · Adquisición ESP32')
        root.geometry('1070x705')
        root.minsize(800, 550)
        self.mode = 'idle'
        self.port = None
        self.rx = bytearray()
        self.samples: list[Sample] = []
        self.invalid = 0
        self.counter = 0
        self.plot_pending = False
        self.status = tk.StringVar(value='Desconectado')
        self.port_name = tk.StringVar()
        self.sample_lbl = tk.StringVar(value='Muestras: 0')
        self.adc_lbl = tk.StringVar(value='ADC: —')
        self.volt_lbl = tk.StringVar(value='Voltaje estimado: —')
        self.invalid_lbl = tk.StringVar(value='Tramas no válidas: 0')

        top = ttk.Frame(root, padding=(18, 16))
        top.pack(fill='x')
        ttk.Label(top, text='Adquisición de datos con ESP32',font=('Segoe UI',19,'bold')).pack(anchor='w')
        ttk.Label(top,text='Semana 5 · GPIO36 (ADC1) · 115200 baudios · t_ms,adc,voltage').pack(anchor='w')
        bar=ttk.Frame(root,padding=(18,0));bar.pack(fill='x')
        ttk.Label(bar,text='Puerto USB:').pack(side='left')
        self.combo=ttk.Combobox(bar,textvariable=self.port_name,width=23)
        self.combo.pack(side='left',padx=6)
        ttk.Button(bar,text='Actualizar puertos',command=self.refresh_ports).pack(side='left',padx=3)
        ttk.Button(bar,text='Conectar ESP32',command=self.connect).pack(side='left',padx=3)
        ttk.Button(bar,text='Simulación local',command=self.simulate).pack(side='left',padx=3)
        ttk.Button(bar,text='Detener',command=self.stop).pack(side='left',padx=3)

        bar2=ttk.Frame(root,padding=(18,13));bar2.pack(fill='x')
        for textvar in (self.status,self.sample_lbl,self.adc_lbl,self.volt_lbl,self.invalid_lbl):
            ttk.Label(bar2,textvariable=textvar).pack(side='left',padx=(0,19))
        fig=Figure(figsize=(9,4.0),dpi=100)
        self.axes=fig.add_subplot(111)
        self.axes.set(xlabel='Tiempo desde el inicio (s)',ylabel='Voltaje estimado (V)',ylim=(0,3.3))
        self.axes.grid(alpha=.25)
        self.line,=self.axes.plot([],[],linewidth=1.8)
        self.canvas=FigureCanvasTkAgg(fig,master=root)
        self.canvas.get_tk_widget().pack(fill='both',expand=True,padx=18,pady=(0,8))
        buttons=ttk.Frame(root,padding=(18,5,18,14));buttons.pack(fill='x')
        ttk.Button(buttons,text='Guardar CSV',command=self.save_csv).pack(side='left',padx=(0,8))
        ttk.Button(buttons,text='Limpiar registro',command=self.clear).pack(side='left',padx=(0,8))
        ttk.Label(buttons,text='Guardar conserva las marcas de tiempo enviadas por el ESP32.').pack(side='left',padx=(20,0))
        self.refresh_ports()
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.after(REFRESH_MS,self.tick)

    def refresh_ports(self):
        ports=[p.device for p in serial.tools.list_ports.comports()] if serial else []
        self.combo['values']=ports
        if ports and self.port_name.get() not in ports:self.port_name.set(ports[0])

    def stop(self):
        self.mode='idle'
        if self.port is not None:
            try:self.port.close()
            except Exception:pass
            self.port=None
        self.status.set('Detenido')
        self.rx.clear()

    def connect(self):
        name=self.port_name.get().strip()
        if not serial:
            messagebox.showerror('PySerial no disponible','Instale con: pip install pyserial')
            return
        if not name:
            messagebox.showwarning('Puerto no seleccionado','Seleccione el puerto USB del ESP32.')
            return
        self.stop()
        try:
            self.port=serial.Serial(port=name,baudrate=BAUD,timeout=0)
            self.mode='usb'
            self.rx.clear()
            self.status.set('USB · '+name)
        except (OSError,serial.SerialException) as e:
            self.port=None
            messagebox.showerror('No se pudo conectar',str(e))

    def simulate(self):
        self.stop()
        self.mode='sim'
        self.counter=0
        self.status.set('Simulación local (sin hardware)')

    def add_sample(self,record:Sample):
        self.samples.append(record)
        if len(self.samples)>MAX_SAMPLES:
            self.samples=self.samples[-MAX_SAMPLES:]
        self.sample_lbl.set('Muestras: '+str(len(self.samples)))
        self.adc_lbl.set('ADC: '+str(record.adc))
        self.volt_lbl.set(f'Voltaje estimado: {record.voltage:.4f} V')
        self.plot_pending=True

    def ingest(self,chunk:bytes):
        self.rx.extend(chunk)
        if len(self.rx)>65536:
            self.rx.clear()
            self.invalid+=1
        while b'\n' in self.rx:
            raw,_,remaining=self.rx.partition(b'\n')
            self.rx=bytearray(remaining)
            text=raw.decode('utf-8',errors='replace')
            is_meta=not text.strip() or text.lstrip().startswith('#') or text.strip().lower()=='t_ms,adc,voltage'
            s=parse_line(text)
            if s is None:
                if not is_meta:self.invalid+=1
            else:
                self.add_sample(s)
        self.invalid_lbl.set(f'Tramas no válidas: {self.invalid}')

    def tick(self):
        if self.mode=='sim':
            tm=self.counter*REFRESH_MS
            v=1.65+.8*math.sin(2*math.pi*.30*tm/1000)
            adc=max(0,min(4095,round(4095*v/3.3)))
            self.ingest(f'{tm},{adc},{3.3*adc/4095:.4f}\n'.encode())
            self.counter+=1
        elif self.mode=='usb' and self.port is not None:
            try:
                n=min(self.port.in_waiting,8192)
                if n:self.ingest(self.port.read(n))
            except (OSError,serial.SerialException) as e:
                self.stop()
                self.status.set('Error de comunicación')
                messagebox.showerror('Conexión perdida',str(e))
        if self.plot_pending:
            recent=self.samples[-VISIBLE:]
            times=[(s.t_ms-recent[0].t_ms)/1000 for s in recent]
            self.line.set_data(times,[s.voltage for s in recent])
            self.axes.set_xlim(0,max(2,times[-1] if times else 2))
            self.canvas.draw_idle()
            self.plot_pending=False
        self.root.after(REFRESH_MS,self.tick)

    def save_csv(self):
        if not self.samples:
            messagebox.showinfo('Sin datos','Realice primero una adquisición o simulación.');return
        path=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='semana05_mediciones.csv')
        if not path:return
        try:
            with open(path,'w',newline='',encoding='utf-8') as f:
                w=csv.writer(f);w.writerow(['t_ms','adc','voltage'])
                w.writerows((s.t_ms,s.adc,f'{s.voltage:.4f}') for s in self.samples)
        except OSError as e:
            messagebox.showerror('Error al guardar',str(e));return
        self.status.set(f'CSV guardado · {len(self.samples)} muestras')

    def clear(self):
        self.samples.clear();self.invalid=0;self.rx.clear()
        self.sample_lbl.set('Muestras: 0');self.adc_lbl.set('ADC: —');self.volt_lbl.set('Voltaje estimado: —');self.invalid_lbl.set('Tramas no válidas: 0')
        self.line.set_data([],[]);self.axes.set_xlim(0,2);self.canvas.draw_idle()

    def close(self):
        self.stop();self.root.destroy()


def main():
    root=tk.Tk();ControlLabApp(root);root.mainloop()

if __name__=='__main__':
    main()
