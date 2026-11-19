"""Semana 13. Escalón de calentador 1, CSV y gráfica. Modo simulado por defecto."""
import argparse,csv,time
from pathlib import Path
from tclab_core import FOPDT

def run(modo='simulado',duracion=420,dt=2,potencia=40):
    if modo=='real':
        import tclab
        lab=tclab.TCLab()
    else:
        lab=None;plant=FOPDT(ts=dt)
    data=[]
    try:
        for i in range(int(duracion/dt)+1):
            t=i*dt;u=potencia if t>=30 else 0
            if lab is not None:
                lab.Q1(u);y=float(lab.T1);y2=float(lab.T2)
            else:
                y=plant.temperature;y2=plant.ambient;plant.step(u)
            data.append({'tiempo_s':t,'T1_C':round(y,3),'T2_C':round(y2,3),'Q1_pct':u,'fuente':modo.upper()})
            if lab is not None and i<int(duracion/dt):time.sleep(dt)
    finally:
        if lab is not None:
            lab.Q1(0);lab.Q2(0);lab.close()
    dest=Path(__file__).with_name('semana13_respuesta_escalon.csv')
    with dest.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    try:
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,4.5));ax.plot([d['tiempo_s'] for d in data],[d['T1_C'] for d in data],label='T1 (°C)')
        ax.set(xlabel='Tiempo (s)',ylabel='Temperatura T1 (°C)',title='Respuesta al escalón: '+modo)
        ax2=ax.twinx();ax2.plot([d['tiempo_s'] for d in data],[d['Q1_pct'] for d in data],':',label='Q1 (%)',alpha=.55)
        ax2.set_ylabel('Potencia Q1 (%)');ax.grid(True);fig.tight_layout();fig.savefig(dest.with_suffix('.png'),dpi=180);plt.close(fig)
    except ImportError:pass
    print('Guardado:',dest,'lecturas:',len(data))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--modo',choices=['simulado','real'],default='simulado');ap.add_argument('--duracion',type=int,default=420);ap.add_argument('--dt',type=float,default=2);ap.add_argument('--potencia',type=float,default=40);p=ap.parse_args();run(p.modo,p.duracion,p.dt,p.potencia)
