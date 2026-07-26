# Relatório do Candidato

---

## Identificação do Candidato

- **Davi Erlon Lopes de Morais:**
- **GitHub: https://github.com/DaviErlon**

---

## Visão Geral da Solução

O projeto tem como objetivo desenvolver uma solução de baixo custo para o monitoramento de linhas de produção industriais, realizando a contagem automática de produtos e a identificação de falhas operacionais de maneira não intrusiva, ou seja, sem alterar a estrutura física da esteira.

O sistema embarcado simulado utiliza um sensor que detecta a passagem de itens por meio do bloqueio da luz de uma fonte posicionada em frente a esse sensor, contabilizando a produção e sinalizando possíveis anomalias no funcionamento com base no tempo do bloqueio.

A interação com o usuário pode ser feita a partir de um botão físico, que permite reiniciar o contador a qualquer momento, viabilizando o início de um novo ciclo de operação.

---

## Arquitetura do Sistema Embarcado

O sistema foi desenvolvido de forma modular, separando as responsabilidades de aquisição dos sinais, controle da lógica da aplicação e execução do programa principal. Essa organização facilita a manutenção do código, aumenta sua legibilidade e permite a reutilização dos módulos em outros projetos.


```
  src/
  ├── main.py
  ├── sensors.py
  └── states.py
```

1. O arquivo `main.py` é o ponto de entrada do programa. Nele são declaradas constantes e instanciados os sensores, a máquina de estados e as variáveis de controle necessárias à execução da aplicação. Em seguida, o programa entra em um loop que realiza periodicamente a leitura do sensor óptico e do botão. A leitura do sensor óptico é utilizada para atualizar a máquina de estados, enquanto a leitura do botão atua exclusivamente no reset das variáveis de controle, com destaque para o contador. Com base no estado atual da máquina, são executados blocos específicos para a contagem de produtos e a detecção de microparadas.

2. `sensors.py` contém as classes que abstraem o funcionamento dos periféricos, encapsulando a inicialização dos pinos e fornecendo métodos de leitura para o programa principal. A classe LDR modela o sensor de luminosidade, disponibiliza o método `.get_raw_value()`, que retorna o valor digital bruto do ADC, e `.get_lux()`, que converte esse valor em lux utilizando o cálculo presente na documentação [oficial do sensor](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor) (apesar de este último não ser utilizado neste código, o que será justificado mais adiante). Já a classe BTN representa o botão físico, e em seu construtor configura-se corretamente o pino como entrada e com ativação do pull-up interno; possui os métodos `.get_value()`, que implementa um algoritmo de debounce e retorna o estado estável do botão, e o método `.rising_edge()`, que detecta a borda de subida do sinal (transição de 0 para 1), permitindo capturar o momento exato em que o botão é liberado — recurso empregado para acionar a reinicialização do contador.

3. Por último, `states.py` contém a classe StateMachine, representando uma máquina de estado baseada nas ideias de autômatos — o estado determina o bloco, e, após o bloco, um novo estado. Seu construtor permite definir os limiares de luminosidade que determinam as transições: LUX_FREE_THRESHOLD (abaixo do qual considera-se luz livre) e LUX_OBSTRUCTED_THRESHOLD (acima do qual considera-se luz bloqueada). O método `.update(raw_value)` recebe o valor bruto do LDR e, a partir dele e dos limites, decide o estado/evento atual da máquina, que é retornado e representa um dos seguintes atributos da própria classe:

```python
  FREE = 0        # -> Luz livre
  OBSTRUCTED = 1  # -> Luz bloqueada
  RISING = 2      # -> Borda de subida (estado imediatamente anterior a todo FREE)
  FALLING = 3     # -> Borda de descida (estado imediatamente anterior a todo OBSTRUCTED)
```

A lógica de transição é simples: se estiver em FREE e o valor lido for maior ou igual ao limiar de obstrução, a máquina transita para OBSTRUCTED e retorna o evento FALLING; se estiver em OBSTRUCTED e o valor lido for menor ou igual ao limiar de luz livre, transita para FREE e retorna o evento RISING. Caso contrário, permanece no estado atual. O botão de reinicialização não influencia a máquina de estados, atuando apenas sobre as variáveis de controle no arquivo principal.

---

## Componentes Utilizados na Simulação

- [ESP32](https://docs.wokwi.com/guides/esp32): É o microcontrolador do sistema embarcado, o "cérebro" da simulação. Ele é o responsável por executar o código, processar os dados dos sensores e controlar a lógica do sistema
- [Botão](https://docs.wokwi.com/parts/wokwi-pushbutton) (Push Button): É um componente de entrada que permite a interação do usuário com o sistema.
- [LDR](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor) (Photoresistor): É um sensor de luz analógico. Sua resistência elétrica varia de acordo com a intensidade de luz incidente, permitindo que o sistema detecte quando um objeto bloqueia a luz.

---

## Decisões Técnicas Relevantes

Organização do código em três módulos: A separação em `main.py`, `sensors.py` e `states.py` foi adotada para isolar responsabilidades: a aquisição de dados, a lógica de estados e o controle do fluxo principal. Essa arquitetura modular segue boas práticas da engenharia de software, facilitando manutenção, legibilidade, escalabilidade e reutilização.

Inclusão dos estados RISING e FALLING: Intuitivamente, a máquina de estados consideraria apenas os estados FREE e OBSTRUCTED. A adição dos eventos RISING (transição de obstruído para livre) e FALLING (transição de livre para obstruído) foi essencial para distinguir momentos críticos: a contagem de produtos, ocorrendo apenas na borda de subida (RISING), evitando contagens duplicadas, e a medição de tempo para detecção de microparadas é iniciada na borda de descida (FALLING), tornando a lógica mais precisa e confiável, além de evitar muitas flags de controle.

Uso do valor bruto do ADC em vez de conversão para lux: A interface criada para o LDR oferece o método `.get_lux()`, que converte o sinal analógico para lux utilizando operações com potências e constantes como GAMMA e RL10. No entanto, optou-se por utilizar o valor bruto do ADC (.get_raw_value()) e compará-lo diretamente com limiares em contagem digital, obtidos manualmente no simulador Wokwi: valores ≤ 999 indicam luz livre (equivalente a > 500 lux), enquanto valores ≥ 2045 indicam obstrução (equivalente a < 100 lux). Essa escolha reduz drasticamente o custo computacional, pois elimina operações de ponto flutuante e exponenciação, mantendo a mesma funcionalidade com ganhos significativos de desempenho — especialmente relevante em microcontroladores com recursos limitados.

Estratégia de temporização não-bloqueante: O sistema não utiliza temporizadores por hardware ou interrupções (IRQs) para medir o tempo de obstrução. Em vez disso, a lógica de detecção de microparadas baseia-se no armazenamento de um timestamp no momento da transição FALLING e na comparação com o tempo atual dentro do loop principal, usando `time.ticks_diff()`. Essa abordagem é não-bloqueante e suficientemente precisa para a faixa de tempo considerada. O uso de IRQs seria desnecessário e introduziria complexidade adicional, como a necessidade de gerenciar o desarme das interrupções durante o reset do contador e no estado RISING, sem trazer benefícios reais.

---

## Resultados Obtidos

O sistema simulado apresentou comportamento conforme o esperado, atendendo a todos os requisitos funcionais propostos. Os principais resultados observados são:

1. O módulo de contagem e detecção de microparadas opera corretamente, respondendo às variações de luminosidade e ao acionamento do botão. Em ambiente simulado, os limiares definidos mostraram-se adequados, mas é válido ressaltar que em um cenário real seria necessário adaptar os valores com base no calculo real de luminozidade (999 e 2045 são limites equivalentes a 100 e 500 de luz somente sobre um GAMMA de 0.7 e RL10 de 50 kilo-ohms).

2. A simulação passou em todos os testes do Actions. Destaca-se a decisão de implementar a reinicialização do contador na borda de subida do botão, por meio do método `.rising_edge()`. Embora a prática mais comum seja utilizar a borda de descida, a opção pela subida foi adotada para atender de forma limpa ao terceiro teste, evitando soluções "gambiarrescas".

3. No site do Wokwi e localmente, o sistema funciona plenamente, inclusive com o método `.get_lux()` quando utilizado, porém, no ambiente do GitHub Actions, a simulação apresentou instabilidades, provavelmente causado pela execução de cálculos com ponto flutuante e exponenciação, o que motivou a opção pelo uso do valor bruto do ADC para garantir robustez nos testes automatizados.
---

## Comentários Adicionais

#### Dificuldades encontradas
O principal desafio foi lidar com o GitHub Actions e compreender o funcionamento dos arquivos `.yaml` para depuração dos testes automatizados. Um exemplo disso foi o caso da borda de subida do botão: a condição de parada da simulação só é satisfeita após o botão ser liberado, e os logs indicavam apenas que a simulação havia excedido o tempo limite de 10 segundos, sem apontar diretamente a causa. Foi necessário um processo investigativo para identificar que o erro estava justamente na detecção da borda, evidenciando a importância de uma instrumentação mais detalhada nos testes automatizados.

#### Limitações da simulação
O ambiente Wokwi, embora eficaz para validação conceitual, não reproduz fielmente o comportamento de diversos sensores. Em particular, as configurações `AO.atten(ADC.ATTN_11DB)` e `AO.width(ADC.WIDTH_12BIT)` em `sensors.py` são ignoradas pela simulação, mas são necessárias em uma implementação real no ESP32, onde a atenuação e a resolução do ADC afetam diretamente a faixa de leitura.

#### Melhorias futuras
Em primeiro lugar, a transcrição do código para C permitiria maior eficiência e portabilidade para microcontroladores com restrições de memória. Além disso, o sistema poderia ser ampliado para gerar relatórios ao final de cada ciclo, contendo o total de peças contadas, a velocidade média de produção e os horários de início e fim do turno, agregando valor à análise de produtividade.

#### Principais aprendizados
Durante o desenvolvimento, houve um aprofundamento significativo no funcionamento do sensor LDR, incluindo o estudo de sua curva de resposta e dos cálculos presentes na documentação oficial para conversão em lux. Também ficou evidente que o MicroPython, embora ágil e didático, carece de estruturas como Enum e match, que tornariam o código mais expressivo e legível para uma máquina de estado.