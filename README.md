# AI Model Evals using Azure AI Foundry

[Evaluating GenAI Models using Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/evaluate-generative-ai-app) and the [azure-ai-evaluation](https://pypi.org/project/azure-ai-evaluation/) library.

## Requirements

1. [An Azure AI Foundry and project](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-projects?tabs=ai-foundry)
2. A LLM deployment in that project (gpt-4.1 for example)
3. Python 3.11+
4. [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli?view=azure-cli-latest)

## Setup

1. Clone this repository

```
git clone https://github.com/neaorin/ai-foundry-evals
cd ai-foundry-evals
```

2. Create and activate a Python virtual environment, install requirements
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Make a copy of the `.env.example` file and name it `.env`

4. Edit the values in the `.env` file to correspond to your settings.

5. Log in to Azure

```
az login
```

## Evaluation of AI quality for Retrieval Augmented Generation (RAG) chatbots

This example shows how you can evaluate a RAG chatbot based on [AI quality metrics](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/rag-evaluators) like Groundedness, Similarity, Fluency etc. It also allows evaluation for [Risk & Safety metrics](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-evaluators/risk-safety-evaluators) like Hate and unfairness, Self-harm, Sexual, and Violence.

1. Go to the `rag` folder

```
cd rag
```

2. Update the `input/validation_data.csv` file with your validation dataset

3. Open the `rag_model_endpoint.py` file and update the prompt as needed

4. Open the `models.json` file and update as needed with the model deployments you want to evaluate (see the **Evaluating different LLMs** section below for structure)

5. Upload your PDF documents to the `input/kb` folder

6. Build your vector index in Azure AI Search: 

```
python azure-ai-search-build-index.py
```

7. Compile your validation dataset including the context from vector search:

```
python azure-ai-search-retrieve-context.py
```

After this step, a new file `temp/validation_data_with_context.csv` should have been created.

8. Run your evaluations

```
python ai_quality_evals.py
```

9. After the evaluation run is over, you can examine the output in the [AI Foundry Portal](https://ai.azure.com/), in the Evaluation tab of your project.

## Evaluation AI text classification

This example shows how you can evaluate a text classifier that picks the appropriate category for a natural language text input.

1. Go to the `text-classification` folder

```
cd text-classification
```

2. Update the `input/validation_data.csv` file with your validation dataset

3. Open the `classify_model_endpoint.py` file and update the prompt as needed

4. Open the `models.json` file and update as needed with the model deployments you want to evaluate (see the **Evaluating different LLMs** section below for structure)

5. Run your evaluations

```
python classify_evals.py
```

6. After the evaluation run is over, you can examine the output in the [AI Foundry Portal](https://ai.azure.com/), in the Evaluation tab of your project.


## Evaluating different LLMs 

You can evaluate and compare multiple LLMs during the same evaluation run. The `models.json` file accepts an array of models, which can be either:

- OpenAI proprietary models (gpt-5, gpt-4.1 etc) - use `"type": "azure-openai"`, authentication uses your Entra account and the endpoint is an Azure OpenAI endpoint (`https://<endpoint>.openai.azure.com/`)
- Other models deployed in Azure AI Foundry (Llama, Mistral, DeepSeek, Phi etc) - use `"type": "azure-ai"`, authentication uses your Entra account and the endpoint is an AI Foundry endpoint (`https://<endpoint>.services.ai.azure.com/`)

Example JSON file:

```
[
    {
        "type": "azure-openai",
        "azure-deployment": "gpt-4.1",
        "azure-endpoint": "https://<endpoint>.openai.azure.com/"
    },
    {
        "type": "azure-ai",
        "azure-deployment": "Phi-4",
        "azure-endpoint": "https://<endpoint>.services.ai.azure.com/"
    }
]
```



