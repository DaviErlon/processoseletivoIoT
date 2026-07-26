from machine import Pin, ADC
import time

class LDR:
    def __init__(self, pin, GAMMA = 0.7, RL10 = 50.0):
        self._GAMMA = GAMMA # sensibilidade a luz do LDR
        self._RL10 = RL10   # resistencia do LDR a 10 lux

        AO = ADC(Pin(pin))
        
        #configurações esperadas para o ADC do ESP32, mas não impactam a simulação;
        #o WOKWI desconsidera esses detalhes necessários em uma implementação real 
        AO.atten(ADC.ATTN_11DB)
        AO.width(ADC.WIDTH_12BIT)

        self._AO = AO

    def get_raw_value(self):
        return self._AO.read()

    def get_lux(self):
        """metodo de leitura e conversão seguindo o calculo presente na documentação do wokwi"""
        
        raw = self._AO.read()
        vol = raw / 4095.0 * 5              # tensao do pino AO
        res = 2000 * vol / (1 - vol / 5)    # calculo da resistencia do LDR

        return pow(self._RL10 * 1e3 * pow(10, self._GAMMA) / res, (1 / self._GAMMA)) # conversao para lux

class BTN:
    def __init__(self, pin, debounce_ms=50):
        self._button_pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._last_raw_state = self._button_pin.value()     # último valor bruto lido do botão (antes do debounce)
        self._last_debounced_state = self._last_raw_state   # último valor já estabilizado pelo debounce

        # tempo mínimo entre mudanças aceitas
        self._debounce_ms = debounce_ms
        self._timestamp_debounce = time.ticks_ms()

    def get_value(self):
        raw_state = self._button_pin.value()

        # verifica se o valor bruto mudou
        if raw_state != self._last_raw_state:
            now = time.ticks_ms()

            # só aceita a mudança se o intervalo de debounce foi respeitado
            if time.ticks_diff(now, self._timestamp_debounce) >= self._debounce_ms:
                self._last_raw_state = raw_state
                self._timestamp_debounce = now

        return self._last_raw_state
    
    def rising_edge(self):
        current_state = self.get_value() 
        rising_edge_detected = self._last_debounced_state == 0 and current_state == 1
        self._last_debounced_state = current_state

        return rising_edge_detected
