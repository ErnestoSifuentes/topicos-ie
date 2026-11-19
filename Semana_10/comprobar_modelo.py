"""Pruebas matemáticas y lógicas sin hardware físico. Ejecutar: python comprobar_modelo.py"""
from tmp36_modelo import CadenaTMP36, Control, Estado

m = CadenaTMP36(); m.validar()
for t in [20, 35, 45, 80, 120]:
    row = m.salida(t)
    assert abs(m.temperatura(row['vo']) - t) < 1e-9, t
    assert 0 <= row['adc_ideal'] <= 4095
    print(f'T={t:5.1f}°C | Vs={row["vs"]:.3f} V | V*={row["diferencial"]:.3f} V | Vo={row["vo"]:.3f} V | D≈{row["adc_ideal"]}')
assert round(m.salida(20)['vo'], 3) == 0.498
assert round(m.salida(120)['vo'], 3) == 2.988
c = Control(35, 45, 1)
assert c.calcular(30) == Estado.CALEFACCION
assert c.calcular(35.4) == Estado.CALEFACCION
assert c.calcular(36) == Estado.APAGADO
assert c.calcular(50) == Estado.ENFRIAMIENTO
assert c.calcular(44.5) == Estado.ENFRIAMIENTO
assert c.calcular(44) == Estado.APAGADO
assert c.apagar() == Estado.APAGADO
print('Pruebas numéricas y de lógica: satisfactorias. No representan validación del ESP32 real.')
