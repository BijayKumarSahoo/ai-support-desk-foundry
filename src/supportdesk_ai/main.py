import logging
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from openai import APIError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


logger = logging.getLogger(__name__)


def main() -> int:
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    deployment_name = os.getenv("AZURE_AI_MODEL_DEPLOYMENT")

    if not project_endpoint:
        logger.error("AZURE_AI_PROJECT_ENDPOINT is not configured.")
        return 2

    if not deployment_name:
        logger.error("AZURE_AI_MODEL_DEPLOYMENT is not configured.")
        return 2

    try:
        credential = DefaultAzureCredential()

        project = AIProjectClient(endpoint=project_endpoint, credential=credential)

        client = project.get_openai_client()

        response = client.responses.create(
            model=deployment_name,
            instructions=(
                "You are SupportDesk AI, a technical support assistant. "
                "Provide concise, structured troubleshooting guiudance. "
                "Distinguish verified information from possiblities. "
                "Never claim to have inspected systems or logs you cannot access."
            ),
            input=(
                "Explain three possible causes of an Azure Function failing "
                "to connect to Azure Service Bus. Suggest on safe diagnositc "
                "check for each cause. Do not assume tath any particular cause "
                "has been confirmed."
            ),
            max_output_tokens=300,
        )

        answer = (response.output_text or "").strip()

        if not answer:
            logger.error("The model returned an empty text response")
            return 1

        print("\n--- SupportDesk AI response ---\n")
        print(answer)

        print("\n--- Usage ---")
        if response.usage:
            print(f"Input tokens:  {response.usage.input_tokens}")
            print(f"Output tokens: {response.usage.output_tokens}")
            print(f"Total tokens:  {response.usage.total_tokens}")
        else:
            print("Usage information was not returned.")

        return 0

    except (AzureError, APIError):
        logger.exception(
            "Foundry request failed. Check the endpoint, deployment name, "
            "authentication, permissions, quota, and network connectivity."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
