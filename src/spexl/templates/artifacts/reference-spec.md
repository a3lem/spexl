# [Capability/Feature Name]

## Overview / Purpose

[Brief description of what this capability does and its role in the system.]

## Requirements

<!-- GIVEN guidance:
     Use GIVEN when the scenario depends on setup or state. Omit when there is none.

     Good GIVEN (precondition matters):
       Given a user with expired credentials
       When the user attempts login
       Then the system rejects the attempt

     No GIVEN needed (no precondition):
       When the user runs `spexl --version`
       Then the system prints the version string

     Smell: if your When contains "and X exists" or "in a project with no Y",
     extract that to Given. When should be the action only. -->

### Requirement: [Requirement name]

The system SHALL [requirement].

#### Scenario: [descriptive name]
  Given [precondition or system state]
  When [action]
  Then [expected outcome]

#### Scenario: [error case]
  Given [precondition or system state]
  When [invalid action]
  Then [error behavior]

### Requirement: [Another requirement name]

The system SHALL [requirement].

#### Scenario: [descriptive name]
  Given [precondition]
  When [action]
  Then [expected outcome]

## Non-Functional Requirements
<!-- (optional) Performance, security, reliability constraints -->

The system SHALL [performance/security/reliability requirement].

WHILE [condition], the system SHALL [constraint].

## Glossary
<!-- (optional) Define domain-specific terms -->

- [Term]: [Definition]
