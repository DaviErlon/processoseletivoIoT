from machine import Pin, ADC
import time

class LDR:
    def __init__(self, pin, GAMMA = 0.7, RL10 = 50.0):
        self._GAMMA = GAMMA
        self._RL10 = RL10

        AO = ADC(Pin(pin))
        
        #configurações esperadas para o ADC do ESP32, mas não impactam a simulação;
        #o WOKWI desconsidera esses detalhes necessários em uma implementação real 
        AO.atten(ADC.ATTN_11DB)
        AO.width(ADC.WIDTH_12BIT)

        self._AO = AO

    def get_raw_value(self):
        return self._AO.read()

    def get_lux(self):
        """metodo de leitura e conversão para lux seguindo o calculo presente em https://docs.wokwi.com/parts/wokwi-photoresistor-sensor"""
        
        raw = self._AO.read()
        vol = raw / 4095.0 * 5 # tensao do pino AO
        res = 2000 * vol / (1 - vol / 5) # calculo da resistencia do LDR

        return pow(self._RL10 * 1e3 * pow(10, self._GAMMA) / res, (1 / self._GAMMA)) # conversao para lux


class BTN:
    def __init__(self, pin, debounce_ms=50):
        self._btn = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._last_state = self._btn.value()

        # atributos para implementar um debounce via software
        self._dbc_ms = debounce_ms
        self._last_time = time.ticks_ms()

    def get_value(self):
        state = self._btn.value()

        #primeiro if verifica se houve mudança de estado no botao
        if state != self._last_state:
            now = time.ticks_ms()
            #segunfo if verifica se essa mudança ocorre respeitando o intervalo debounce
            if time.ticks_diff(now, self._last_time) >= self._dbc_ms:
                self._last_state = state
                self._last_time = now

        return self._last_state