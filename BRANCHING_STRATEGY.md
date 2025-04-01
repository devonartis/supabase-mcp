# Branching Strategy

## Main Branches
- `main` - Production-ready code (protected)
- `develop` - Integration branch for features (protected)

## Feature Branches
Format: `feature/[area]-[description]`
Examples:
- `feature/ui-core-components`
- `feature/layout-setup`
- `feature/charts-integration`
- `feature/ai-chat`

## Bug Fix Branches
Format: `fix/[issue-number]-[description]`
Example: `fix/123-chart-rendering`

## Hotfix Branches
Format: `hotfix/[issue-number]-[description]`
Example: `hotfix/456-critical-security-fix`
- Created from `main` for urgent production fixes
- Merged into both `main` and `develop`

## Release Branches
Format: `release/[version]`
Example: `release/1.0.0`
- Created from `develop` when features are complete
- Used for final testing and preparation
- Merged into `main` and tagged when released

## Branch Protection Rules
- Require pull request reviews before merging
- Require status checks to pass
- Require linear history
- Prevent force pushes
- Require signed commits
- Automatically delete merged branches

## Branch Workflow
1. Create feature branch from `develop`
2. Develop and test feature locally
3. Push branch and create PR to `develop`
4. Run CI/CD pipeline and automated tests
5. Code review and approval by at least 2 maintainers
6. Squash merge into `develop`
7. Periodically create release branch from `develop`
8. Perform final testing on release branch
9. Merge release branch into `main` and tag version
10. Delete release branch after merge

## Branch Cleanup Policy
- Delete feature branches after merge
- Delete release branches after merge
- Keep hotfix branches for 7 days after merge
- Weekly cleanup of stale branches (unmerged for > 30 days)

## Commit Message Format
```
type(scope): subject

[optional body]
[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only changes
- style: Changes that do not affect the meaning of the code
- refactor: Code change that neither fixes a bug nor adds a feature
- test: Adding missing tests
- chore: Changes to the build process or auxiliary tools
- perf: Performance improvement
- ci: CI/CD pipeline changes
- revert: Revert a previous commit

Examples:
```
feat(ui): add stock chart component

- Implement TradingView lightweight charts
- Add basic price and volume display
- Include zoom controls

Closes #123
```

```
fix(charts): correct volume calculation

- Fix volume calculation formula
- Add validation for negative values
- Update related tests

Fixes #456
```

```
chore(deps): update axios to v1.4.0

- Update axios package
- Update related types
- Update mock server config
```
