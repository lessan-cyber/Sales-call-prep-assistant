# CodeRabbit Setup Verification Checklist

Use this checklist to verify that CodeRabbit is properly configured and working for your repository.

## ✅ Pre-Installation Checklist

- [ ] Repository is on GitHub
- [ ] You have admin access to the repository
- [ ] You have a GitHub account
- [ ] `.coderabbit.yaml` file exists in repository root
- [ ] `.coderabbit.yaml` has valid YAML syntax

## ✅ Installation Steps

### Step 1: Install CodeRabbit GitHub App
- [ ] Visit https://coderabbit.ai/
- [ ] Click "Get Started" or "Install App"
- [ ] Sign in with GitHub
- [ ] Select your repository: `Sales-call-prep-assistant`
- [ ] Grant permissions:
  - [ ] Contents (Read)
  - [ ] Pull requests (Read and Write)
  - [ ] Checks (Write)
  - [ ] Discussions (Read)

### Step 2: Verify Installation
- [ ] Go to repository Settings → Integrations
- [ ] CodeRabbit is listed in installed apps
- [ ] App is enabled for the repository

## ✅ Configuration Validation

### Verify Configuration File
```bash
# Check file exists
ls -la .coderabbit.yaml
```

**Expected**: File exists

### Validate YAML Syntax
```bash
# Using Python
python3 -c "import yaml; yaml.safe_load(open('.coderabbit.yaml'))"
```

**Expected**: No errors, outputs parsed YAML

### Check Key Settings
Open `.coderabbit.yaml` and verify:

- [ ] `language: en-US` is set
- [ ] `profile: assertive` (or preferred profile)
- [ ] `auto_review.enabled: true`
- [ ] Tools are enabled:
  - [ ] ruff (for Python)
  - [ ] eslint (for TypeScript)
  - [ ] gitleaks (security)
  - [ ] semgrep (security)

## ✅ Testing the Integration

### Test 1: Create a Test Branch
```bash
git checkout -b test/coderabbit-verification
```

**Status**: [ ]

### Test 2: Make a Simple Change

Create a test Python file:
```bash
cat > test_file.py << 'EOF'
"""Test file for CodeRabbit verification."""


def hello_world() -> str:
    """Return a greeting message."""
    return "Hello, World!"
EOF
```

Or make a simple change to an existing file (e.g., add a blank line)

**Status**: [ ]

### Test 3: Commit and Push
```bash
git add .
git commit -m "test: verify coderabbit integration"
git push origin test/coderabbit-verification
```

**Status**: [ ]

### Test 4: Create Pull Request
1. Go to GitHub repository
2. Click "Create Pull Request"
3. Select base: `main`, compare: `test/coderabbit-verification`
4. Add title: `test: verify coderabbit integration`
5. Click "Create Pull Request"

**Status**: [ ]

### Test 5: Wait for CodeRabbit Review

**Timeline**: 2-5 minutes

**What to check**:
- [ ] CodeRabbit adds a review comment
- [ ] Review summary appears in PR description
- [ ] GitHub check status shows CodeRabbit
- [ ] Walkthrough comment is posted

**Status**: [ ]

### Test 6: Verify Review Content

Check that CodeRabbit provided:

- [ ] High-level summary
- [ ] File-specific comments (if applicable)
- [ ] Check status (success/warning/failure)
- [ ] Tool results (ruff, eslint, etc.)
- [ ] Security scan results

**Status**: [ ]

## ✅ Feature Testing

### Test Auto-Commands
In a PR comment, try:
```comment
@coderabbitai summary
```
**Expected**: CodeRabbit generates a summary

**Status**: [ ]

```comment
@coderabbitai outline
```
**Expected**: CodeRabbit creates an outline

**Status**: [ ]

```comment
@coderabbitai faq
```
**Expected**: CodeRabbit shows FAQ

**Status**: [ ]

### Test Custom Path Instructions
Create PR with:
- Python file changes → Should mention Google Python Style
- TypeScript file changes → Should mention Google TypeScript Style
- FastAPI router changes → Should mention API best practices

**Status**: [ ]

### Test Security Scanning
Add test code with potential issue:
```python
# Test in a Python file
API_KEY = "sk-1234567890abcdef"  # Looks like a secret
```

**Expected**: gitleaks should detect this

**Status**: [ ]

## ✅ Verification Complete

If all tests pass:

- [ ] ✅ CodeRabbit is installed
- [ ] ✅ Configuration is valid
- [ ] ✅ Auto-review works
- [ ] ✅ Commands respond
- [ ] ✅ Security scanning works
- [ ] ✅ Tools are integrated

## ❌ Troubleshooting Failed Tests

### CodeRabbit Not Reviewing PR

**Check**:
1. Is it a draft PR? → Publish it
2. Is "wip" or "draft" in title? → Rename
3. Is base branch `main`? → Change if needed

**Solution**:
```comment
@coderabbitai review
```

**Status**: [ ]

### Configuration Not Applied

**Check**:
1. Is `.coderabbit.yaml` in PR branch? → Merge to main first
2. Is YAML valid? → Validate syntax
3. File in repository root? → Move if needed

**Solution**:
```comment
@coderabbitai configuration
```

**Status**: [ ]

### Commands Not Responding

**Possible reasons**:
- App not properly installed
- Permissions insufficient
- Service temporarily down

**Solution**:
1. Reinstall app
2. Check permissions
3. Try again in 5 minutes

**Status**: [ ]

### Security Scanner False Positives

**Example**: API key in `.env.example`

**Expected**: Should NOT trigger (legitimate example keys)

**If triggered**:
- Use `@coderabbitai ignore` for specific comment
- Review gitleaks configuration
- Ensure example keys are in `.gitignore` only

**Status**: [ ]

## 📝 Test Report

Copy this section and fill it out after testing:

```
Date: ___________
Tester: __________

✅ Installation Steps Completed: [Yes/No]
✅ Configuration Valid: [Yes/No]
✅ Test PR Created: [Yes/No]
✅ Review Received: [Yes/No]
✅ Commands Working: [Yes/No]
✅ Security Scanning: [Yes/No]

Overall Status: [Success/Failed]

Notes:
-
-
-

Issues Encountered:
-
-

Solutions Applied:
-
-
```

## 🎯 Next Steps

After verification is complete:

1. **Clean up test branch**
   ```bash
   git checkout main
   git branch -D test/coderabbit-verification
   ```

2. **Update team documentation**
   - Share integration guide
   - Schedule team training
   - Add to onboarding docs

3. **Start using CodeRabbit**
   - Create feature branches
   - Write conventional commits
   - Let CodeRabbit review PRs
   - Respond to feedback

4. **Monitor and adjust**
   - Review feedback quality
   - Adjust configuration as needed
   - Collect team feedback

## 📚 Resources

- **Integration Guide**: `docs/CodeRabbit-Integration-Guide.md`
- **Configuration**: `.coderabbit.yaml`
- **Project Docs**: `CLAUDE.md` (includes CodeRabbit section)
- **CodeRabbit Docs**: https://coderabbit.ai/

## 💡 Tips

1. **Keep PRs small** - Faster reviews
2. **Use conventional commits** - Better summaries
3. **Write clear descriptions** - Better context
4. **Don't ignore security warnings** - Always fix
5. **Ask questions** - Use `@coderabbitai` in comments

---

**Verification Complete!** ✅

Your CodeRabbit integration is ready for use.
