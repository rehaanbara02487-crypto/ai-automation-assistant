# GitHub Setup

Do this only after the localhost app works.

## 1. Initialize Git

```powershell
git init
git status
```

## 2. Confirm Clean Ignore Rules

These should not be committed:

- `.env`
- `.env.local`
- `node_modules/`
- `.next/`
- `.venv/`
- `__pycache__/`
- `*.log`

## 3. First Commit

```powershell
git add .
git commit -m "Initial BeingAI Assistant MVP"
```

## 4. Create GitHub Repo

Create an empty GitHub repository, then connect it:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/beingai-assistant.git
git push -u origin main
```

## Suggested Commit Style

Use small, readable commits:

- `Create local-first app scaffold`
- `Add automation planner and validation`
- `Add Supabase schema`
- `Add local testing workflow`
- `Prepare deployment docs`

