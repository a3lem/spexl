# Backlog

## Things to clarify to agent

A change cannot be applied unless all 4 artifacts are present (i.e. proposal, design, spec deltas, tasks) or unless one or more artifacts have been marked as skipped.

---

During the proposal and design phase it is important to gather as much information as possible. Use the AskUserQuestion repeatedly. Assume there is *always* more information to gather. Do not relent until the user explicitly says to stop asking questions.

---

To archive completed/rejected change, use `archive` command, not `mv`. Archive updates metadata on the change that mv skips.

---

Any '[CLARIFICATION NEEDED]' placeholder shall block the transition to the apply phase, pending clarification from the user.

---

A good change slug consists of 3 to 7 words. Helps to start with verb. Should be precise while remaining compact. Usually a verb phrase.

A good reference spec slug is similar in length, but usually a noun phrase. Slightly more general obviously, but still precise.

## Design directions

tasks.md. What is its role actually? Full-blown todo list vs. high-level overview of phases, with todos tracked separately.

---

Template files. Decompose into smaller units to make recombination easier. Tempted to use jinja but maybe slight overkill.

This probably works just as well:

```
"\n\n".join(
  [partal1, partial2, partial4]
)
```

---

`spexl changes --deltas` should show the ref specs impacted (name + rel path)

`spexl refs --changes` should show which ref specs are targeted by active changes.
