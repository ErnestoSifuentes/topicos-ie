"""Tabla comparativa de reglas PI para modelo FOPDT. NO ejecuta hardware."""
from tclab_core import imc_pi

def sintonias(kp,tau,theta,lam=None):
    if kp<=0 or tau<=0 or theta<=0:raise ValueError('Kp,tau,theta deben ser >0 para comparar ZN/CC')
    lam=tau if lam is None else lam
    kc_imc,ti_imc=imc_pi(kp,tau,theta,lam)
    ratio=theta/tau
    kc_zn=.9*tau/(kp*theta);ti_zn=3.33*theta
    kc_cc=(tau/(kp*theta))*(.9+theta/(12*tau))
    ti_cc=theta*(30+3*ratio)/(9+20*ratio)
    return {'IMC/λ':(kc_imc,ti_imc),'Ziegler–Nichols':(kc_zn,ti_zn),'Cohen–Coon':(kc_cc,ti_cc)}

if __name__=='__main__':
    for name,(kc,ti) in sintonias(.55,125,6,lam=125).items():
        print(f'{name:18s}  Kc={kc:9.3f} %/°C   Ti={ti:7.2f} s')
    print('Advertencia: valores demostrativos, validar estabilidad y saturación antes de usar hardware.')
