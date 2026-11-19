"""Semana 14. Identificación de Kp, tau, theta: ajustar CSV (semana 13)."""
import argparse,csv,math
import numpy as np
from scipy.optimize import least_squares

def fopdt(t,kp,tau,theta,T0,u0,time_step=30):
    elapsed=np.maximum(0,np.array(t,dtype=float)-time_step-theta)
    return T0+kp*u0*(1-np.exp(-elapsed/tau))

def fit(path,power=40,step_time=30):
    with open(path,encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    t=np.array([float(r['tiempo_s']) for r in rows]);y=np.array([float(r['T1_C']) for r in rows]);T0=float(np.median(y[t<step_time]))
    if len(t)<8 or np.ptp(y)<0.4:raise ValueError('Se requieren al menos 8 puntos y respuesta térmica observable')
    def residual(v):return fopdt(t,*v,T0,power,step_time)-y
    p=least_squares(residual,[0.5,120,5],bounds=([0.001,2.,0.],[5.,2000.,180.]),loss='soft_l1')
    k,tau,theta=p.x;rmse=float(np.sqrt(np.mean(residual(p.x)**2)))
    print(f'Kp={k:.4f} °C/%; tau={tau:.2f} s; theta={theta:.2f} s; RMSE={rmse:.3f} °C')
    try:
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,4.5));ax.plot(t,y,'.',label='Datos');ax.plot(t,fopdt(t,k,tau,theta,T0,power,step_time),label='FOPDT ajustado')
        ax.set(xlabel='Tiempo (s)',ylabel='Temperatura T1 (°C)',title='Identificación FOPDT');ax.grid(True);ax.legend();fig.tight_layout();fig.savefig('semana14_ajuste_fopdt.png',dpi=180);plt.close(fig)
    except ImportError:pass
    return k,tau,theta,rmse
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('csv',help='CSV de Semana13');ap.add_argument('--potencia',type=float,default=40);ap.add_argument('--escalon',type=float,default=30);a=ap.parse_args();fit(a.csv,a.potencia,a.escalon)
