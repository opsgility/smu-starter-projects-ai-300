// Reference-only Bicep mirror of the ARM template attached to the lab (SkillMeUp Template ID 72).
// The lab platform deploys this at start; you do NOT redeploy it from a workflow at student time.
// The Bicep is here only so the `bicep-validate` job in deploy-autodispatch.yml can what-if
// against production behaviour, and so you can read the shape without switching to the ARM JSON.
//
// If you edit this file, the ARM template attached to the lab does NOT update. That is intentional —
// the platform-owned template is versioned server-side.

targetScope = 'resourceGroup'

// See ARM JSON at Template ID 72 in SkillMeUp for the full authoritative content.
// This scaffold lists the resource shape only.

param location string = resourceGroup().location
