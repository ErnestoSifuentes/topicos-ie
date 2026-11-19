"""INTERFAZ-IA · Proyecto 3: panel TCLab, control digital en PC.

Simulado = modelo docente FOPDT, NO lecturas reales. Para hardware TCLab estándar
requiere `pip install tclab` y su firmware compatible. Mantener supervisión.
"""
import csv
import math
import threading
import time
import queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import deque
from tclab_core import FOPDT, PID, performance
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TCLabApp:
    def __init__(self,root):
        self.root=root;root.title('INTERFAZ-IA | Laboratorio de control térmico TCLab')
        root.geometry('1240x790');root.minsize(950,660)
        self.mode=tk.StringVar(value='Simulación FOPDT')
        self.control=tk.StringVar(value='PI')
        self.sp=tk.DoubleVar(value=40.0)
        self.kc=tk.DoubleVar(value=1.5)
        self.ti=tk.DoubleVar(value=120.0)
        self.td=tk.DoubleVar(value=0.0)
        self.ts=tk.DoubleVar(value=2.0)
        self.max_temp=tk.DoubleVar(value=65.0)
        self.manual=tk.DoubleVar(value=20.0)
        self.q2=tk.DoubleVar(value=0.0)
        self.status=tk.StringVar(value='Desconectado · salidas apagadas')
        self.temp=tk.StringVar(value='—');self.temp2=tk.StringVar(value='—');self.out=tk.StringVar(value='0 %')
        self.dat=[];self.connected=False;self.running=False;self.stop_ev=threading.Event();self.worker=None
        self.messages=queue.Queue();self.lab=None;self.plant=None
        self._ui()
        root.protocol('WM_DELETE_WINDOW',self.exit)
        root.after(80,self._poll)
    def _ui(self):
        self.root.configure(bg='#f4f7f9')
        header=tk.Frame(self.root,bg='#152a3a',height=80);header.pack(fill='x');header.pack_propagate(False)
        tk.Label(header,text='INTERFAZ-IA   |   CONTROL TÉRMICO TCLab',font=('Georgia',19,'bold'),fg='white',bg='#152a3a').pack(side='left',padx=24,pady=20)
        tk.Label(header,text='UNIDAD III · PROYECTO 3',font=('Segoe UI',10,'bold'),fg='#aee4df',bg='#152a3a').pack(side='right',padx=24)
        commands=ttk.Frame(self.root,padding=(12,9));commands.pack(fill='x')
        for text,call in [('Conectar',self.connect),('Adquirir',self.acquire),('Detener',self.stop),('Procesar',self.process),('Guardar',self.save),('Salir',self.exit)]:
            ttk.Button(commands,text=text,command=call).pack(side='left',padx=4)
        ttk.Label(commands,textvariable=self.status,foreground='#116f72',font=('Segoe UI',10,'bold')).pack(side='right',padx=6)
        body=ttk.PanedWindow(self.root,orient='horizontal');body.pack(fill='both',expand=True,padx=12,pady=(0,10))
        left=ttk.Frame(body,padding=8);right=ttk.Frame(body,padding=8);body.add(left,weight=1);body.add(right,weight=3)
        conf=ttk.LabelFrame(left,text='Configuración',padding=10);conf.pack(fill='x')
        self._entry(conf,'Fuente',self.mode,opts=['Simulación FOPDT','TCLab real'])
        self._entry(conf,'Controlador',self.control,opts=['Manual','ONOFF','P','PI','PID'])
        self._entry(conf,'Referencia SP (°C)',self.sp)
        self._entry(conf,'Kc (%/°C)',self.kc)
        self._entry(conf,'Ti (s)',self.ti)
        self._entry(conf,'Td (s)',self.td)
        self._entry(conf,'Ts (s)',self.ts)
        self._entry(conf,'Q1 manual (%)',self.manual)
        self._entry(conf,'Perturbación Q2 (%)',self.q2)
        self._entry(conf,'Paro seguridad T1 (°C)',self.max_temp)
        status=ttk.LabelFrame(left,text='Indicadores',padding=10);status.pack(fill='x',pady=10)
        for title,var in [('T1',self.temp),('T2',self.temp2),('Q1',self.out)]:
            line=ttk.Frame(status);line.pack(fill='x',pady=4)
            ttk.Label(line,text=title,width=8,font=('Segoe UI',11,'bold')).pack(side='left')
            ttk.Label(line,textvariable=var,font=('Segoe UI',16,'bold'),foreground='#116f72').pack(side='left')
        ttk.Label(left,text='Modo simulación: datos de modelo, NO mediciones.\nModo real: control Python por USB, no PID embebido.\nAl detener, Q1 y Q2 se ponen en 0 %.',wraplength=260,foreground='#607080').pack(anchor='w',pady=9)
        fig=Figure(figsize=(8,6),dpi=100);self.ax=fig.add_subplot(211);self.ax2=fig.add_subplot(212);fig.subplots_adjust(left=.10,right=.97,top=.95,bottom=.10,hspace=.35)
        self.figure=fig;self.canvas=FigureCanvasTkAgg(fig,master=right);self.canvas.get_tk_widget().pack(fill='both',expand=True)
        self.stats=ttk.Label(right,text='Procesar para calcular IAE, ISE, ITAE y esfuerzo de control.',foreground='#485d69');self.stats.pack(anchor='w')
        self._draw()
    def _entry(self,frame,name,var,opts=None):
        row=ttk.Frame(frame);row.pack(fill='x',pady=4)
        ttk.Label(row,text=name,width=24).pack(side='left')
        if opts is not None:
            ttk.Combobox(row,textvariable=var,values=opts,state='readonly',width=21).pack(side='right',fill='x',expand=True)
        else:ttk.Entry(row,textvariable=var,width=13).pack(side='right')
    def connect(self):
        if self.connected:return
        try:
            if self.mode.get()=='TCLab real':
                import tclab
                self.lab=tclab.TCLab() # conexión bajo responsabilidad del operador
                self.lab.Q1(0);self.lab.Q2(0)
            else:self.plant=FOPDT(ts=max(0.25,float(self.ts.get())))
            self.dat=[];self.connected=True;self.status.set('Conectado · '+self.mode.get());self._draw()
        except Exception as e:
            self.lab=None;self.plant=None;messagebox.showerror('Conexión',str(e));self.status.set('No conectado')
    def acquire(self):
        if not self.connected:self.connect()
        if not self.connected or self.running:return
        try:
            ts=float(self.ts.get());assert .25<=ts<=60
            sp=float(self.sp.get());kc=float(self.kc.get());ti=float(self.ti.get());td=float(self.td.get());maxT=float(self.max_temp.get())
            if not (0<=sp<=maxT<=85 and 0<=kc<=50 and ti>0 and 0<=td<=400):raise ValueError('Revise límites y parámetros')
        except Exception:
            messagebox.showerror('Parámetros','Ts entre 0.25 y 60 s; 0 ≤ SP ≤ paro ≤ 85 °C; Kc y Td no negativos; Ti positivo.');return
        if self.plant is not None and abs(self.plant.ts-ts)>1e-9:
            self.plant=FOPDT(ts=ts)  # Un cambio de Ts reinicia la simulación y el retardo discreto
        self.stop_ev.clear();self.running=True;self.status.set('Adquiriendo…')
        cfg=dict(mode=self.control.get(),ts=ts,sp=sp,kc=kc,ti=ti,td=td,manual=float(self.manual.get()),q2=float(self.q2.get()),maxT=maxT,source=self.mode.get())
        self.worker=threading.Thread(target=self._loop,args=(cfg,),daemon=True);self.worker.start()
    def _loop(self,cfg):
        c=PID(kc=cfg['kc'],ti=cfg['ti'],td=cfg['td'],ts=cfg['ts'],filter_time=max(4,cfg['ts']*4))
        prev_u=0;start=time.monotonic();i=0
        try:
            while not self.stop_ev.is_set():
                due=start+i*cfg['ts'];remaining=due-time.monotonic()
                if remaining>0 and self.stop_ev.wait(remaining):break
                t=time.monotonic()-start  # tiempo realmente transcurrido, incluye jitter de USB/PC
                if self.lab is not None:
                    y=float(self.lab.T1);y2=float(self.lab.T2)
                else:
                    y=float(self.plant.temperature);y2=float(self.plant.ambient)
                if not math.isfinite(y) or y>=cfg['maxT']:
                    self.messages.put(('alarm',f'Protección: T1 = {y:.2f} °C.'));break
                mode=cfg['mode']
                if mode=='Manual':u=max(0,min(100,cfg['manual']))
                elif mode=='ONOFF':u=100 if y<=cfg['sp']-.5 else 0 if y>=cfg['sp']+.5 else prev_u
                else:u,_=c.update(cfg['sp'],y,mode)
                q2=max(0,min(100,cfg['q2']))
                if self.lab is not None:self.lab.Q1(u);self.lab.Q2(q2)
                else:self.plant.step(u,q2)
                prev_u=u
                self.messages.put(('data',{'tiempo_s':t,'referencia_C':cfg['sp'],'T1_C':y,'T2_C':y2,'Q1_pct':u,'Q2_pct':q2,'fuente':'REAL' if self.lab else 'SIMULADO','controlador':mode}))
                i+=1
        except Exception as e:self.messages.put(('alarm','Error de lectura/control: '+str(e)))
        finally:
            try:
                if self.lab is not None:self.lab.Q1(0);self.lab.Q2(0)
            except Exception:pass
            self.messages.put(('stopped',None))
    def stop(self):
        self.stop_ev.set();self.status.set('Deteniendo y apagando salidas…')
    def _poll(self):
        try:
            changed=False
            for _ in range(300):
                typ,data=self.messages.get_nowait()
                if typ=='data':self.dat.append(data);changed=True
                elif typ=='alarm':self.status.set(data);self.stop_ev.set()
                elif typ=='stopped':self.running=False
            if changed:
                d=self.dat[-1];self.temp.set(f"{d['T1_C']:.2f} °C");self.temp2.set(f"{d['T2_C']:.2f} °C");self.out.set(f"{d['Q1_pct']:.1f} %");self._draw()
        except queue.Empty:pass
        if self.root.winfo_exists():self.root.after(150,self._poll)
    def _draw(self):
        self.ax.clear();self.ax2.clear()
        if self.dat:
            a=self.dat[-800:];t=[r['tiempo_s'] for r in a]
            self.ax.plot(t,[r['T1_C'] for r in a],label='T1 (°C)')
            self.ax.plot(t,[r['referencia_C'] for r in a],'--',label='Referencia (°C)')
            self.ax2.plot(t,[r['Q1_pct'] for r in a],label='Q1 (%)')
            self.ax2.plot(t,[r['Q2_pct'] for r in a],':',label='Q2 (%)')
        self.ax.set(ylabel='Temperatura (°C)',title='Respuesta de temperatura');self.ax2.set(xlabel='Tiempo (s)',ylabel='Potencia de calentador (%)',title='Señales de control');self.ax2.set_ylim(-4,104)
        for a in (self.ax,self.ax2):a.grid(True,alpha=.4)
        if self.dat:self.ax.legend(loc='best',fontsize=8);self.ax2.legend(loc='best',fontsize=8)
        self.canvas.draw_idle()
    def process(self):
        if len(self.dat)<2:messagebox.showinfo('Procesar','Primero registre al menos dos muestras.');return
        m=performance(self.dat)
        self.stats.configure(text='  '.join(f'{k}: {v:.2f}' for k,v in m.items()))
    def save(self):
        if not self.dat:messagebox.showinfo('Guardar','No hay muestras.');return
        fn=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='INTERFAZ_IA_TCLab.csv')
        if not fn:return
        with open(fn,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(self.dat[0]));w.writeheader();w.writerows(self.dat)
        self.status.set('CSV guardado: '+Path(fn).name)
    def exit(self):
        self.stop_ev.set()
        if self.worker and self.worker.is_alive():self.worker.join(timeout=3)
        try:
            if self.lab is not None:self.lab.Q1(0);self.lab.Q2(0);self.lab.close()
        except Exception:pass
        self.root.destroy()

if __name__=='__main__':
    root=tk.Tk();TCLabApp(root);root.mainloop()
