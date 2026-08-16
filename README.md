# smu-starter-projects-ai-300

Starter projects for the SkillMeUp **AI-300: Operationalizing Machine Learning and Generative AI Solutions** course.

Every hands-on lab in AI-300 forks this repo. Each lesson lives in its own `lessonN/` subfolder; every GitHub Actions workflow lives at the repo root under `.github/workflows/` with an `lN-` prefix so it is obvious at a glance which lesson owns each workflow.

## Repo layout

```
smu-starter-projects-ai-300/
├── .github/
│   └── workflows/
│       ├── l3-deploy-workspace.yml       ← Lesson 3
│       ├── l5-train-eta.yml              ← Lesson 5
│       ├── l7-retrain-on-drift.yml       ← Lesson 7
│       ├── l14-deploy-autodispatch.yml   ← Lesson 14 (capstone)
│       ├── l14-deploy-dispatcher.yml
│       ├── l14-deploy-eta.yml
│       └── l14-nightly-eval.yml
├── lesson3/    — MLOps foundation (GitHub, OIDC, Azure ML workspace via Bicep)
├── lesson5/    — Train, register, evaluate the ETA predictor
├── lesson7/    — Deploy the ETA predictor with progressive rollout + drift monitoring
├── lesson11/   — Evaluate and observe Meridian Dispatcher end-to-end
├── lesson13/   — RAG tuning + fine-tuning for the contract summarizer
└── lesson14/   — End-to-end MLOps + GenAIOps capstone (Auto-Dispatch)
```

Each `lessonN/` subfolder has its own README with the lesson-specific student workflow, Bicep / code samples, and any lesson-specific `.env.example`.

## Why workflows live at the repo root

GitHub Actions only scans `.github/workflows/*.yml` at the **repo root** — a workflow file dropped under `lessonN/.github/workflows/` is silently ignored and never fires. That's why the layout is split: source code + docs under `lessonN/`, workflows at the top.

Each workflow's `paths:` filter is scoped to its own lesson subfolder so a push that touches `lesson7/` does not fire the Lesson 3 workflow, and vice versa.

## Where labs point

Every AI-300 hands-on lab in SkillMeUp sets `StarterProjectUrl` to this repo and `StarterProjectSubfolder` to its own `lessonN`. When a student launches a lab, the lab VS Code container clones the fork and opens the correct `lessonN/` subfolder.

## Adding a new lesson starter

1. Create `lessonN/` at the repo root with the lesson's code, README, and any docs.
2. If the lesson has a GitHub Actions workflow, put it at `.github/workflows/lN-<name>.yml` and prefix every `paths:` filter + `--template-file` / `-f` / `path:` reference with `lessonN/`.
3. Point the corresponding SkillMeUp lab at `StarterProjectSubfolder: lessonN`.
