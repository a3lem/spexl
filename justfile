default:
    @just --list

plugins:
    shablon generate

test:
    uv run pytest

sync: plugins
