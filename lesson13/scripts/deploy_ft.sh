#!/usr/bin/env bash
# Exercise 6 — deploy the fine-tuned model with a small capacity, name it
# gpt-4.1-mini-ft-v1, then flip the dispatcher to 90/10 split.
#
# Prerequisites:
#   - `az login --use-device-code` succeeded (VS Code container is headless)
#   - .env populated from ARM outputs
#   - fine_tuned_model.txt written by app.finetune
set -euo pipefail

# Load .env into current shell.
set -a
# shellcheck disable=SC1091
source .env
set +a

FT_MODEL="$(cat fine_tuned_model.txt)"
DEPLOYMENT_NAME="${FINE_TUNED_DEPLOYMENT:-gpt-4.1-mini-ft-v1}"

echo "Deploying $FT_MODEL as $DEPLOYMENT_NAME on account $AZURE_OPENAI_ACCOUNT_NAME..."

az cognitiveservices account deployment create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "$AZURE_OPENAI_ACCOUNT_NAME" \
    --deployment-name "$DEPLOYMENT_NAME" \
    --model-name "$FT_MODEL" \
    --model-version "1" \
    --model-format OpenAI \
    --sku-capacity "50" \
    --sku-name "Standard"

echo "Deployment created. Verify:"
az cognitiveservices account deployment show \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "$AZURE_OPENAI_ACCOUNT_NAME" \
    --deployment-name "$DEPLOYMENT_NAME" \
    --query "{name:name, model:properties.model.name, status:properties.provisioningState}" \
    -o table

echo "Next: run \`python -m app.dispatcher smoke\` to confirm both variants respond."
