# The code front

Loaded by step 4 of `SKILL.md` when the plan picked the code front. Its evidence is a `file:line` in a cloned repository.

Two entry paths, by query type:

- **Discovery** (find repos for a topic): write 2 or 3 search queries from different angles
  and 1 or 2 GitHub topic slugs, then run the bundled script (path relative to this skill's
  directory):

  ```
  python3 scripts/search_repos.py "query 1" "query 2" --topic topic-slug-1 --topic topic-slug-2
  ```

  Optional flags: `--limit 20`, `--language python`, `--min-stars 500`. It returns a JSON
  list with `fullName`, `description`, `stargazersCount`, `updatedAt`, `language`, `url`,
  merged, deduplicated, filtered to 100+ stars by default and in GitHub's relevance order.

- **Targeted** (a named project): map the name to its repository (`vscode` is
  `microsoft/vscode`). When the name is ambiguous, run
  `python3 scripts/search_repos.py "project name" --min-stars 0` and take the top match.

Select at most three repositories, ranked by how directly they answer the questions.
When more than three fit, clone the top three and list the rest in the open section as
left out by the cap.

**Explorer prompt** (one per repository):

```
Clone https://github.com/OWNER/REPO shallow (--depth 1) into WORKDIR/repos/OWNER-REPO.

Answer these questions: [the planned questions relevant to this repo]

Return: purpose, stack, directory layout, architecture pattern, and for each question a
finding with a file:path:line citation as evidence. Keep it under 600 words.
```
