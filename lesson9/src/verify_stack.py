"""
verify_stack.py — Ex 1 asks you to author this end-to-end.

Goal: prove that the pre-provisioned Foundry project + gpt-5.1 deployment
are reachable via azure-ai-projects using DefaultAzureCredential (no key).

You fill in EVERY line below the TODO markers — do not paste from another
lesson's code. The point of the exercise is that you feel the shape of the
azure-ai-projects call once, so it is not a magic import in the API in Ex 4.

Environment variables (injected by the lab, verify with `echo` before running):
    FOUNDRY_PROJECT_ENDPOINT   e.g. https://meridian-foundry-XXXX.services.ai.azure.com/api/projects/dispatcher
    FOUNDRY_CHAT_DEPLOYMENT    e.g. gpt-5.1

Run:
    cd lesson9/src
    python verify_stack.py

Expected: a coherent dispatcher-flavored paragraph proposing ONE next action
for the human dispatcher, ending in a `Next: ...` line.
"""
import os

# TODO Ex 1 Task 2 — imports
# Import DefaultAzureCredential from azure.identity and AIProjectClient from
# azure.ai.projects. The identity call is what turns the container's managed
# identity into a Foundry access token without ever seeing a client secret.


PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
CHAT_DEPLOYMENT = os.environ["FOUNDRY_CHAT_DEPLOYMENT"]


def main() -> None:
    # TODO Ex 1 Task 2 — construct the AIProjectClient
    # Pass endpoint=PROJECT_ENDPOINT and credential=DefaultAzureCredential().
    # DO NOT pass an api_key — the whole point is that there isn't one.
    project = ...

    # TODO Ex 1 Task 2 — get the Azure OpenAI client from the project
    # project.inference.get_azure_openai_client(api_version="2025-11-13-preview")
    openai = ...

    # TODO Ex 1 Task 2 — the first inference call
    # Use openai.chat.completions.create with:
    #   - model=CHAT_DEPLOYMENT
    #   - a system message describing the Meridian Dispatcher assistant
    #   - a user message about Load 4471 (Fresno, CA -> Portland, OR, reefer,
    #     42,000 lbs, produce, Tuesday pickup)
    completion = ...

    print(completion.choices[0].message.content)


if __name__ == "__main__":
    main()
