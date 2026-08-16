# OIDC federation for the pre-provisioned UAMI

GitHub Actions will authenticate to Azure using **OpenID Connect (OIDC)** — no client secret, no service-principal password. This document walks you through creating the **federated credential** on the pre-provisioned User-Assigned Managed Identity (UAMI) so Entra ID trusts a specific branch / job in your fork of this repo.

## How it works

1. When the workflow runs, GitHub Actions mints a short-lived JWT that describes the running workflow — its repository owner, repository name, ref, and job environment. The issuer is `https://token.actions.githubusercontent.com`.
2. `azure/login@v2` sends that JWT to Entra ID and asks for an access token for the UAMI's client ID.
3. Entra ID looks up the federated credentials on the UAMI. If any of them matches the JWT's `sub` (subject) claim, the login is allowed — no secret exchange, no rotation.
4. The workflow gets an access token that Azure treats as the UAMI, so anything the UAMI has RBAC for (Contributor on the resource group, in this lab) is now available to the workflow.

## Prerequisites

- The UAMI's **client ID** (the lab hands this to you as `AZURE_CLIENT_ID`).
- The Azure tenant ID (`AZURE_TENANT_ID`).
- The subscription ID (`AZURE_SUBSCRIPTION_ID`).
- Your GitHub username / org that owns the fork.
- The name of your fork (usually still `smu-starter-projects`).
- The branch the workflow will run on (`main`).

## Step 1 — Set the three GitHub Actions secrets

In your fork on github.com:

**Settings → Secrets and variables → Actions → New repository secret**, add:

| Secret name | Value |
|-------------|-------|
| `AZURE_CLIENT_ID` | UAMI client ID |
| `AZURE_TENANT_ID` | Tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Subscription ID |

## Step 2 — Create the federated credential on the UAMI

Open the lab's Cloud Shell (or any terminal where you are signed into `az` as the lab user), then run:

```bash
# Values the lab handed you
UAMI_NAME="<pre-provisioned UAMI name>"
RG_NAME="meridian-mlops-rg"

# Values you fill in
GITHUB_OWNER="<your github username or org>"
GITHUB_REPO="smu-starter-projects"
GITHUB_BRANCH="main"

az identity federated-credential create \
  --name github-actions-main \
  --identity-name "$UAMI_NAME" \
  --resource-group "$RG_NAME" \
  --issuer https://token.actions.githubusercontent.com \
  --subject "repo:${GITHUB_OWNER}/${GITHUB_REPO}:ref:refs/heads/${GITHUB_BRANCH}" \
  --audiences api://AzureADTokenExchange
```

**Subject pattern reference** — the `subject` claim GitHub puts in the JWT is one of:

| Trigger | Subject pattern |
|---------|-----------------|
| Push / merge on a branch | `repo:<owner>/<repo>:ref:refs/heads/<branch>` |
| Push of a tag | `repo:<owner>/<repo>:ref:refs/tags/<tag>` |
| Pull request run | `repo:<owner>/<repo>:pull_request` |
| Workflow using an environment | `repo:<owner>/<repo>:environment:<env-name>` |

For this lab, the workflow fires on push to `main`, so the branch pattern above is the one you need.

## Step 3 — Push and verify

```bash
git add .
git commit -m "Wire OIDC deploy"
git push origin main
```

Watch the run in your fork's **Actions** tab. Successful login looks like:

```
Attempting Azure CLI login with OIDC...
Subscription is set successfully.
```

If you see `AADSTS70021: No matching federated identity record found`, your subject pattern does not match — most commonly the branch name in the federated credential does not match the branch you pushed to.

## Cleanup

The lab tears down the UAMI when your instance ends. No manual cleanup needed.
