from typing_extensions import Self
from typing import TypedDict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient

system_prompt = """
Ești un agent de clasificare pentru <institutie>. Primești textul unei petiții în limba română și atribui exact o categorie din setul de mai jos. Scopul este rutarea corectă a petiției către echipa responsabilă.

Categorii disponibile:
- Categoria 1: Contestații & litigii fiscale
- Categoria 2: Impozit pe venit & contribuții sociale
- Categoria 3: Solicitări de informații despre legislația fiscală

Răspunde cu un JSON de forma:
{"categorie": "Impozit pe venit & contribuții sociale", "sumarizare": "Sumarizarea textului în maxim 20 de cuvinte"}

Valoarea campului "categorie" trebuie să fie exact una dintre categoriile specificate, fără variații. 
Răspunsul trebuie să fie un JSON valid, fără alte comentarii, fără markdown sau text adițional.
"""

class ClassifyModelEndpoint:
    def __init__(self: Self, env: dict) -> None:
        self.env = env
        print(self.env)

    class Response(TypedDict):
        query: str
        response: str

    # @trace
    def __call__(self: Self, query: str) -> Response:
        
        messages=[
                {
                    "role": "system",
                    "content": system_prompt
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
            max_tokens=250,
            temperature=0.0,
            frequency_penalty=0,
            presence_penalty=0,
        )

        return {"query": query, "response": completion.choices[0].message.content}
