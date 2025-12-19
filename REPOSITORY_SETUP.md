# Repository Setup Instructions

## Update GitHub Repository Name

The repository should be renamed from `SiNGH` to `singh.inquiry.institute` on GitHub.

### Steps:

1. Go to your repository on GitHub: `https://github.com/InquiryInstitute/SiNGH`
2. Navigate to **Settings** → **General**
3. Scroll down to the "Repository name" section
4. Change the name from `SiNGH` to `singh.inquiry.institute`
5. Click "Rename"

### Update Local Git Remote

After renaming on GitHub, update your local repository's remote URL:

```bash
git remote set-url origin git@github.com:InquiryInstitute/singh.inquiry.institute.git
```

Verify the change:
```bash
git remote -v
```

## GitHub Pages Configuration

GitHub Pages is configured via the workflow file at `.github/workflows/pages.yml`. 

### To enable GitHub Pages:

1. Go to repository **Settings** → **Pages**
2. Under "Source", select **GitHub Actions** (not "Deploy from a branch")
3. The workflow will automatically deploy when you push to the `main` branch

### Custom Domain Setup:

1. In **Settings** → **Pages**, enter your custom domain: `singh.inquiry.institute`
2. Check "Enforce HTTPS"
3. Follow the instructions in [AWS_ROUTE53_SETUP.md](./AWS_ROUTE53_SETUP.md) to configure DNS

## Next Steps

1. ✅ Repository renamed to `singh.inquiry.institute`
2. ✅ GitHub Pages workflow configured
3. ⏳ Enable GitHub Pages in repository settings
4. ⏳ Configure AWS Route 53 (see [AWS_ROUTE53_SETUP.md](./AWS_ROUTE53_SETUP.md))
5. ⏳ Add your project content
