# Evals of /bb:animate-tour

Three scenarios that check `/bb:animate-tour` picks up the right requests and follows its own
steps, run on Haiku, Sonnet and Opus. They follow the evaluation advice of Anthropic's skill
authoring guide: a few concrete scenarios written down before the skill changes, run on every
model the skill will meet.

## Where the evals live

`evals/` sits at the repo root, outside `plugins/bb`, so nothing here ships with the plugin.
One folder per skill (`evals/<skill>/`) with the same four parts:

- `scenarios.json`: the scenarios, in the guide's shape (`skills`, `query`, `files`,
  `expected_behavior`).
- `run.mjs`: the runner. It loads `plugins/bb` through the Claude Agent SDK with no user or
  project settings, so only bb is in context, and grades each transcript.
- `fixtures/`: the files a scenario hands the skill.
- `results/DATE/`: each run's transcript and checks, kept so a later run has a baseline.

## The scenarios

1. **`trigger`**: four requests, each run 5 times per model. The first `Skill` call has to name
   the expected skill. The GIF for the launch email and the video for the launch sit next to
   each other on purpose: they are the pair `/bb:reel` and `/bb:animate-tour` can confuse.
2. **`gif-from-screenshots`**: three screenshots of a mock "Pesquisa" feature that carry
   names, CNJ numbers, amounts and dates. The skill has to ask the mode and the quality, show
   the step plan in an `AskUserQuestion` before producing, keep every piece of that data out of
   the plan and the scene, record with `scripts/tour.mjs`, read the stills, and close with a
   plain text question.
3. **`no-browser`**: a request to walk the feature in the browser, in a session with no
   browser. The skill has to stop, offer the choice (connect Claude in Chrome or send
   screenshots; reading the code is an option only in code mode) in an `AskUserQuestion`, and
   wait for the screenshots once they are picked.

The runner plays the person: it answers each `AskUserQuestion` with the scenario's `answers`
(the `RESPONDERS` in `run.mjs` match them to the options), and replies in text when a turn ends on a question. It allows writes only inside the
run's `scenes/` folder (the path resolved, so `scenes/../` stays out), and Bash only for the
exact `tour.mjs` verbs and `ls`, `file`, `du` and `stat`, with no shell operators. It denies the
rest. A check passes on a call's result, not on the call: the record has to succeed and leave
its full GIF on disk, and a still has to be read back without error.

## Run them

```bash
cd evals/animate-tour
npm install
node run.mjs trigger
node run.mjs scenario no-browser
node run.mjs scenario gif-from-screenshots
```

After a grader changes, `node run.mjs regrade results/DATE/FILE.json` grades a saved run
again without running the model.

`--models haiku` narrows the run to one model, and `--runs 3` changes the trigger repetitions.
The GIF scenario needs the studio installed once (`/bb:reel`'s bootstrap). Each scenario run
gets a studio of its own: a temporary folder passed as `MOTION_HOME`, linked to the install in
`~/Motion`, with empty `scenes/` and `out/`. Runs never share a scene, even when every model
picks the same slug, and `~/Motion` is left as it was. The result file names that folder
(`studio`), where the scene and the GIFs stay.

A trigger check through `claude -p --tools ""` does not measure triggering: with no `Skill`
tool, the skill list is not in context, and the model guesses from the request alone. The
runner keeps the `Skill` tool and reads which skill it calls.

## Results

Run on 2026-10-19 on `main` at `e315d72` (the trigger before the rebase, on `ce99ef3`, which
has the same skill), with `claude-haiku-5-5`,
`claude-sonnet-5-5` and `claude-opus-5-5`. The transcripts are in `results/2026-10-19/`.

### Trigger, 5 runs per model

| Request                                                                                             | Expected          | Haiku | Sonnet | Opus |
| --------------------------------------------------------------------------------------------------- | ----------------- | ----- | ------ | ---- |
| preciso de um GIF mostrando como a feature de pesquisa funciona, para o e-mail de lançamento        | `bb:animate-tour` | 5/5   | 5/5    | 5/5  |
| faz um vídeo de lançamento da feature de pesquisa, 20s, vertical                                    | `bb:reel`         | 5/5   | 5/5    | 5/5  |
| quero um modal de onboarding animado para a nova feature de prazos                                  | `bb:animate-tour` | 5/5   | 5/5    | 5/5  |
| o StepArt do tour de Gestão de Projetos precisa de um passo novo mostrando o filtro por responsável | `bb:animate-tour` | 5/5   | 5/5    | 5/5  |

### Scenarios, 1 run per model

| Check                      | Haiku | Sonnet | Opus |
| -------------------------- | ----- | ------ | ---- |
| `gif-from-screenshots`     | 6/7   | 5/7    | 6/7  |
| asks_mode                  | yes   | yes    | yes  |
| asks_quality               | yes   | no     | yes  |
| plan_in_question           | yes   | yes    | yes  |
| real_data_replaced         | no    | no     | no   |
| records_with_tour_mjs      | yes   | yes    | yes  |
| reads_stills               | yes   | yes    | yes  |
| closes_with_plain_question | yes   | yes    | yes  |
| `no-browser`               | 4/4   | 4/4    | 4/4  |

What the misses were:

- **real_data_replaced, all three.** Each model turned `Parecer_Locacao_Ribeiro.pdf` into
  `Parecer_Locacao_01.pdf` or `Parecer_Locacao.pdf` in the scene: the client's name went, the
  rest of the screenshot's file name stayed. `pattern.md` asks to replace file names whole, and
  gives `Contrato_01.pdf` as the model, which reads as "keep the kind of document, add a
  number". Opus also listed the parties' real names in the plan, to say what it replaced. Every
  name, CNJ number, amount and date was replaced in the scenes. Two lines in `pattern.md`,
  section 1, would close it: the new file name is invented, never derived from the
  screenshot's, and the plan says what was replaced by kind ("os nomes das partes") without
  quoting it.
- **asks_quality, Sonnet.** It asked the mode and the plan in one question ("Aprovado, GIF"),
  never asked the quality, and recorded `light` and `high`, which the skill allows only when the
  person does not know.

How the models asked: Haiku asked the mode with the quality in its labels ("Fora do app, GIF
light") and the plan in the same `AskUserQuestion`. Opus did the same and asked the feature's
icon too. Sonnet folded the mode into the plan's approval. All three showed the plan before
writing the scene.

These are single runs. A scenario that fails once is worth running again before it changes the
skill.
