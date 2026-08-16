// main.bicep
// -------------------------------------------------------------
// AI-300 Lesson 3 — Meridian Freight MLOps Foundation
// Deploys a Microsoft.MachineLearningServices/workspaces resource wired to
// the four pre-provisioned dependent resources (Storage, KV, ACR, App Insights).
// The lab pre-provisions everything else in the resource group and hands you
// their names as parameters. You author only the workspace.
// -------------------------------------------------------------

@description('Per-instance suffix injected by the lab so the workspace name is unique.')
@minLength(3)
@maxLength(12)
param workspaceNameSuffix string

@description('Azure region for the workspace. Should match the pre-provisioned dependent resources.')
param location string = resourceGroup().location

@description('Name of the pre-provisioned Storage account bound as the workspace default datastore.')
param storageAccountName string

@description('Name of the pre-provisioned Key Vault bound to the workspace.')
param keyVaultName string

@description('Name of the pre-provisioned Container Registry bound to the workspace.')
param containerRegistryName string

@description('Name of the pre-provisioned Application Insights instance bound to the workspace.')
param applicationInsightsName string

@description('Friendly display name shown in Azure ML studio.')
param workspaceFriendlyName string = 'Meridian Freight MLOps'

@description('Description text shown in Azure ML studio.')
param workspaceDescription string = 'Production MLOps workspace for the Meridian Freight platform team.'

// Resolve the pre-provisioned dependencies by name so we can bind their resource IDs.
resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' existing = {
  name: storageAccountName
}

resource keyVault 'Microsoft.KeyVault/vaults@2024-11-01' existing = {
  name: keyVaultName
}

resource acr 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = {
  name: containerRegistryName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

// The workspace itself.
resource workspace 'Microsoft.MachineLearningServices/workspaces@2026-05-01' = {
  name: 'meridian-mlws-${workspaceNameSuffix}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: workspaceFriendlyName
    description: workspaceDescription
    storageAccount: storage.id
    keyVault: keyVault.id
    containerRegistry: acr.id
    applicationInsights: appInsights.id
    publicNetworkAccess: 'Enabled'
    hbiWorkspace: false
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output workspacePrincipalId string = workspace.identity.principalId
