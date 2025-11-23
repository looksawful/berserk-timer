# 🚀 RELEASE PREPARATION CHECKLIST

**Project:** berserk-timer
**Target Version:** 0.1.3-beta
**Date:** November 23, 2025

---

## ✅ COMPLETED

### 1. `.gitignore` Updated
- ✅ Added `INTERNALS.md` (personal notes)
- ✅ Added `.pytest_cache/`, `.coverage`, `htmlcov/`
- ✅ Added `*.pkf`, `desktop.ini` (OS files)
- ✅ Added `*.whl`, `*.egg-info/` (build artifacts)
- ✅ Extended Python bytecode patterns

### 2. Configuration Template Created
- ✅ Created `config.example.json` (clean template)
- ✅ User's `config.json` is gitignored (stays private)

### 3. Documentation Updated
- ✅ Updated `README.md`:
  - New installation instructions (Windows/Linux/MacOS)
  - Usage examples with all CLI flags
  - Interactive commands table
  - Development setup guide
  - Contributing guidelines
  - Commit message convention
- ✅ Created `CHANGELOG.md`:
  - Version history
  - Detailed 0.1.3-beta changes
  - Planned features

### 4. Files Status
```
✅ .gitignore          - Updated
✅ config.example.json - Created
✅ README.md           - Updated
✅ CHANGELOG.md        - Created
🔄 config.json         - Gitignored (user data)
🔄 logs/               - Gitignored (user data)
🔄 venv/               - Gitignored
🔄 __pycache__/        - Gitignored
```

---

## 📋 PRE-COMMIT CHECKLIST

### Before Committing

- [ ] **Check git status:**
  ```bash
  git status
  ```

- [ ] **Review changes:**
  ```bash
  git diff
  ```

- [ ] **Verify gitignore works:**
  ```bash
  # Should NOT show: config.json, logs/, venv/, __pycache__/
  git status --ignored
  ```

- [ ] **Run tests:**
  ```bash
  pytest tests/ -v
  ```

- [ ] **Check test coverage:**
  ```bash
  pytest tests/ --cov=src
  # Target: >70% coverage
  ```

---

## 🎯 GIT COMMANDS FOR RELEASE

### Step 1: Stage Release Files

```bash
# Navigate to project
cd a:\Users\awful\Documents\CODE\PETS\PROD\berserk-timer

# Stage only release-related files
git add .gitignore
git add config.example.json
git add README.md
git add CHANGELOG.md

# Verify what will be committed (should NOT include config.json, logs/, venv/)
git status
```

### Step 2: Create Release Commit

```bash
# Commit with descriptive message
git commit -m "release: prepare v0.1.3-beta

- Updated .gitignore (add INTERNALS.md, testing artifacts, OS files)
- Created config.example.json template for users
- Updated README.md with installation, usage, and contribution guides
- Created CHANGELOG.md documenting version history

Changes:
- Added safe_word config option
- Fixed message sanitization
- Fixed premature timer end logging
- Enhanced test coverage

Files: .gitignore, config.example.json, README.md, CHANGELOG.md"
```

### Step 3: Verify Commit

```bash
# View last commit
git log -1 --stat

# Check what's NOT staged (should see config.json, logs/, etc.)
git status

# Double-check gitignored files aren't tracked
git ls-files --ignored --exclude-standard
```

### Step 4: Push to GitHub

```bash
# Push to dev branch first (safer)
git push origin dev

# If everything looks good, merge to main
git checkout main
git merge dev
git push origin main
```

---

## 🧪 POST-COMMIT TESTING PLAN

### Local Testing

1. **Clone fresh copy:**
   ```bash
   cd /tmp  # or another location
   git clone https://github.com/looksawful/berserk-timer.git test-install
   cd test-install
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create config:**
   ```bash
   cp config.example.json config.json
   ```

4. **Run timer:**
   ```bash
   # Test basic timer
   python -m src.main 1

   # Test preset
   python -m src.main -t

   # Test witness mode
   python -m src.main -w -t
   ```

5. **Verify logs created:**
   ```bash
   ls logs/
   # Should see witness_log_YYYY-MM-DD.txt after witness mode
   ```

6. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

---

## 🏷️ CREATE GITHUB RELEASE

### After Testing, Create Release on GitHub

1. **Go to:** https://github.com/looksawful/berserk-timer/releases

2. **Click:** "Create a new release"

3. **Fill in:**
   - **Tag version:** `v0.1.3-beta`
   - **Target:** `main` branch
   - **Release title:** `Berserk Timer v0.1.3-beta`
   - **Description:**

```markdown
## 🎉 Berserk Timer v0.1.3-beta

Productivity timer with witness accountability mode.

### ✨ What's New

- **Safe Word Configuration** - Skip witness mode prompts with customizable keyword
- **Message Sanitization** - Automatic cleanup of empty log entries
- **Improved Logging** - Timer completion only logs when naturally finished
- **Better Defaults** - Test preset now 1 minute (more realistic)
- **Enhanced Tests** - Added config validation and sanitization tests

### 📦 Installation

```bash
git clone https://github.com/looksawful/berserk-timer.git
cd berserk-timer
pip install -r requirements.txt
cp config.example.json config.json
python -m src.main 25
```

### 📖 Documentation

See [README.md](README.md) for full usage guide.

### 🐛 Bug Fixes

- Fixed premature "Timer ended" logging
- Fixed empty messages in witness logs
- Fixed missing safe_word in default config

### 📝 Changed Files

- `src/config_manager.py`
- `src/main.py`
- `tests/test_config.py`
- `.gitignore`
- `README.md` (complete rewrite)
- `CHANGELOG.md` (new)
- `config.example.json` (new)

### 🔗 Full Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

4. **Publish release**

---

## ⚠️ TROUBLESHOOTING

### If config.json appears in git status:

```bash
# Remove from staging
git reset HEAD config.json

# Verify gitignore
cat .gitignore | grep config.json

# If needed, remove from git tracking
git rm --cached config.json
git commit -m "chore: remove config.json from tracking"
```

### If logs/ appears in git status:

```bash
# Remove from git
git rm --cached -r logs/
git commit -m "chore: remove logs from tracking"
```

### If venv/ appears:

```bash
# Ensure .gitignore has venv/
echo "venv/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore venv directory"
```

---

## 📊 FINAL CHECKLIST BEFORE RELEASE

- [ ] All tests pass locally
- [ ] README.md is accurate
- [ ] CHANGELOG.md is up to date
- [ ] config.example.json works as template
- [ ] .gitignore prevents private files from committing
- [ ] Fresh install works from GitHub
- [ ] All features documented
- [ ] No sensitive data in repository
- [ ] Commit message follows convention
- [ ] Changes pushed to main branch
- [ ] GitHub release created with tag

---

## 🎯 NEXT STEPS AFTER RELEASE

1. **Update Documentation:**
   - [ ] Update `Docs/berserk-timer-TODO.md`
   - [ ] Update `Docs/PROJECT_STATUS.md`
   - [ ] Mark v0.1.3-beta as released

2. **Start Next Development Cycle:**
   - [ ] Create branch `dev` for next version
   - [ ] Plan v0.1.4 features
   - [ ] Update ROADMAP

3. **Monitor:**
   - [ ] Check for issues on GitHub
   - [ ] Respond to feedback
   - [ ] Fix critical bugs in hotfix branches

---

**Ready to commit? Run Step 1 commands above! 🚀**
