from sensors import LDR, BTN
from states import StateMachine, States
import time

#gpios usadas =)
LDR_PIN = 12
BTN_PIN = 13

#intervalo tolerável no estado low em milissegundos
MICRO_STOP_TIME_MS = 5000

def main():
    # interface para abstrair a inicialização e logica dos 
    # periféricos, configurando pinos e atributos usados pelos métodos
    ldr = LDR(LDR_PIN)
    btn = BTN(BTN_PIN)

    # interface que abstrai a logica da máquina de estados
    state_machine = StateMachine(initial_state=States.HIGH)

    #variavel count se refere ao contador de produtos
    # e timestamp guarda o momento em que o estado é de descida
    count = 0
    timestamp = 0.0

    #flags para nao poluir o terminal 
    alert_triggered = False
    reset_triggered = False

    print("Contador de Producao Inicializado")

    while True:
        state = state_machine.update(ldr.get_raw_value(), btn.get_value())

        # Reset das flags conforme o estado
        if state == States.RESET:
            if not reset_triggered:
                count = 0
                timestamp = 0.0
                print("Turno resetado com sucesso. Contadores zerados.")
                reset_triggered = True
        else:
            reset_triggered = False  # permite novo reset quando o botão for solto


        if state == States.FALLING:
            timestamp = time.ticks_ms()
            alert_triggered = False  # nova parada, alerta ainda não emitido

        elif state == States.LOW:
            if not alert_triggered and time.ticks_diff(time.ticks_ms(), timestamp) >= MICRO_STOP_TIME_MS:
                print("Alerta: Micro-parada detectada!")
                alert_triggered = True

        elif state == States.RISING:
            count += 1
            print("Peca detectada! Total:", count)
            alert_triggered = False

        elif state == States.HIGH:
            pass

if __name__ == "__main__":
    main()