"""Semana 15. Comparación ONOFF/P/PI/PID. Resultados simulados claramente marcados."""
import csv
from pathlib import Path
from tclab_core import simulate,performance,imc_pi
Kc,Ti=imc_pi(.55,125,6,lam=125)
print('Sintonía IMC PI, a partir de modelo DEMOSTRATIVO: Kc=',round(Kc,3),'%/°C; Ti=',Ti,'s')
results={}
for m in ['ONOFF','P','PI','PID']:
    records=simulate(m,600,2,kc=Kc,ti=Ti,td=8,sp=40,step_time=20,q2_time=390)
    results[m]=records
    out=Path(__file__).with_name('Semana15_'+m+'_SIMULADO.csv')
    with out.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    print(m,performance(records))
try:
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5))
    for m,rows in results.items():ax.plot([r['tiempo_s'] for r in rows],[r['T1_C'] for r in rows],label=m)
    ax.plot([r['tiempo_s'] for r in rows],[r['referencia_C'] for r in rows],':',label='Setpoint')
    ax.grid(True);ax.legend();ax.set(xlabel='Tiempo (s)',ylabel='T1 (°C)',title='Comparación de reguladores (solo simulación)');fig.tight_layout();fig.savefig(Path(__file__).with_name('semana15_comparacion.png'),dpi=180);plt.close(fig)
except ImportError:pass
