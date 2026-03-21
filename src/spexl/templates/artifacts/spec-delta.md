<!-- GIVEN guidance:
     Use GIVEN when the scenario depends on setup or state. Omit when there is none.

     Good GIVEN (precondition matters):
       - GIVEN a user with expired credentials
       - WHEN the user attempts login
       - THEN the system rejects the attempt

     No GIVEN needed (no precondition):
       - WHEN the user runs `spexl --version`
       - THEN the system prints the version string

     Smell: if your WHEN contains "and X exists" or "in a project with no Y",
     extract that to GIVEN. WHEN should be the action only. -->

## ADDED Requirements

### Requirement: [Requirement name]
The system SHALL [requirement].

#### Scenario: [Descriptive name]
- **GIVEN** [precondition or system state]
- **WHEN** [action or trigger]
- **THEN** [expected outcome]
- **AND** [additional outcome]

## MODIFIED Requirements

<!-- MODIFIED replaces the entire requirement block at merge time.
     Include ALL scenarios, even unchanged ones. The heading is the match key. -->

### Requirement: [Existing requirement name]
[Full updated requirement text]

#### Scenario: [Unchanged scenario]
[Include as-is from the reference spec]

#### Scenario: [New or changed scenario]
- **GIVEN** [precondition or system state]
- **WHEN** [action]
- **THEN** [new expected outcome]

## REMOVED Requirements

### Requirement: [Removed requirement name]
**Reason**: [Why this is being removed]
**Migration**: [What replaces it, if anything]

## RENAMED Requirements

### FROM: [Old requirement name]
### TO: [New requirement name]
