#!/usr/bin/env python3
# INTERFAZ-IA | Practicas 2 y 3 | Pt2000 / ESP32 / PySerial
# Ejecutar: python termometro_pt2000.py  (ver requirements.txt)
# Admite SIMULACION o puerto USB serie. Ninguna simulacion equivale a validacion fisica.
import csv
import math
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import deque

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

A = 3.9083e-3
B = -5.775e-7
R0 = 2000.0


def rtd_resistance(temp_c):
    return R0 * (1 + A * temp_c + B * temp_c * temp_c)


def temperature_from_r(r):
    if r <= 0 or not math.isfinite(r):
        raise ValueError('Resistencia imposible')
    disc = A * A - 4 * B * (1 - r / R0)
    if disc < 0:
        raise ValueError('Fuera del rango de inversion')
    t = (-A + math.sqrt(disc)) / (2 * B)
    if not (-200 < t < 850):
        raise ValueError('Temperatura fuera de margen')
    return t


def voltage_from_temperature(temp_c, kind, cfg):
    r = rtd_resistance(temp_c)
    v_s = cfg['vcc'] * r / (cfg['rseries'] + r)
    if kind == 'DIVISOR':
        v_base = cfg['vcc'] * cfg['rbal'] / (cfg['rref_top'] + cfg['rbal'])
    else:
        v_base = cfg['vcc'] * cfg['rbal'] / (cfg['rref_top'] + cfg['rbal'])
    return cfg['vbias'] + cfg['gain'] * (v_s - v_base)


def resistance_from_voltage(vout, kind, cfg):
    v_base = cfg['vcc'] * cfg['rbal'] / (cfg['rref_top'] + cfg['rbal'])
    v_sensor = v_base + (vout - cfg['vbias']) / cfg['gain']
    if not 0 < v_sensor < cfg['vcc']:
        raise ValueError('Salida fuera de rango / parametros incorrectos')
    return cfg['rseries'] * v_sensor / (cfg['vcc'] - v_sensor)

class Thermometer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('INTERFAZ-IA · Termómetro Pt2000 · Prácticas 2 y 3')
        self.geometry('1180x770')
        self.minsize(940, 650)
        self.port = None
        self.serial_buffer = b''
        self.running = False
        self.connected = False
        self.rows = []
        self.t0 = time.monotonic()
        self.last_sim = 0
        self.plot_t = deque(maxlen=450)
        self.plot_temp = deque(maxlen=450)
        self.values = {}
        self.kind = tk.StringVar(value='PUENTE')
        self.mode = tk.StringVar(value='SIMULACION')
        self.portName = tk.StringVar(value='COM3')
        self.info = tk.StringVar(value='Detenido · Seleccione simulación o puerto USB')
        self.measure = tk.StringVar(value='— °C')
        self.statistics = tk.StringVar(value='N=0 | Media=— | s=— | Pulse Procesar')
        self.signals = tk.StringVar(value='ADC: —   |   Vo: — V   |   Vs: — V   |   R: — Ω')
        self._layout()
        self.kind.trace_add('write', self._on_kind_change)
        self.job = self.after(30, self._tick)

    def _layout(self):
        bar = ttk.Frame(self, padding=12); bar.pack(fill='x')
        ttk.Label(bar, text='Termómetro Pt2000', font=('Segoe UI', 19, 'bold')).pack(side='left', padx=5)
        ttk.Label(bar, text='Prácticas 2 y 3 · ESP32 / Python').pack(side='left', padx=14)
        top = ttk.LabelFrame(self, text='Conexión y configuración', padding=10)
        top.pack(fill='x', padx=16, pady=4)
        items = [('Modo', self.mode, ['SIMULACION','USB']), ('Circuito',self.kind,['DIVISOR','PUENTE'])]
        for text,var,opts in items:
            ttk.Label(top,text=text).pack(side='left',padx=(5,3))
            ttk.Combobox(top,textvariable=var,values=opts,width=13,state='readonly').pack(side='left',padx=4)
        ttk.Label(top,text='Puerto:').pack(side='left',padx=(15,4))
        ttk.Entry(top,textvariable=self.portName,width=12).pack(side='left')
        ttk.Button(top,text='Buscar puertos',command=self.find_ports).pack(side='left',padx=5)
        controls = ttk.LabelFrame(self,text='Operación del instrumento',padding=9)
        controls.pack(fill='x',padx=16,pady=5)
        style=ttk.Style(self)
        if 'clam' in style.theme_names(): style.theme_use('clam')
        style.configure('Accion.TButton',font=('Segoe UI',10,'bold'),padding=(17,10))
        style.configure('Salir.TButton',font=('Segoe UI',10,'bold'),padding=(17,10))
        for label,callback in [('Conectar',self.connect),('Adquirir',self.acquire),('Procesar',self.process),('Guardar',self.export),('Salir',self.destroy)]:
            ttk.Button(controls,text=label,command=callback,style='Salir.TButton' if label=='Salir' else 'Accion.TButton').pack(side='left',padx=5)
        ttk.Button(controls,text='Detener adquisición',command=self.stop_acquisition).pack(side='right',padx=5)
        conf = ttk.LabelFrame(self,text='Parámetros del circuito (ajustar a valores medidos)',padding=9)
        conf.pack(fill='x',padx=16,pady=4)
        defaults={'vcc':3.300,'rseries':15000,'rbal':2155.87,'rref_top':15000,'gain':15,'vbias':0.200}
        for i,(k,label) in enumerate([('vcc','VCC (V)'),('rseries','R superior sensor (Ω)'),('rbal','R referencia inferior (Ω)'),('rref_top','R referencia superior (Ω)'),('gain','Ganancia G'),('vbias','V sesgo (V)')]):
            cell=ttk.Frame(conf);cell.grid(row=0,column=i,padx=5,sticky='ew')
            ttk.Label(cell,text=label).pack(anchor='w')
            v=tk.StringVar(value=str(defaults[k]));self.values[k]=v
            ttk.Entry(cell,textvariable=v,width=15).pack()
        center=ttk.Frame(self,padding=(16,10));center.pack(fill='both',expand=True)
        left=ttk.Frame(center);left.pack(side='left',fill='both',expand=True)
        ttk.Label(left,textvariable=self.measure,font=('Segoe UI',25,'bold')).pack(anchor='w',pady=7)
        ttk.Label(left,textvariable=self.statistics,font=('Segoe UI',11)).pack(anchor='w')
        ttk.Label(left,textvariable=self.signals,font=('Segoe UI',10)).pack(anchor='w',pady=(7,0))
        ttk.Label(left,textvariable=self.info,wraplength=520,foreground='#386b71').pack(anchor='w',pady=(8,12))
        self.fig=Figure(figsize=(7,4),dpi=100)
        self.ax=self.fig.add_subplot(111)
        self.ax.set(xlabel='Tiempo (s)',ylabel='Temperatura (°C)',title='Temperatura adquirida')
        self.ax.grid(True,alpha=.25)
        (self.trace,)=self.ax.plot([],[],lw=1.7)
        self.canvas=FigureCanvasTkAgg(self.fig,master=left)
        self.canvas.get_tk_widget().pack(fill='both',expand=True)
        right=ttk.LabelFrame(center,text='Últimas muestras',padding=8)
        right.pack(side='right',fill='y',padx=(14,0))
        self.table=ttk.Treeview(right,columns=['ms','adc','mv','r','t'],show='headings',height=19)
        for col,label,w in [('ms','t (ms)',80),('adc','ADC',65),('mv','mV',65),('r','Ω',85),('t','°C',80)]:
            self.table.heading(col,text=label);self.table.column(col,width=w,anchor='center')
        self.table.pack(fill='y',expand=True)
        ttk.Label(self,text='Los resultados simulados se identifican como SIMULACION. Verifique el ADC y el acondicionamiento con multímetro antes del montaje experimental.',padding=(18,10)).pack(anchor='w')

    def _on_kind_change(self, *_):
        # Los parámetros del amplificador son distintos para cada montaje.
        # El estudiante debe reemplazarlos por los valores realmente medidos.
        if self.running or self.connected:
            self.stop()
        self.values['gain'].set('22' if self.kind.get() == 'DIVISOR' else '19')
        self.info.set('Circuito ' + self.kind.get() + ': revise las resistencias y Vbias antes de iniciar')

    def params(self):
        cfg={k:float(v.get()) for k,v in self.values.items()}
        if any(cfg[x]<=0 for x in ['vcc','rseries','rbal','rref_top','gain']) or cfg['vbias']<0 or cfg['vbias']>=cfg['vcc'] or cfg['gain']>=1000:
            raise ValueError('Valores de diseño fuera de rango')
        return cfg

    def find_ports(self):
        if serial is None:
            messagebox.showerror('PySerial','Instale pyserial: pip install pyserial')
            return
        ports=[p.device for p in serial.tools.list_ports.comports()]
        messagebox.showinfo('Puertos','\n'.join(ports) if ports else 'No se detectaron puertos')
        if ports:self.portName.set(ports[0])

    def connect(self):
        """Abrir y verificar el puerto; la adquisición comienza con Adquirir."""
        self.stop()
        try: self.params()
        except Exception as exc:
            messagebox.showerror('Parámetros',str(exc));return
        if self.mode.get() == 'USB':
            if serial is None:
                messagebox.showerror('PySerial','Falta pyserial. Instale las dependencias del curso.');return
            try:
                self.port = serial.Serial(self.portName.get().strip(),115200,timeout=0)
                self.port.reset_input_buffer()
            except Exception as exc:
                self.port=None
                messagebox.showerror('Puerto serial',str(exc));return
        self.connected=True
        self.info.set('Conectado · '+self.mode.get()+' · '+self.kind.get()+' · Pulse Adquirir')

    def acquire(self):
        if not self.connected:
            messagebox.showinfo('Conexión','Primero pulse Conectar.');return
        if self.running:
            self.info.set('La adquisición ya está en curso.');return
        try: self.params()
        except Exception as exc:
            messagebox.showerror('Parámetros',str(exc));return
        self.rows.clear();self.plot_t.clear();self.plot_temp.clear();self.serial_buffer=b''
        for x in self.table.get_children():self.table.delete(x)
        self.running=True;self.t0=time.monotonic();self.last_sim=0
        self.statistics.set('N=0 | Pulse Procesar después de adquirir')
        self.measure.set('— °C')
        self.info.set('Adquiriendo · '+self.mode.get()+' · '+self.kind.get())

    def stop_acquisition(self):
        self.running=False
        self.info.set('Adquisición detenida · '+str(len(self.rows))+' muestras. Pulse Procesar o Guardar')

    def stop(self):
        self.running=False
        self.connected=False
        if self.port is not None:
            try:self.port.close()
            except Exception:pass
            self.port=None
        self.info.set('Desconectado')

    def process(self):
        if not self.rows:
            messagebox.showinfo('Procesar','Primero adquiera algunas muestras.');return
        vals=np.array([r[4] for r in self.rows],dtype=float)
        self.statistics.set(f'N={len(vals)} | Media={np.mean(vals):.3f} °C | s={np.std(vals,ddof=1) if len(vals)>1 else 0:.3f} °C | Mín={min(vals):.2f} °C | Máx={max(vals):.2f} °C')
        self.info.set('Procesamiento completado · resultados calculados a partir de las muestras adquiridas')

    def ingest(self,ms,adc,mv):
        cfg=self.params();vout=mv/1000.0
        try:
            resistance=resistance_from_voltage(vout,self.kind.get(),cfg)
            temperature=temperature_from_r(resistance)
        except (ValueError,ZeroDivisionError):
            self.info.set('Dato fuera del intervalo de medida; revise parámetros o saturación del ADC')
            return
        rec=(int(ms),int(adc),float(mv),round(resistance,4),round(temperature,4),self.mode.get(),self.kind.get())
        self.rows.append(rec)
        self.plot_t.append(ms/1000);self.plot_temp.append(temperature)
        self.table.insert('',0,values=[rec[0],rec[1],round(rec[2]),round(rec[3],1),round(rec[4],2)])
        if len(self.table.get_children())>25:self.table.delete(self.table.get_children()[-1])
        self.measure.set(f'{temperature:.2f} °C')
        vbase=cfg['vcc']*cfg['rbal']/(cfg['rref_top']+cfg['rbal'])
        vs=vbase+(vout-cfg['vbias'])/cfg['gain']
        self.signals.set(f'ADC: {int(adc)}   |   Vo: {vout:.4f} V   |   '+(f'Vs: {vs:.4f} V   |   ' if self.kind.get()=='DIVISOR' else f'Vd: {(vout-cfg["vbias"])/cfg["gain"]:.5f} V   |   ')+f'R: {resistance:.2f} Ω')

    def _tick(self):
        try:
            if self.running:
                now=time.monotonic()
                if self.mode.get()=='SIMULACION':
                    if now-self.last_sim>=0.25:
                        self.last_sim=now
                        ts=now-self.t0
                        cfg=self.params();kind=self.kind.get()
                        t=40+17*math.sin(ts/12)+2*math.sin(ts/2)
                        v=voltage_from_temperature(t,kind,cfg)
                        mv=max(0,min(3100,int(v*1000+np.random.normal(0,1.5))))
                        adc=int(round(mv/3100*4095))
                        self.ingest(int(ts*1000),adc,mv)
                elif self.port is not None:
                    if self.port.in_waiting:
                        self.serial_buffer += self.port.read(self.port.in_waiting)
                        if len(self.serial_buffer) > 100000:
                            self.serial_buffer = self.serial_buffer[-10000:]
                        while b'\n' in self.serial_buffer:
                            line,self.serial_buffer = self.serial_buffer.split(b'\n',1)
                            cells=line.decode('ascii',errors='ignore').strip().split(',')
                            if len(cells)==3:
                                try:self.ingest(int(cells[0]),int(cells[1]),float(cells[2]))
                                except (ValueError,OverflowError):pass
                if self.rows:
                    xs=np.asarray(self.plot_t,dtype=float);ys=np.asarray(self.plot_temp,dtype=float)
                    self.trace.set_data(xs,ys)
                    self.ax.relim();self.ax.autoscale_view();self.canvas.draw_idle()
        except Exception as exc:
            self.stop();self.info.set('Error: '+str(exc))
        finally:
            self.job = self.after(100,self._tick)

    def export(self):
        if not self.rows:
            messagebox.showinfo('CSV','No hay muestras');return
        file=filedialog.asksaveasfilename(title='Guardar mediciones',defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if not file:return
        with open(file,'w',encoding='utf-8-sig',newline='') as f:
            writer=csv.writer(f);writer.writerow(['t_ms','adc_raw','adc_mV','r_ohm','temp_c','origen','circuito'])
            writer.writerows(self.rows)
        self.info.set(f'Archivo CSV guardado: {file}')

    def destroy(self):
        if getattr(self,'job',None) is not None:
            try:self.after_cancel(self.job)
            except Exception:pass
        self.stop()
        super().destroy()

if __name__=='__main__':
    Thermometer().mainloop()
