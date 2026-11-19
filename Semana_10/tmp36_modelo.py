"""Modelo nominal del Proyecto 1. Los parámetros de medición deben sustituirse por los observados."""
from dataclasses import dataclass
from enum import Enum


@dataclass
class CadenaTMP36:
    sensibilidad: float = 0.010      # V/°C, TMP36 nominal
    offset_sensor: float = 0.500    # V a 0 °C
    referencia_resta: float = 0.500 # V medida en el restador
    ganancia: float = 2.49          # 24.9 kΩ / 10 kΩ
    margen_adc: float = 3.30       # límite de diseño, no referencia calibrada garantizada

    def validar(self):
        if not (0.005 < self.sensibilidad < 0.020):
            raise ValueError('Sensibilidad fuera del rango previsto para TMP36')
        if not (0.3 <= self.offset_sensor <= 0.7 and 0.3 <= self.referencia_resta <= 0.7):
            raise ValueError('Revise los offsets (voltios)')
        if not (0.1 <= self.ganancia <= 6.0):
            raise ValueError('Ganancia incompatible con el diseño')
        for t in (20, 120):
            vo = self.salida(t)['vo']
            if not 0.05 < vo < self.margen_adc - 0.05:
                raise ValueError(f'Vo({t} °C)={vo:.3f} V no tiene margen suficiente para el ADC')

    def salida(self, temperatura):
        vs = self.offset_sensor + self.sensibilidad * temperatura
        diferencial = vs - self.referencia_resta
        vo = self.ganancia * diferencial
        adc_ideal = round(max(0, min(4095, vo / self.margen_adc * 4095)))
        return {'T': temperatura, 'vs': vs, 'diferencial': diferencial,
                'vo': vo, 'adc_ideal': adc_ideal}

    def temperatura(self, vo):
        vs = float(vo) / self.ganancia + self.referencia_resta
        return (vs - self.offset_sensor) / self.sensibilidad


class Estado(Enum):
    APAGADO = 'APAGADO'
    CALEFACCION = 'CALEFACCIÓN'
    ENFRIAMIENTO = 'ENFRIAMIENTO'


class Control:
    def __init__(self, inferior=35.0, superior=45.0, histeresis=1.0):
        self.inferior, self.superior, self.histeresis = inferior, superior, histeresis
        self.estado = Estado.APAGADO
        self.validar()

    def validar(self):
        if not (20 <= self.inferior < self.superior <= 120):
            raise ValueError('Los límites deben cumplir 20 <= inferior < superior <= 120 °C')
        if not (0 <= self.histeresis < (self.superior - self.inferior) / 2):
            raise ValueError('La histéresis debe ser menor que la mitad de la separación entre límites')

    def calcular(self, t):
        if self.estado == Estado.CALEFACCION and t < self.inferior + self.histeresis:
            return self.estado
        if self.estado == Estado.ENFRIAMIENTO and t > self.superior - self.histeresis:
            return self.estado
        self.estado = Estado.APAGADO
        if t < self.inferior:
            self.estado = Estado.CALEFACCION
        elif t > self.superior:
            self.estado = Estado.ENFRIAMIENTO
        return self.estado

    def apagar(self):
        self.estado = Estado.APAGADO
        return self.estado
