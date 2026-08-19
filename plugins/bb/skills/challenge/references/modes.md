# The five challenge modes

Load only the section for the mode chosen in Step 2. Every mode runs against the
**steelmanned** thesis, and every challenge it produces must be specific,
concrete, and pointed toward improvement.

## Questionar premissas: Socrático

Map the implicit premises of the thesis (what must be true for it to work).
Formulate questions that put each central premise in question. Climb the "why"
chain until you find unverified premises. Prioritize the 3–5 with the highest
impact if they are false.

## Testar evidências: Falsificação

Define the falsification criterion: what would need to be true to prove the
thesis wrong? Evaluate the quality of the evidence (direct observation, data,
anecdote, or assumption?). Identify gaps between the conclusion and what the
evidence actually supports.

## Construir contra-argumento: Dialético

Formulate the strongest possible antithesis, not the most obvious one.
Identify points of irresolvable tension between thesis and antithesis. Propose
a synthesis that acknowledges what each side gets right.

## Projetar falha: Pre-mortem

Assume it is 6 months in the future and the thesis has failed. Narrate 3–5
plausible failure stories: concrete, not generic. For each one, trace the chain
of second-order consequences. Order by probability.

## Atacar adversarialmente: Red Team

Adopt the perspective of whoever wants this to fail (competitor, internal
critic, market, regulator). Identify the most likely attack vectors. For each
vector: what would the specific action be, and what is the resulting damage?

## Worked examples

### "Desafia minha estratégia de migrar pra microservices no Q3"

**Steelman:** "Você acredita que decompor em serviços independentes vai eliminar
o gargalo de deploy, permitir que os 4 times entreguem em ciclos próprios e
melhorar o isolamento de falhas, especialmente depois dos 3 incidentes do
trimestre passado por acoplamento. É uma leitura justa?"

**Mode:** Pre-mortem.
**Challenge 1:** Em 6 meses, 2 dos 8 serviços foram extraídos mas o monolito
ainda depende deles via chamadas síncronas. O gargalo piorou porque toda mudança
toca os dois.
**Challenge 2:** Os serviços de pedidos e estoque têm consistência eventual, mas
a lógica assume consistência imediata. Uma promoção-relâmpago cria 200 pedidos
oversold em 4 minutos.

### "Questiona minhas premissas sobre lançar a feature X esse mês"

**Steelman:** reformulate the strongest argument for launching now; confirm.
**Mode:** Falsificação, _"O que precisaria ser verdade pra provar que lançar
agora é um erro? Que dados sustentam o timing, e o que é premissa?"_
