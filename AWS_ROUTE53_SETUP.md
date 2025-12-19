# AWS Route 53 Setup for singh.inquiry.institute

This guide provides step-by-step instructions for configuring AWS Route 53 to point your custom domain to GitHub Pages.

## Prerequisites

- AWS account with Route 53 access
- Domain name registered (or transferred to Route 53)
- GitHub Pages site deployed and accessible

## Step 1: Get GitHub Pages IP Addresses

GitHub Pages uses the following IP addresses:
- `185.199.108.153`
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

Alternatively, you can use GitHub's CNAME record:
- `inquiryinstitute.github.io` (for user/organization pages)
- Or the specific repository subdomain if using project pages

## Step 2: Create Hosted Zone in Route 53

1. Log in to AWS Console and navigate to Route 53
2. Click "Hosted zones" in the left sidebar
3. Click "Create hosted zone"
4. Enter your domain name: `singh.inquiry.institute` (or `inquiry.institute` if managing the parent domain)
5. Choose "Public hosted zone"
6. Click "Create hosted zone"

## Step 3: Configure DNS Records

### Option A: Using A Records (for apex domain)

If you want `singh.inquiry.institute` to point directly to GitHub Pages:

1. In your hosted zone, click "Create record"
2. Configure the record:
   - **Record name**: Leave blank (for apex) or enter subdomain
   - **Record type**: `A`
   - **Value**: Enter one of the GitHub Pages IP addresses
   - **TTL**: `300` (5 minutes)
3. Create 3 additional A records with the same configuration but different IP addresses (one for each of the 4 IPs)

### Option B: Using CNAME (Recommended for subdomains)

If you want `singh.inquiry.institute` as a subdomain:

1. In your hosted zone, click "Create record"
2. Configure the record:
   - **Record name**: `singh` (or leave blank for apex)
   - **Record type**: `CNAME`
   - **Value**: `inquiryinstitute.github.io` (or your GitHub Pages URL)
   - **TTL**: `300` (5 minutes)
3. Click "Create records"

**Note**: CNAME records cannot be used for apex domains (e.g., `inquiry.institute`). For apex domains, use A records or ALIAS records.

### Option C: Using ALIAS Record (Best for apex domains)

If managing the apex domain `inquiry.institute`:

1. Click "Create record"
2. Configure the record:
   - **Record name**: Leave blank
   - **Record type**: `A - Routes traffic to an IPv4 address and some AWS resources`
   - **Alias**: Enable
   - **Route traffic to**: Select "Alias to another record in this hosted zone" or use CloudFront distribution if applicable
   - For GitHub Pages, you'll need to use A records with IP addresses (see Option A)

## Step 4: Configure GitHub Pages Custom Domain

1. Go to your GitHub repository: `InquiryInstitute/singh.inquiry.institute`
2. Navigate to **Settings** → **Pages**
3. Under "Custom domain", enter: `singh.inquiry.institute`
4. Check "Enforce HTTPS" (recommended)
5. GitHub will automatically create a CNAME file in your repository

## Step 5: Update Name Servers (if domain is registered elsewhere)

If your domain is registered with a different registrar:

1. In Route 53, go to your hosted zone
2. Note the 4 name server addresses (e.g., `ns-123.awsdns-12.com`)
3. Go to your domain registrar's control panel
4. Update the name servers to the Route 53 name servers provided

## Step 6: Verify DNS Propagation

Wait for DNS propagation (can take up to 48 hours, usually much faster):

```bash
# Check A records
dig singh.inquiry.institute A

# Check CNAME records
dig singh.inquiry.institute CNAME

# Check name servers
dig singh.inquiry.institute NS
```

Or use online tools:
- https://dnschecker.org
- https://www.whatsmydns.net

## Step 7: SSL Certificate (HTTPS)

GitHub Pages automatically provisions SSL certificates via Let's Encrypt for custom domains. Once DNS is properly configured and GitHub detects the custom domain, HTTPS will be enabled automatically.

## Troubleshooting

### Domain not resolving
- Verify DNS records are correct
- Check name servers are updated at registrar
- Wait for DNS propagation (up to 48 hours)

### HTTPS not working
- Ensure "Enforce HTTPS" is enabled in GitHub Pages settings
- Wait for Let's Encrypt certificate provisioning (can take up to 24 hours)
- Verify DNS is correctly pointing to GitHub Pages

### CNAME conflicts
- If using apex domain, you cannot use CNAME. Use A records instead.
- Ensure no conflicting records exist in your DNS zone

## Additional Resources

- [GitHub Pages Custom Domain Documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [AWS Route 53 Documentation](https://docs.aws.amazon.com/route53/)
- [DNS Propagation Checker](https://dnschecker.org)
