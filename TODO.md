# TODO

## Next


## Doing


## Done

<!-- Periodically cleared. Not a log. -->

- Reworked `tests/test_generate.py` and `tests/test_steering.py` to mirror the installed tree verbatim against `src/spexl/content/`, assert per-action-skill deferral to the methodology skill, and drop all composition-era assertions.
- Renamed the methodology skill from `learn-about-sdd-with-spexl` (a.k.a. `spexl-101` mid-session) to `how-to-use-spexl`. Stripped the "librarian" persona framing. Action skills no longer reference file paths inside `how-to-use-spexl/`; they defer routing to the methodology skill. Propagated the rename and framing through specs, agents, action skills, onboard.md, and tests.
