# Onboarding

## REMOVED Requirements

### Requirement: Onboard command
**Reason**: The `spexl onboard` command served methodology content for manual paste into AGENTS.md/CLAUDE.md. This workflow is replaced by the install command, which generates a rules file (`sdd-with-spexl.md`) containing the same content, installed directly to the target's rules directory. Manual paste is no longer necessary.
**Migration**: Users should run `spexl install -t <target>` instead of `spexl onboard`. The rules file is automatically installed alongside skills and agents. Existing AGENTS.md/CLAUDE.md entries pasted via the old command should be removed to avoid duplication.
