# Git Commit Convention for MSRA External Resources

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type Types

| Type | Description |
|------|-------------|
| feat | New external resource integration |
| fix | Bug fix in integration code |
| docs | Documentation changes |
| style | Formatting, no code change |
| refactor | Code restructuring |
| test | Adding or updating tests |
| chore | Maintenance tasks |
| perf | Performance improvements |
| ci | CI/CD changes |

### Scope

| Scope | Description |
|-------|-------------|
| registry | Resource registry changes |
| integration | Integration module changes |
| optimization | Optimization scheduler changes |
| tests | Test suite changes |
| docs | Documentation updates |
| deps | Dependency updates |

### Subject

- Use imperative mood: "add feature" not "added feature"
- No period at the end
- Max 50 characters

### Examples

```
feat(registry): add causalforest to candidate projects

Added causalforest R package to the registry with compatibility score 9.
This enables random forest based causal inference in MSRA pipeline.

Closes #123
```

```
fix(integration): resolve compatibility check false positives

The compatibility checker was incorrectly flagging installed packages.
Fixed by improving pip list parsing logic.

Tests: resources/external/tests/test_compatibility.py
```

```
docs(registry): update github_projects.json with new meta-analysis tools

Added bayesmeta and metaSEM to meta-analysis category.
Updated compatibility scores based on recent maintenance activity.
```

```
test(tests): add integration tests for resource loader

Added end-to-end tests for the complete resource loading workflow.
Tests cover registry loading, filtering, and statistics generation.
```

## Branch Naming

```
<type>/<scope>-<description>

Examples:
- feature/registry-add-pymeta
- fix/integration-compatibility-check
- docs/update-readme
- chore/add-ci-workflow
```

## Pull Request Guidelines

1. Title follows commit message format
2. Description includes:
   - What changes were made
   - Why the changes were made
   - How to test the changes
3. Link to related issues
4. Request review from maintainers

## Workflow for Adding New Resources

1. **Update Registry**
   ```bash
   # Add to github_projects.json or academic_literature.json
   git add resources/external/registry/
   git commit -m "feat(registry): add <resource-name> to <category>"
   ```

2. **Run Tests**
   ```bash
   pytest resources/external/tests/ -v
   ```

3. **Run Optimization Cycle**
   ```bash
   python -m resources.external.optimization.optimization_scheduler --run
   ```

4. **Generate Report**
   ```bash
   python -m resources.external.optimization.optimization_scheduler --report
   ```

5. **Commit All Changes**
   ```bash
   git add -A
   git commit -m "chore: complete resource integration cycle"
   ```
