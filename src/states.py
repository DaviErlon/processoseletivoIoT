class StateMachine:
    # Estados (os valores atribuidos nao representam nada alem de uma enumeracao)
    FREE = 0        # -> Luz livre
    OBSTRUCTED = 1  # -> Luz bloqueada
    RISING = 2      # -> Borda de subida (acabou de voltar para FREE)
    FALLING = 3     # -> Borda de descida (acabou de entrar em OBSTRUCTED)

    # LUX_FREE_THRESHOLD é o limite do intervarlo [0 a 999], ou seja, mais que 500 lux 
    # LUX_OBSTRUCTED_THRESHOLD  é o limite do intervalor [2045 a 4095], ou seja, menos que 100 lux
    def __init__(self, initial_state=FREE, LUX_FREE_THRESHOLD=999, LUX_OBSTRUCTED_THRESHOLD=2045):
        self._state = initial_state
        self.LUX_FREE_THRESHOLD = LUX_FREE_THRESHOLD
        self.LUX_OBSTRUCTED_THRESHOLD = LUX_OBSTRUCTED_THRESHOLD

    def update(self, raw_value):
        """
        Atualiza a máquina de estados e retorna o estado/evento atual.
        """

        # Estado FREE
        if self._state == self.FREE:
            if raw_value >= self.LUX_OBSTRUCTED_THRESHOLD:
                self._state = self.OBSTRUCTED
                return self.FALLING

            return self.FREE

        # Estado OBSTRUCTED
        if self._state == self.OBSTRUCTED:
            if raw_value <= self.LUX_FREE_THRESHOLD:
                self._state = self.FREE
                return self.RISING

            return self.OBSTRUCTED

        return self._state