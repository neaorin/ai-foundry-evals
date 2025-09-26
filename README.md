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

## Evaluation AI text classification

This example shows how you can evaluate a text classifier that picks the appropriate category for a natural language text input.

1. Go to the `text-classification` folder

```
cd text-classification
```

2. Update the `input/validation_data.csv` file with your validation dataset

3. Open the `classify_model_endpoint.py` file and update the prompt as needed

4. Open the `models.json` file and update as needed with the model deployments you want to evaluate

5. Run your evaluations

```
python classify_evals.py
```

6. After the evaluation run is over, you can examine the output in the [AI Foundry Portal](https://ai.azure.com/), in the Evaluation tab of your project.

