---
name: feedback_naming
description: Naming guidelines – avoid vague module names, use precise plain-language change slugs
type: feedback
---

**Module names:** Don't name modules after abstract categories like `plumbing.py`, `utils.py`, `helpers.py`, or `common.py`. Name them after what they operate on (the domain), not what role they play.

**Why:** Adriaan flagged `cli/plumbing.py` as having the same self-evidence as `utils.py`. The fix was splitting into `cli/changes.py`, `cli/links.py`, `cli/validate.py`, `cli/refs.py`.

**Change slugs:** Be precise, use plain language. 3-5 words recommended. One should know what the change does from the name alone. Describe what it *does*, not what it *is about*. Avoid corporate/abstract phrasing.

- Bad: `knowledge-delivery-architecture`, `claude-project-setup`, `toml-discovery`
- Good: `replace-context-with-prime-and-explain`, `add-hooks-on-init`, `add-toml-based-discovery`

**Why:** Adriaan called `knowledge-delivery-architecture` "linkedin speak." A slug should tell you what happens without opening the proposal.

**How to apply:** For modules, name after the domain. For change slugs, use verb-first plain language (3-5 words) that describes the concrete action.
