from sensors import LDR, BTN
from states import StateMachine
import time

# gpios usadas =)
LDR_PIN = 12
BTN_PIN = 13

# intervalo tolerável no estado OBSTRUCTED em milissegundos
MICRO_STOP_TIME_MS = 5000

def main():
    # interfaces para os perifericos e máquina de estado
    ldr = LDR(LDR_PIN)
    btn = BTN(BTN_PIN)
    state_machine = StateMachine()

    count = 0                   # count se refere ao contador de produtos
    timestamp = time.ticks_ms() # timestamp guarda um momento de referencia para calcular a microparada   
    alert_triggered = False     # flag para nao poluir o terminal, imprimindo o alerta apenas uma vez

    print("Contador de Producao Inicializado")

    while True:
        # leitura do sensor de luz e detectação da borda de subida do botão já com debounce  
        raw_value = ldr.get_raw_value()
        btn_rising = btn.rising_edge()

        if btn_rising:
            count = 0
            timestamp = time.ticks_ms()
            alert_triggered = False
            print("Turno resetado com sucesso. Contadores zerados.")

        # inferencia do estado do novo estado 
        state = state_machine.update(raw_value) 

        if state == StateMachine.FALLING:
            timestamp = time.ticks_ms() # nova referencia de tempo para ser usada no estado OBSTRUCTED

        elif state == StateMachine.OBSTRUCTED:
            if not alert_triggered and time.ticks_diff(time.ticks_ms(), timestamp) >= MICRO_STOP_TIME_MS:
                print("Alerta: Micro-parada detectada!")
                alert_triggered = True

        elif state == StateMachine.RISING:
            count += 1
            print("Peca detectada! Total:", count)
            alert_triggered = False

        # trecho puramente semantico, não faz nada além de aguardar e pode ser removido  
        elif state == StateMachine.FREE:
            pass


if __name__ == "__main__":
    main()