# Enable HTTPS for GitHub Pages

## Current Issue
- SSL certificate is for `*.github.io` but domain is `singh.inquiry.institute`
- HTTPS enforcement is disabled
- This causes SSL warnings in browsers

## Solution

### Option 1: Enable via GitHub Dashboard (Recommended)
1. Go to: https://github.com/InquiryInstitute/singh.inquiry.institute/settings/pages
2. Under "Custom domain", check **"Enforce HTTPS"**
3. Save changes
4. Wait 5-10 minutes for GitHub to provision SSL certificate

### Option 2: Wait for Automatic Provisioning
GitHub Pages automatically provisions SSL certificates for verified custom domains, but it can take up to 24 hours after domain verification.

## Current Status
- ✅ DNS: Correctly pointing to `inquiryinstitute.github.io`
- ✅ Domain: Verified (`protected_domain_state: "verified"`)
- ⚠️ HTTPS: Not enforced (needs manual enable)
- ⚠️ SSL: Certificate not yet provisioned for custom domain

## Verification Commands
```bash
# Check HTTPS enforcement
gh api repos/InquiryInstitute/singh.inquiry.institute/pages | jq '.https_enforced'

# Test HTTP (should work)
curl -I http://singh.inquiry.institute

# Test HTTPS (will work after certificate is provisioned)
curl -I https://singh.inquiry.institute
```

## After Enabling HTTPS
1. GitHub will provision a Let's Encrypt certificate
2. This usually takes 5-10 minutes
3. Once provisioned, HTTPS will work without warnings
4. HTTP will automatically redirect to HTTPS
