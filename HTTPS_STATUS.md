# HTTPS Status

## Current Situation

The GitHub API requires the SSL certificate to be provisioned **before** HTTPS enforcement can be enabled. The error "The certificate does not exist yet" indicates that GitHub hasn't automatically provisioned the certificate for the custom domain yet.

## What Happens

1. Domain is verified ✅ (`protected_domain_state: "verified"`)
2. DNS is correct ✅ (CNAME to `inquiryinstitute.github.io`)
3. SSL certificate: **Not yet provisioned** ⏳
4. HTTPS enforcement: **Cannot enable until certificate exists** ⏳

## Solution

GitHub Pages automatically provisions SSL certificates for verified custom domains, but this can take:
- **5-10 minutes** (typical)
- **Up to 24 hours** (in some cases)

Once the certificate is provisioned, you can enable HTTPS enforcement via:
```bash
gh api repos/InquiryInstitute/singh.inquiry.institute/pages -X PUT \
  -F https_enforced:=true \
  -F cname=singh.inquiry.institute \
  -F build_type=workflow \
  -F 'source[branch]=main' \
  -F 'source[path]=/'
```

## Check Status

```bash
# Check if certificate is ready
gh api repos/InquiryInstitute/singh.inquiry.institute/pages | jq '.https_enforced'

# Test HTTPS
curl -I https://singh.inquiry.institute
```

## Alternative: Enable via Dashboard

If the certificate is provisioned but API still fails:
1. Go to: https://github.com/InquiryInstitute/singh.inquiry.institute/settings/pages
2. Check "Enforce HTTPS"
3. Save
