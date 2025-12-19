# GitHub Pages 404 Fix

## Issue
The site at http://singh.inquiry.institute/ was returning 404.

## Root Cause
The GitHub Pages workflow was configured to use Jekyll, but the repository only contains static HTML files. Jekyll was trying to process the site and failing.

## Solution
1. **Updated workflow** (`.github/workflows/pages.yml`):
   - Changed from Jekyll build to static file deployment
   - Creates `_site` directory and copies static files
   - Ensures `.nojekyll` and `CNAME` are included

2. **Added `.nojekyll` file**:
   - Tells GitHub Pages to skip Jekyll processing
   - Must be in the root and copied to `_site/`

## What Changed
- Workflow now builds static site manually
- Copies `index.html`, `.nojekyll`, `CNAME`, and markdown files to `_site/`
- Deploys static files directly

## Next Steps
1. Push changes to trigger workflow
2. Wait for GitHub Actions to deploy (usually 1-2 minutes)
3. Verify site is accessible at http://singh.inquiry.institute/

## Verification
After deployment, check:
- Site loads at http://singh.inquiry.institute/
- Custom domain is working (HTTPS should be enabled)
- All links work correctly
