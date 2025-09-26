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

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com"
        )

        if self.env["type"] == "azure-openai":
            client = AzureOpenAI(
                azure_endpoint=self.env["azure-endpoint"],
                api_version="2024-06-01",
                azure_ad_token_provider=token_provider,
            )
            # Call the model
            completion = client.chat.completions.create(
                model=self.env["azure-deployment"],
                messages=messages,
                max_tokens=250,
                temperature=0.0,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False,
            )
            output = completion.to_dict()
            return {"query": query, "response": output["choices"][0]["message"]["content"]}

        elif self.env["type"] == "azure-ai":
            client = ChatCompletionsClient(endpoint=self.env["azure-endpoint"], 
                                           credential=AzureKeyCredential(self.env["azure-key"]),
                                           api_version="2024-05-01-preview")

            completion = client.complete(
                model=self.env["azure-deployment"],
                messages=messages,
                max_tokens=250,
                temperature=0.0,
                frequency_penalty=0,
                presence_penalty=0,
            )

            return {"query": query, "response": completion.choices[0].message.content}
