from typing_extensions import Self
from typing import TypedDict
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient


class RAGModelEndpoint:
    def __init__(self: Self, env: dict) -> None:
        self.env = env
        print(self.env)

    class Response(TypedDict):
        response: str

    # @trace
    def __call__(self: Self, query: str, context: str) -> Response:

        if not context:
            raise ValueError("Context is required for RAG model")
        
        messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant. Answer the user's question using the information provided in the context section.
                    --- begin context ---
                    {context}
                    --- end context ---
                    """
                },
                {
                    "role": "user",
                    "content": query,
                }
            ]

        client: ChatCompletionsClient = None

        if self.env["type"] == "azure-openai":
            client = ChatCompletionsClient(endpoint=f'{self.env["azure-endpoint"]}/openai/deployments/{self.env["azure-deployment"]}', 
                                           credential=DefaultAzureCredential(),
                                           credential_scopes=["https://cognitiveservices.azure.com/.default"],
                                           api_version="2024-06-01")

        elif self.env["type"] == "azure-ai":
            client = ChatCompletionsClient(endpoint=f'{self.env["azure-endpoint"]}/models', 
                                           credential=DefaultAzureCredential(),
                                           credential_scopes=["https://ai.azure.com/.default"],)

        completion = client.complete(
            model=self.env["azure-deployment"],
            messages=messages,
            max_tokens=1000,
            temperature=0.0,
            frequency_penalty=0,
            presence_penalty=0,
        )

        return {"response": completion.choices[0].message.content}