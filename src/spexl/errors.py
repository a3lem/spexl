# [AI]
# Context: rewrite-as-spexl (task 1.2)
# Intent: single error type for CLI, replaces SpectlError from spectl.py


class SpexlError(Exception):
    pass
