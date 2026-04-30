# Verification

Every requirement and scenario in a spec should have a corresponding test. Verification is part of the apply phase, not a separate phase.

## Test Strategies

Choose based on what's being tested:

- **Unit tests** (pytest): logic-heavy code, pure functions, data transformations
- **Behavioral tests** (subprocess): CLI tools, end-to-end flows, input/output contracts
- **Differential tests**: "this input produces this output" -- suitable for parsers, formatters, simple transformations

## Writing Tests

Spec scenarios are already written in Given/When/Then. They translate directly to test cases.

For each requirement in `deltas/*/spec.md`:

1. Identify the scenarios
2. Write a test per scenario (or per meaningful group)
3. Annotate with `# spec:` comments

Trivial scenarios that are covered by other tests don't need dedicated test functions.

## Spec Annotations

Link tests back to specs with comments above the test function:

```python
# spec: session-management requirement=session-timeout scenario=idle-timeout
def test_idle_timeout():
    ...
```

Format: `# spec: <name> requirement=<slug> scenario=<slug>`

- `<name>` is the spec name (directory name under `reference/` or `deltas/`)
- `requirement` is the slugified requirement heading
- `scenario` is the slugified scenario heading (optional for requirement-level tests)

File-level annotations link the whole file to a spec:

```python
"""Tests for session timeout.
# spec: session-management requirement=session-timeout
"""
```

This convention is language-agnostic. In non-Python files:

```javascript
// spec: session-management requirement=session-timeout scenario=idle-timeout
test('idle timeout disconnects after 30 minutes', () => {
```

## Verification as a Gate

A change is not `complete` until:

- Every requirement has at least one test
- Every non-trivial scenario has a corresponding test
- All tests pass

`tasks.md` should include a Verification section with test-writing tasks. These tasks block the change from reaching `complete` status.

## Coverage Check

To verify coverage, grep for `# spec: <name>` across test files and cross-reference against requirements in the spec. Every `### Requirement:` heading in the spec should appear as a `requirement=<slug>` in at least one test annotation.
