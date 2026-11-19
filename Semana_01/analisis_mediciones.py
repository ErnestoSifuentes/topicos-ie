"""Análisis didáctico de medidas CSV exportadas por INTERFAZ-IA (Semana 1).
No requiere paquetes externos. Uso: python analisis_mediciones.py medidas.csv
Los cálculos de k*s describen dispersión de lecturas, no reemplazan un presupuesto GUM.
"""
import csv
import math
import statistics
import sys
from pathlib import Path


def leer_mediciones(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        filas = csv.DictReader(archivo, delimiter=";")
        if not {'Lectura', 'Valor', 'Unidad'}.issubset(filas.fieldnames or []):
            raise ValueError("El CSV necesita las columnas Lectura;Valor;Unidad")
        valores = []
        unidad = None
        for fila in filas:
            lectura = fila['Valor'].strip()
            if not lectura:
                continue
            valor = float(lectura.replace(',', '.'))
            if not math.isfinite(valor):
                raise ValueError("El CSV contiene una lectura no finita")
            valores.append(valor)
            unidad = fila['Unidad'].strip()
        return valores, unidad or '(sin unidad)'


def analizar(valores, unidad='unidad', k=2):
    if len(valores) < 2:
        raise ValueError('Se requieren al menos dos mediciones')
    media = statistics.mean(valores)
    s = statistics.stdev(valores)
    return {
        'n': len(valores), 'media': media, 's_muestral': s,
        'banda_dispersión_k_s': k * s,
        'error_estandar_de_media': s / math.sqrt(len(valores)),
        'unidad': unidad, 'k': k
    }


def main():
    if len(sys.argv) != 2:
        print('Uso: python analisis_mediciones.py archivo.csv')
        return 2
    valores, unidad = leer_mediciones(Path(sys.argv[1]))
    r = analizar(valores, unidad)
    print(f"Lecturas válidas: {r['n']}")
    print(f"Media: {r['media']:.6f} {unidad}")
    print(f"Desviación típica muestral: {r['s_muestral']:.6f} {unidad}")
    print(f"Banda didáctica ±k*s (k=2): ±{r['banda_dispersión_k_s']:.6f} {unidad}")
    print(f"Error estándar s/√n: {r['error_estandar_de_media']:.6f} {unidad}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
