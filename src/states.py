LUX_HIGH_THRESHOLD = 999   # <= 999 -> HIGH (luz livre)
LUX_LOW_THRESHOLD = 2045   # >= 2045 -> LOW (luz bloqueada)

class States:
    """
        HIGH     -> Luz livre
        LOW      -> Luz bloqueada
        FALLING  -> Borda de descida (acabou de entrar em LOW)
        RISING   -> Borda de subida (acabou de voltar para HIGH)
    """
    HIGH = 0
    LOW = 1
    RISING = 2
    FALLING = 3
    RESET = 4


class StateMachine:
    def __init__(self, initial_state=States.HIGH):
        self._state = initial_state

    def update(self, raw_value, btn_value):
        """
        Atualiza a máquina de estados e retorna o estado/evento atual.

        HIGH     -> Luz livre.
        LOW      -> Luz bloqueada.
        FALLING  -> Acabou de entrar em LOW.
        RISING   -> Acabou de voltar para HIGH.
        """
        if btn_value == 0:
            return States.RESET

        # Estado HIGH
        if self._state == States.HIGH:
            if raw_value >= LUX_LOW_THRESHOLD:
                self._state = States.LOW
                return States.FALLING

            return States.HIGH

        # Estado LOW
        if self._state == States.LOW:
            if raw_value <= LUX_HIGH_THRESHOLD:
                self._state = States.HIGH
                return States.RISING

            return States.LOW