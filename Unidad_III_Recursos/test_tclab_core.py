from tclab_core import FOPDT,PID,imc_pi,simulate,performance
p=FOPDT(ts=1);first=p.temperature
for i in range(400):temp=p.step(50)
assert temp>first+10
assert 0<p.temperature<90
ctrl=PID(kc=3,ti=80,ts=2)
for i in range(300):
 u,d=ctrl.update(100,20,'PI');assert 0<=u<=100
assert ctrl.integral<1e5
kc,ti=imc_pi(.55,125,6,125);assert kc>0 and ti==125
r=simulate('PI',600,2);assert len(r)==301 and performance(r)['IAE']>0
print('Pruebas matemáticas correctas')
