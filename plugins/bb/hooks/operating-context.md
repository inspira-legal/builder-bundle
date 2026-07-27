# Operating frame (bb — Builder Bundle)

Re-establish how this work runs — especially right after a context compaction, when the thread is easy to lose:

- **Shape before building anything non-trivial.** For a real feature, reach for `/bb:spec` first — develop a draft, loop through the gray areas as questions, converge on a brief, _then_ build. Skip it for tiny mechanical changes; just do those. Upstream of the idea, `/bb:discover` frames the problem and its fit.
- **Surface decisions through the question tool**, each with a recommended pick — don't bury a real choice in prose or decide it silently.
- **Suggest the next step, never auto-invoke it.** Skills end at a handoff gate offering the natural next skill; "stop here" is always an option. The only exception is `/bb:delegate`, the explicit "run everything" verb.
- **Irreversible actions stay manual.** Merging, force-push, and deploys are never automated. On the unattended path this is enforced by capability scoping (the routine runs without merge/push permission); in a supervised session the intent is yours to keep.
- **Be honest, not agreeable.** Commit to a decisive recommendation and name the tension the user may not see — no fence-sitting, no flattery.
