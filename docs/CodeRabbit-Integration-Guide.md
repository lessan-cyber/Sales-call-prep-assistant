# CodeRabbit Integration Guide

This guide provides step-by-step instructions for integrating and using CodeRabbit AI-powered code reviews in the Sales-call-prep-assistant project.

## Table of Contents

1. [Installation](#installation)
2. [Configuration Overview](#configuration-overview)
3. [Usage Examples](#usage-examples)
4. [Review Workflow](#review-workflow)
5. [Commands Reference](#commands-reference)
6. [Customization](#customization)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Install CodeRabbit GitHub App

1. Navigate to [https://coderabbit.ai/](https://coderabbit.ai/)
2. Click **"Get Started"** or **"Install App"**
3. Sign in with your GitHub account
4. Select your repository: `Sales-call-prep-assistant`
5. Grant the following permissions:
   - **Contents**: Read access to code
   - **Pull requests**: Read and write access for reviews
   - **Checks**: Write access for review status
   - **Discussions**: Read access for Q&A

### Step 2: Verify Configuration

The `.coderabbit.yaml` configuration file is already in the repository root. CodeRabbit will automatically detect it when a PR is created.

To verify the configuration is working:
```bash
# Check if the file exists
ls -la .coderabbit.yaml

# View the configuration
cat .coderabbit.yaml
```

### Step 3: Test the Integration

1. Create a test branch:
   ```bash
   git checkout -b test/coderabbit-integration
   ```

2. Make a small change (e.g., add a comment)

3. Create a pull request to `main` branch

4. CodeRabbit will automatically start reviewing within 2-3 minutes

5. Check the PR for CodeRabbit's review comments and summary

## Configuration Overview

### What We've Configured

The `.coderabbit.yaml` file includes:

#### 1. **Profile & Tone**
- `profile: assertive` - More thorough feedback
- `tone_instructions: "Be concise and focus on critical issues..."` - Custom tone

#### 2. **Auto Review Settings**
- Automatically reviews all PRs (except drafts)
- Ignores PRs with "wip", "draft", "fixup" in title
- Reviews all changes to `main` branch

#### 3. **Language-Specific Tools**
- **Python**: ruff, flake8, pylint
- **TypeScript/JavaScript**: eslint, biome
- **Security**: gitleaks, semgrep, osv-scanner
- **Docs**: markdownlint
- **Infrastructure**: actionlint, checkov, hadolint

#### 4. **Path-Based Instructions**
- Custom review guidelines for each file type
- Specific rules for FastAPI routers
- Specific rules for AI agents
- React/Next.js component guidelines

#### 5. **Custom Checks**
- Environment variables validation (error level)
- Security vulnerability scanning (error level)
- Database migration verification (warning level)

#### 6. **Pre-merge Checks**
- Docstring coverage (80% threshold, warning)
- PR title format (warning)
- PR description completeness (warning)

## Usage Examples

### Example 1: Creating a New Feature

```bash
# Create feature branch
git checkout -b feat/add-new-endpoint

# Make your changes
# ... edit files ...

# Commit with conventional commit format
git add .
git commit -m "feat(api): add new endpoint for fetching company data"

# Push and create PR
git push origin feat/add-new-endpoint
```

**What CodeRabbit will do:**
1. ✅ Review Python code with ruff, flake8, pylint
2. ✅ Check for proper type hints and docstrings
3. ✅ Scan for security issues (gitleaks, semgrep)
4. ✅ Verify environment variable usage
5. ✅ Check FastAPI best practices
6. ✅ Generate high-level summary
7. ✅ Create sequence diagram if applicable
8. ✅ Suggest labels and reviewers

### Example 2: Adding a React Component

```bash
# Create feature branch
git checkout -b feat/add-dashboard-component

# Make your changes
# ... create new component in frontend ...

# Commit with conventional commit format
git add .
git commit -m "feat(frontend): add new dashboard component with statistics"

# Push and create PR
git push origin feat/add-dashboard-component
```

**What CodeRabbit will do:**
1. ✅ Review TypeScript code with eslint, biome
2. ✅ Check component structure and props typing
3. ✅ Verify accessibility (a11y) best practices
4. ✅ Check Tailwind CSS usage
5. ✅ Verify Next.js App Router patterns
6. ✅ Suggest tests if needed
7. ✅ Generate component summary

### Example 3: Database Migration

```bash
# Create feature branch
git checkout -b feat/add-user-preferences-table

# Create migration file
# ... add new migration file to backend/supabase/migrations/ ...

# Commit with conventional commit format
git add .
git commit -m "feat(db): add user_preferences table with migration file"

# Push and create PR
git push origin feat/add-user-preferences-table
```

**What CodeRabbit will do:**
1. ✅ Run SQLFluff linter
2. ✅ Verify migration file naming convention
3. ✅ Check for backward compatibility
4. ✅ Scan SQL for security issues
5. ✅ Warn about migration strategy
6. ✅ Suggest testing approach

## Review Workflow

### Standard Workflow

```
1. Developer creates PR
   ↓
2. CodeRabbit auto-starts review
   ↓
3. Review complete (2-5 minutes)
   ↓
4. Review summary posted to PR
   ↓
5. Developer addresses issues
   ↓
6. CodeRabbit updates status
   ↓
7. All checks pass → Ready to merge
```

### Review Statuses

CodeRabbit updates the PR with several status indicators:

- **Pending**: Review in progress
- **Success**: Review complete with no issues
- **Warning**: Review complete with warnings (can merge)
- **Failure**: Review complete with errors (must fix before merge)
- **Skipped**: PR excluded by filters (e.g., draft, "wip" in title)

### Understanding Review Output

CodeRabbit provides:

1. **High-Level Summary**
   - Overview of changes
   - Key findings
   - Effort estimation

2. **File-by-File Comments**
   - Specific issues found
   - Suggested fixes
   - Best practice recommendations

3. **Walkthrough**
   - Detailed explanation of changes
   - Sequence diagrams
   - Related issues and PRs

4. **Check Status**
   - GitHub check results
   - Test coverage
   - Security scan results

## Commands Reference

Use these commands in PR comments to interact with CodeRabbit:

### Summary & Overview

```comment
@coderabbitai summary
```
Generates a concise summary of the PR changes.

```comment
@coderabbitai outline
```
Creates an outline/table of contents of the changes.

```comment
@coderabbitai walkthrough
```
Provides a detailed walkthrough of the changes.

### Diagrams & Visualization

```comment
@coderabbitai sequence-diagrams
```
Generates sequence diagrams for the code changes.

### Review Controls

```comment
@coderabbitai review
```
Requests a fresh review of the PR.

```comment
@coderabbitai ignore-all
```
Ignores all current comments (use with caution).

### Q&A

```comment
@coderabbitai faq
```
Answers questions about the PR changes.

```comment
@coderabbitai help
```
Shows available commands.

### Configuration

```comment
@coderabbitai configuration
```
Outputs the current CodeRabbit configuration as YAML.

### Chat Commands

You can also chat with CodeRabbit:

```comment
@coderabbitai
How can I improve the security of this code?
```

```comment
@coderabbitai
Can you suggest tests for this function?
```

```comment
@coderabbitai
What's the complexity of this algorithm?
```

## Customization

### Modifying the Configuration

To customize CodeRabbit's behavior, edit `.coderabbit.yaml`:

```yaml
# Example: Change profile from assertive to chill
reviews:
  profile: chill  # instead of assertive

# Example: Add custom path instruction
path_instructions:
  - path: "**/utils/*.py"
    instructions: "Review utility functions for performance and reusability"

# Example: Enable auto-assignment of reviewers
suggested_reviewers: true
auto_assign_reviewers: true
```

### Adding Custom Checks

Add custom pre-merge checks:

```yaml
pre_merge_checks:
  custom_checks:
    - mode: error
      name: "Performance check"
      instructions: "Ensure no O(n²) loops in Python code. Check for nested loops that could be optimized."
    - mode: warning
      name: "Documentation check"
      instructions: "Verify all new API endpoints have corresponding OpenAPI docs."
```

### Ignoring Files

Add patterns to skip certain files:

```yaml
reviews:
  path_filters:
    - "!vendor/**"        # Ignore vendor code
    - "!generated/**"     # Ignore generated code
    - "*.md"              # Only review markdown files
```

### Team-Specific Settings

Configure for your team:

```yaml
# Enable poem in walkthrough
poem: false

# Auto-apply labels
auto_apply_labels: true

# Set language
language: en-US

# Configure chat
chat:
  auto_reply: true
  integrations:
    jira:
      usage: enabled  # If using Jira
```

## Best Practices

### Writing PRs That Work Well with CodeRabbit

1. **Use Conventional Commits**
   ```
   feat: add new feature
   fix: bug fix
   refactor: refactor code
   docs: update documentation
   test: add tests
   chore: maintenance
   ```

2. **Write Clear PR Titles**
   - Keep under 50 characters
   - Be descriptive
   - Use conventional commit format

3. **Write Detailed PR Descriptions**
   - Explain what and why
   - Link to issues
   - Add screenshots for UI changes
   - List breaking changes

4. **Keep PRs Small**
   - Aim for < 400 lines of changes
   - Split large features into multiple PRs
   - One feature per PR

### Code Style Consistency

CodeRabbit enforces these standards:

1. **Python**
   - Google Python Style Guide
   - Type hints required
   - Docstrings for all public functions
   - Ruff for linting and formatting

2. **TypeScript**
   - Google TypeScript Style Guide
   - Strict typing
   - Interface definitions
   - ESLint rules

3. **Security**
   - No hardcoded secrets
   - Input validation required
   - SQL injection prevention
   - XSS protection in React

### Leveraging CodeRabbit's Feedback

1. **Don't Ignore Security Warnings**
   - Always fix security issues
   - Review suggestions carefully
   - Ask questions if unclear

2. **Improve Code Quality**
   - Add type hints
   - Write docstrings
   - Follow best practices
   - Add tests for new code

3. **Use Generated Code**
   - Review generated docstrings
   - Consider generated tests
   - Customize as needed

## Troubleshooting

### CodeRabbit Not Reviewing PRs

**Check:**
1. Is the GitHub App installed?
   - Go to repository Settings → Integrations
   - Verify CodeRabbit is listed

2. Is it a draft PR?
   - Draft PRs are skipped by default
   - Publish the PR to trigger review

3. Is there "wip" or "draft" in the title?
   - These are filtered out
   - Rename the PR

4. Is the base branch correct?
   - PRs to `main` are reviewed
   - Check PR settings

**Solutions:**
```bash
# Manually trigger review
@coderabbitai review
# in a PR comment
```

### Configuration Not Applied

**Check:**
1. Is `.coderabbit.yaml` in the repository root?
   ```bash
   ls -la .coderabbit.yaml
   ```

2. Is the YAML syntax valid?
   - Use a YAML validator
   - Check for proper indentation

3. Is it on the correct branch?
   - Configuration must be in the PR branch
   - Or merge to main first

**Solutions:**
```bash
# Get current configuration
@coderabbitai configuration

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.coderabbit.yaml'))"
```

### Review Taking Too Long

**Normal time:** 2-5 minutes for typical PR

**If longer:**
1. PR is very large (400+ lines)
2. Repository has many files
3. Heavy computation required

**Solutions:**
- Split large PRs
- Reduce scope
- Wait patiently

### Incorrect or Irrelevant Feedback

**Possible reasons:**
1. Configuration needs adjustment
2. Path instructions too broad
3. Context not clear

**Solutions:**
1. Refine configuration
2. Add more specific path instructions
3. Improve PR description
4. Use `@coderabbitai ignore` for specific comments

### Security Warnings on False Positives

**Check:**
1. Is it really a secret?
   - API keys in .env.example are OK
   - Test data is OK

2. Is it in the right place?
   - Environment variables should be in .env
   - Never commit actual keys

**Solutions:**
1. Add to `.gitignore` if needed
2. Move test data to test files
3. Use `@coderabbitai ignore` for false positives
4. Refine gitleaks configuration

### Questions Not Answered

Try these commands:
```comment
@coderabbitai faq
@coderabbitai help
@coderabbitai
Can you explain this security warning?
```

### Need Human Review

CodeRabbit is a tool, not a replacement for human review. It helps catch:
- Style issues
- Security problems
- Best practice violations
- Simple bugs

Human review is still needed for:
- Architecture decisions
- Business logic
- Complex integrations
- Code appropriateness

### Disable Temporarily

To pause reviews:
```yaml
# In .coderabbit.yaml
reviews:
  auto_review:
    enabled: false
```

Or add label to PR: `!review` (negative match)

### Re-enable After Disabling

```bash
# Update configuration
git commit -m "chore: re-enable coderabbit reviews"

# Or use command in PR
@coderabbitai review
```

## Support

### Getting Help

1. **CodeRabbit Documentation**
   - [https://coderabbit.ai/](https://coderabbit.ai/)
   - Configuration reference
   - Best practices guide

2. **Commands Help**
   ```comment
   @coderabbitai help
   ```

3. **Configuration Help**
   ```comment
   @coderabbitai configuration
   ```

### Reporting Issues

If you find bugs or have feature requests:

1. Check existing issues in the repository
2. Create a new issue with:
   - Configuration file (redacted)
   - PR link (if applicable)
   - Expected vs actual behavior
   - Screenshots/logs

### Learning More

- Review the configuration reference
- Check example configurations
- Read CodeRabbit's blog
- Experiment with different settings
- Share learnings with the team

## Summary

CodeRabbit provides automated, AI-powered code reviews for your project. With the configured setup:

✅ **Automatic reviews** on all PRs to main
✅ **Security scanning** for vulnerabilities
✅ **Linting** for Python and TypeScript
✅ **Custom checks** for your project
✅ **Best practice enforcement**
✅ **Code quality insights**

Start by installing the GitHub App, then create a test PR to see CodeRabbit in action. The reviews will help maintain code quality and security standards as your project grows.

For questions, use `@coderabbitai help` in any PR comment.
