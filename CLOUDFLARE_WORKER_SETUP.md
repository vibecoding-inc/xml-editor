# Cloudflare Worker Deployment Setup

This guide explains how to set up automated deployment of the XML Editor Cloudflare Worker using GitHub Actions.

## Overview

The GitHub Actions workflow automatically deploys the Cloudflare Worker when:
- Changes are pushed to the `master` branch that affect the `cloudflare-worker/` directory
- Manually triggered via workflow dispatch

The workflow supports two environments:
- **Production**: Default deployment with worker name `xml-editor-collab`
- **Staging**: Test deployment with worker name `xml-editor-collab-staging`

## Prerequisites

1. **Cloudflare Account**: You need a Cloudflare account (free tier works fine)
2. **GitHub Repository**: Admin access to configure secrets

## Setup Instructions

### 1. Create a Cloudflare API Token

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **My Profile** → **API Tokens**
3. Click **Create Token**
4. Use the **Edit Cloudflare Workers** template, or create a custom token with these permissions:
   - **Account** → **Workers Scripts** → **Edit**
   - **Account** → **Workers KV Storage** → **Edit** (optional, for future use)
   - **Account** → **Durable Objects** → **Edit**
5. Set **Account Resources** to include your account
6. Click **Continue to summary** and then **Create Token**
7. **Copy the token** - you won't be able to see it again!

### 2. Get Your Cloudflare Account ID

1. In the [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select any website/zone or go to **Workers & Pages**
3. Find your **Account ID** in the right sidebar (usually under account information)
4. Copy the Account ID

### 3. Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   | Secret Name | Value | Description |
   |-------------|-------|-------------|
   | `CLOUDFLARE_API_TOKEN` | Your API token from step 1 | Authentication for Wrangler |
   | `CLOUDFLARE_ACCOUNT_ID` | Your Account ID from step 2 | Identifies your Cloudflare account |

### 4. Verify Setup

After configuring the secrets, the workflow will automatically run when:
- You push changes to the `cloudflare-worker/` directory on the `master` branch
- You manually trigger it from the Actions tab

## Manual Deployment

You can manually trigger a deployment from the GitHub Actions interface:

1. Go to **Actions** tab in your repository
2. Select **Deploy Cloudflare Worker** workflow
3. Click **Run workflow**
4. Choose the environment:
   - **production** (default): Deploys as `xml-editor-collab`
   - **staging**: Deploys as `xml-editor-collab-staging`
5. Click **Run workflow**

## Configuration

### Worker Name

The worker name is defined in `cloudflare-worker/wrangler.toml`:
```toml
name = "xml-editor-collab"
```

For staging deployments, the workflow automatically appends `-staging` to the name.

### Deployment Triggers

The workflow is configured in `.github/workflows/deploy-cloudflare-worker.yml`:
- **Automatic**: On push to `master` branch with changes to `cloudflare-worker/**`
- **Manual**: Via workflow dispatch with environment selection

### Customization

To customize the deployment:

1. **Change worker name**: Edit `name` in `cloudflare-worker/wrangler.toml`
2. **Add more environments**: Modify the workflow file to add additional environment options
3. **Custom routes**: Add routes in `wrangler.toml` if you have a custom domain
4. **Environment variables**: Add them to `wrangler.toml` under `[vars]` section

## Accessing Your Deployed Worker

After deployment, your worker will be available at:
- **Production**: `https://xml-editor-collab.<your-subdomain>.workers.dev`
- **Staging**: `https://xml-editor-collab-staging.<your-subdomain>.workers.dev`

You can find the exact URL:
1. In the GitHub Actions workflow run output
2. In your [Cloudflare Dashboard](https://dash.cloudflare.com/) under **Workers & Pages**

## Using the Worker

### WebSocket Connection

Connect to your worker using WebSocket from the XML Editor:

```javascript
const ws = new WebSocket('wss://xml-editor-collab.<your-subdomain>.workers.dev/room-name');
```

### Room Names

Rooms are identified by the URL path:
- `wss://your-worker.workers.dev/document-1` → Room: "document-1"
- `wss://your-worker.workers.dev/project/file` → Room: "project/file"

## Troubleshooting

### Deployment Fails with "Authentication error"

**Solution**: Verify that `CLOUDFLARE_API_TOKEN` is correctly set in GitHub secrets and has the necessary permissions.

### Deployment Fails with "Account not found"

**Solution**: Verify that `CLOUDFLARE_ACCOUNT_ID` is correctly set and matches your Cloudflare account.

### Worker Not Responding

**Solution**:
1. Check the deployment logs in GitHub Actions
2. View real-time logs: `wrangler tail xml-editor-collab` (requires local Wrangler setup)
3. Check Cloudflare Dashboard → Workers & Pages → Your Worker → Logs

### Durable Objects Not Working

**Solution**:
1. Ensure Durable Objects are enabled for your Cloudflare account
2. Verify the migrations in `wrangler.toml` are correct
3. Check that the binding name `DOC_ROOM` matches in both `wrangler.toml` and `src/index.js`

### Workflow Doesn't Trigger Automatically

**Solution**:
1. Ensure you're pushing to the `master` branch
2. Verify that changes are in the `cloudflare-worker/` directory
3. Check the workflow file syntax in `.github/workflows/deploy-cloudflare-worker.yml`

## Security Notes

### API Token Security

⚠️ **Never commit your API token to the repository!** Always use GitHub Secrets.

### Worker Security

The current worker implementation has no authentication. For production use, consider:
- Adding API key authentication
- Implementing per-room passwords
- Using Cloudflare Access for authentication
- Rate limiting connections per IP

## Cost

Cloudflare Workers and Durable Objects have generous free tiers:
- **Workers**: 100,000 requests/day
- **Durable Objects**: 1 million requests/month
- **Workers KV**: 100,000 reads/day, 1,000 writes/day

For typical use (small teams, occasional collaboration), the free tier should be sufficient.

## Advanced: Custom Domains

To use a custom domain:

1. Add your domain to Cloudflare
2. Add routes in `wrangler.toml`:
   ```toml
   routes = [
     { pattern = "collab.example.com/*", zone_name = "example.com" }
   ]
   ```
3. Redeploy the worker

## Local Development

To test changes locally before deployment:

```bash
cd cloudflare-worker
npm install -g wrangler  # If not already installed
wrangler login           # Authenticate with Cloudflare
wrangler dev             # Start local development server
```

The local server will be available at `http://localhost:8787` with hot reloading.

## Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)
- [Durable Objects Documentation](https://developers.cloudflare.com/durable-objects/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

If you encounter issues not covered in this guide:
1. Check the [Cloudflare Community](https://community.cloudflare.com/)
2. Review [GitHub Actions logs](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
3. Open an issue in the repository
