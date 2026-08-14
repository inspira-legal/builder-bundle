# Vocabulary — one name per thing, in Portuguese

## Where this applies

Everything the builder reads in Portuguese: gate questions and option labels, the
Portuguese prose of a `description:`, reports, commit messages, and plain chat. The
reference documents and the SKILL.md prose are written in English and stay English — an
English document saying "load-bearing decision" is ordinary English, written the way that
language writes it. This page governs the Portuguese sentence, and the table below is what
you reach for when the document you just read is in English and the answer you are about to
give is in Portuguese.

## The principle

Call each thing by the name it already has in the code or in the repo: the file, the
function, the branch, the PR, the `x` field. Quote that name exactly as written — a name is
an identifier, and half of its value is that a search finds it.

A concept that belongs to this plugin gets one name, and where Portuguese and English both
have a word for it, the Portuguese one is what you write. The item of `## Tarefas` is a
**tarefa**; the artifact at `.bb/<slug>/spec.md` is a **spec**.

## The table

The `chave` column is a search key — it is what the English document you just read said. The
`escreva` column is what the Portuguese sentence gets.

| chave         | escreva              | sentido                                       |
| ------------- | -------------------- | --------------------------------------------- |
| blocker       | impedimento          | o que trava a tarefa                          |
| brief         | spec                 | o arquivo `spec.md` — em inglês também `spec` |
| fan-out       | despacho em paralelo | vários agentes de uma vez                     |
| finding       | achado               | o item que o review devolve                   |
| gray area     | zona cinzenta        | a decisão que a spec ainda não fechou         |
| land          | landar               | levar a branch até o destino                  |
| lens          | lente                | o ângulo que um finder recebe                 |
| load-bearing  | estruturante         | a decisão cara de desfazer                    |
| read-only     | só leitura           | o agente que lê e não edita                   |
| scope         | escopo               | o recorte que o caller passa                  |
| seam          | fronteira            | onde duas partes se encontram                 |
| shape (ideia) | especificar          | dar forma a uma ideia — é o `/bb:spec`        |
| shape (dado)  | formato              | `Finding shape` é o formato do achado         |
| slice         | tarefa               | o item do `## Tarefas` — em inglês, `task`    |
| verdict       | veredito             | CONFIRMED / PLAUSIBLE / REFUTED               |

Two rows carry an exception worth stating in full:

- **brief.** Inside `skills/brisar/**` the design brief is its own artifact, with its own
  file (`brief-design.md`) and its own name — there, "brief" is that document and keeps the
  word. Everywhere the text points at `.bb/<slug>/spec.md`, the word is **spec**.
- **land.** "landa essa branch", "esverdeia a PR" and "shapeia essa ideia" are how the user
  speaks and are what routes a skill. Trigger phrases are quoted as the user says them; the
  table governs the prose around them.

## Capitalization

Portuguese runs in sentence case: the first letter of the line goes up, and the rest of the
words keep the case they have in the dictionary. It holds the same for a heading
(`## Fora de escopo`), an option label ("Neste contexto"), a gate question, and a report
line.

Two things keep their exact case instead. **Proper names** — a phase of the double diamond
("Fase Deliver"), a product, a brand color out of `references/ds/brand/**`. And
**identifiers** — `spec.md`, `/bb:implement`, `lint_spec.py`, `CONFIRMED`, `W003` — which are
written the way the code writes them, in any position including the start of a sentence.

`(Recomendado)` is a suffix: it follows the label of the recommended option, after the label
text, wherever the gate convention asks for one.

## When the word isn't on the table

Say in three words what happens: "o agente que só lê", "a decisão que trava o build". A
description costs three words and lands the first time; a freshly coined name costs one word
and then has to be taught, drifts, and comes back in the next session with a gender nobody
gave it — which is how a word the plugin never wrote ends up sounding like plugin vocabulary.

When the thing already has a name in the code or in the repo, that name is the answer, and
the three-word description is for the concept that has no name anywhere yet.
