# Enable GitHub Pages - Manual Setup Required

## Issue
The workflow is failing because GitHub Pages is not enabled in the repository settings. This must be done manually.

## Error Message
```
Get Pages site failed. Please verify that the repository has Pages enabled and configured to build using GitHub Actions
```

## Solution: Enable Pages Manually

### Step 1: Go to Repository Settings
1. Navigate to: https://github.com/InquiryInstitute/singh.inquiry.institute/settings/pages

### Step 2: Configure Pages
1. Under **"Source"**, select: **"GitHub Actions"** (NOT "Deploy from a branch")
2. Under **"Custom domain"**, enter: `singh.inquiry.institute`
3. Check **"Enforce HTTPS"** (recommended)
4. Click **"Save"**

### Step 3: Verify
After saving, the workflow should automatically run again, or you can:
1. Go to Actions tab: https://github.com/InquiryInstitute/singh.inquiry.institute/actions
2. Click "Deploy GitHub Pages" workflow
3. Click "Run workflow" → "Run workflow"

## Alternative: Enable via GitHub CLI

If you have admin access, you can try:

```bash
# Check current Pages status
gh api repos/InquiryInstitute/singh.inquiry.institute/pages

# Note: Pages must be enabled via web UI - API doesn't support enabling
```

## After Enabling

Once Pages is enabled:
1. The workflow will run automatically on next push
2. Site will be available at: http://singh.inquiry.institute/
3. HTTPS will be enabled automatically (may take up to 24 hours)

## Current Status

- ✅ Workflow file is correct
- ✅ All required files exist (index.html, .nojekyll, CNAME)
- ❌ Pages not enabled in repository settings
- ⏳ Waiting for manual enablement
