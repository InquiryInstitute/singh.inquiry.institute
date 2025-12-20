# Pre-Push Hook

## Overview

A git pre-push hook has been installed that automatically builds the Next.js application before allowing a push.

## What It Does

1. **Checks for Next.js project** - Looks for `package.json`
2. **Installs dependencies** - Runs `npm install` if `node_modules` doesn't exist
3. **Builds the app** - Runs `npm run build`
4. **Blocks push on failure** - If build fails, the push is aborted

## Usage

The hook runs automatically when you run `git push`. You don't need to do anything special.

```bash
git push origin main
# Hook automatically runs: npm install && npm run build
# Push only proceeds if build succeeds
```

## Bypassing the Hook

If you need to push without building (not recommended):

```bash
git push --no-verify origin main
```

## Setting Up Next.js

To use this hook with Next.js:

1. **Initialize Next.js** (if not already done):
   ```bash
   npx create-next-app@latest .
   ```

2. **Ensure package.json has build script**:
   ```json
   {
     "scripts": {
       "build": "next build"
     }
   }
   ```

3. **The hook will automatically run builds on push**

## Current Status

- ✅ Pre-push hook installed: `.git/hooks/pre-push`
- ✅ Hook is executable
- ⏳ Waiting for Next.js setup (currently static HTML site)

## Notes

- The hook only runs if `package.json` exists
- If no Next.js project is detected, the hook passes silently
- Build failures prevent the push from completing
