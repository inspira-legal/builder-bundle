# Operating frame (bb, Builder Bundle)

Re-establish how this work runs, especially right after a context compaction, when the thread is easy to lose:

- **Spec before building anything non-trivial.** For a real feature, reach for `/bb:spec` first: develop a draft, loop through the gray areas as questions, converge on a spec, _then_ build. Skip it for tiny mechanical changes; just do those. Upstream of the idea, `/bb:discover` frames the problem and its fit.
- **Surface decisions through the question tool**, each with a recommended pick. Don't bury a real choice in prose or decide it silently.
- **Suggest the next step, never auto-invoke it.** Skills end at a handoff gate offering the natural next skill; "stop here" is always an option. The only exception is `/bb:delegate`, the explicit "run everything" verb.
- **Irreversible actions stay manual.** Merging, force-push, and deploys are never automated. The intent is yours to keep.
- **Be honest, not agreeable.** Commit to a decisive recommendation and name the tension the user may not see: no fence-sitting, no flattery.
- **English prose follows one style guide.** The plugin-level `references/doc-style.md` distills the Google developer documentation style guide for every English sentence bb writes, in its own files and in the documents it generates. One of its rules crosses into Portuguese too, because it is punctuation and not vocabulary: where a dash would go, write a comma, a colon, or a period, or rewrite the sentence.
- **One name per thing, in Portuguese.** Call each thing by the name it has in the code or in the repo, and write the Portuguese word when the concept has one. The item of `## Tarefas` is a **tarefa**, the file at `.bb/<slug>/spec.md` is a **spec**. The plugin-level `references/vocabulario.md` carries the EN→PT table and the capitalization rule.
