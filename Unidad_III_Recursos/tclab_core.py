"""INTERFAZ-IA Unidad III. Modelo docente y PID discreto, independiente del hardware."""
from collections import deque
from dataclasses import dataclass
import math


def clip(x, lo, hi):
    return max(lo, min(hi, float(x)))

@dataclass
class FOPDT:
    ambient: float = 23.0
    kp: float = 0.55  # °C por punto porcentual de calentador
    tau: float = 125.0 # s
    dead: float = 6.0  # s
    ts: float = 1.0    # s
    temperature: float = 23.0
    def __post_init__(self):
        self.delay_steps = max(0, int(round(self.dead/self.ts)))
        self.history = deque([0.0]*self.delay_steps)
    def step(self, u, q2=0.0):
        u = clip(u,0,100)
        if self.delay_steps:
            self.history.append(u)
            delayed = self.history.popleft()
        else:
            delayed = u
        # Integración exacta del primer orden con retardo discreto aproximado.
        alpha = math.exp(-self.ts/self.tau)
        target = self.ambient + self.kp*delayed + 0.10*clip(q2,0,100)
        self.temperature = alpha*self.temperature+(1-alpha)*target
        return self.temperature

@dataclass
class PID:
    kc: float = 2.0       # % / °C
    ti: float = 120.0     # s (infinito equivale a P)
    td: float = 0.0       # s
    ts: float = 1.0       # s
    bias: float = 0.0     # %
    filter_time: float = 8.0 # filtro de derivada sobre medida, s
    integral: float = 0.0
    prev_y: float | None = None
    d_filtered: float = 0.0
    def reset(self, bias=0):
        self.bias = float(bias);self.integral=0.0;self.prev_y=None;self.d_filtered=0.0
    def update(self, setpoint, y, mode='PI'):
        e=float(setpoint)-float(y)
        p=self.kc*e if mode in ('P','PI','PID') else 0.0
        if self.prev_y is None: dydt=0.0
        else: dydt=(y-self.prev_y)/max(self.ts,1e-6)
        beta=self.ts/(max(0,self.filter_time)+self.ts)
        self.d_filtered+=(dydt-self.d_filtered)*beta
        d=-self.kc*self.td*self.d_filtered if mode=='PID' else 0.0
        ki=self.kc/max(self.ti,1e-6) if mode in ('PI','PID') and math.isfinite(self.ti) and self.ti>0 else 0.0
        candidate=self.integral+ki*self.ts*e
        raw=self.bias+p+candidate+d
        # Integración condicional: bloquear la acción integral que agrava saturación.
        if not ((raw>100 and e>0) or (raw<0 and e<0)):
            self.integral=candidate
        else: raw=self.bias+p+self.integral+d
        self.prev_y=y
        output=clip(self.bias+p+self.integral+d,0,100)
        return output,{'e':e,'P':p,'I':self.integral,'D':d,'raw':raw,'saturated':not(0<=raw<=100)}

def imc_pi(kp,tau,dead,lam=None):
    if kp<=0 or tau<=0 or dead<0:raise ValueError('Parámetros físicos inválidos')
    if lam is None: lam=max(tau,3*dead,1.0)
    if lam<=0:raise ValueError('lambda debe ser positivo')
    return tau/(kp*(lam+dead)),tau

def simulate(mode='PI',n=600,ts=1,kc=2,ti=120,td=0,sp=40,step_time=30,q2_time=None):
    plant=FOPDT(ts=ts);ctl=PID(kc=kc,ti=ti,td=td,ts=ts)
    records=[];u=0.0
    for i in range(int(n/ts)+1):
        t=i*ts;target=plant.ambient if t<step_time else sp
        q2=40.0 if q2_time is not None and t>=q2_time else 0.0
        if mode=='ONOFF': u=100.0 if plant.temperature<target-0.5 else 0.0 if plant.temperature>target+0.5 else u
        elif mode in ('P','PI','PID'): u,_=ctl.update(target,plant.temperature,mode)
        else:u=35.0 if t>=step_time else 0
        y=plant.temperature
        records.append({'tiempo_s':t,'referencia_C':target,'T1_C':y,'Q1_pct':u,'Q2_pct':q2,'fuente':'MODELO_FOPDT'})
        plant.step(u,q2)
    return records

def performance(rows):
    if len(rows)<2:return {'IAE':0.,'ISE':0.,'ITAE':0.,'energia_pct_s':0.}
    sums={'IAE':0.,'ISE':0.,'ITAE':0.,'energia_pct_s':0.}
    for a,b in zip(rows,rows[1:]):
        dt=max(0.,float(b['tiempo_s'])-float(a['tiempo_s']))
        e=float(a['referencia_C'])-float(a['T1_C'])
        sums['IAE']+=abs(e)*dt;sums['ISE']+=e*e*dt;sums['ITAE']+=a['tiempo_s']*abs(e)*dt
        sums['energia_pct_s']+=max(0,a['Q1_pct'])*dt
    return sums
