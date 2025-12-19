# GitHub Pages Troubleshooting

## Current Status: 404 Error

If http://singh.inquiry.institute/ is showing 404, check the following:

## 1. Verify Changes Are Pushed

```bash
git push origin main
```

## 2. Check GitHub Actions

1. Go to: https://github.com/InquiryInstitute/singh.inquiry.institute/actions
2. Look for "Deploy GitHub Pages" workflow
3. Check if it's running or has errors
4. If it failed, check the logs

## 3. Verify GitHub Pages Settings

1. Go to repository Settings → Pages
2. Source should be: **GitHub Actions** (not "Deploy from a branch")
3. Custom domain should be: `singh.inquiry.institute`
4. "Enforce HTTPS" should be checked

## 4. Check Workflow File

The workflow should:
- Build static files to `_site/` directory
- Include `index.html`
- Include `.nojekyll` file
- Include `CNAME` file

## 5. Manual Deployment Test

If the workflow isn't working, you can manually trigger it:

1. Go to Actions tab
2. Select "Deploy GitHub Pages" workflow
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

## 6. Verify Files Are Correct

The repository should have:
- `index.html` in root
- `.nojekyll` in root
- `CNAME` with content: `singh.inquiry.institute`
- `.github/workflows/pages.yml` workflow file

## 7. Check DNS

If GitHub Pages is working but domain isn't:
- Verify Route 53 CNAME record: `singh` → `inquiryinstitute.github.io`
- Check DNS propagation: https://dnschecker.org/#CNAME/singh.inquiry.institute
- Wait for DNS propagation (can take up to 48 hours)

## 8. Common Issues

### Issue: Workflow not running
**Solution**: Check if GitHub Actions is enabled in repository settings

### Issue: Workflow fails
**Solution**: Check workflow logs for errors, ensure all files exist

### Issue: Site loads but shows 404
**Solution**: Verify `index.html` is in `_site/` directory after build

### Issue: Custom domain not working
**Solution**: 
- Verify CNAME file exists and is correct
- Check GitHub Pages settings show custom domain
- Wait for SSL certificate (up to 24 hours)

## Quick Fix Commands

```bash
# Push latest changes
git push origin main

# Verify files exist
ls -la index.html .nojekyll CNAME

# Check workflow file
cat .github/workflows/pages.yml
```
