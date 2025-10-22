eval_prefix = "ai-quality"
validation_data_file = "temp/validation_data_with_context.csv"

import json
from pprint import pprint
import pandas as pd
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
from rag_model_endpoint import RAGModelEndpoint

# Load environment variables from .env file
load_dotenv('../.env')  # take environment variables from .env file
azure_ai_foundry_project_endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")

evaluator_model_config = {
    "azure_endpoint": os.getenv("EVALUATOR_AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.getenv("EVALUATOR_AZURE_OPENAI_DEPLOYMENT"),
}

df = pd.read_csv(validation_data_file)

# create temp folder if it doesn't exist
if not os.path.exists("temp"):
    os.makedirs("temp")

# save as JSONL
df.to_json("temp/data.jsonl", orient="records", lines=True, force_ascii=False)



import pathlib

from azure.ai.evaluation import evaluate
from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    GroundednessEvaluator,
    FluencyEvaluator,
    SimilarityEvaluator,
)


content_safety_evaluator = ContentSafetyEvaluator(
    azure_ai_project=azure_ai_foundry_project_endpoint, credential=DefaultAzureCredential()
)
relevance_evaluator = RelevanceEvaluator(evaluator_model_config)
coherence_evaluator = CoherenceEvaluator(evaluator_model_config)
groundedness_evaluator = GroundednessEvaluator(evaluator_model_config)
fluency_evaluator = FluencyEvaluator(evaluator_model_config)
similarity_evaluator = SimilarityEvaluator(evaluator_model_config)

path = str(pathlib.Path(pathlib.Path.cwd(), "temp", "data.jsonl"))

# read models.json file
with open("models.json") as f:
    models = json.load(f)

# iterate through all the items in the models.json array
for model in models:
    print(f"Evaluating model: {model['azure-deployment']}")

    results = evaluate(
        evaluation_name=eval_prefix + " - " + model['azure-deployment'],
        data=path,
        target=RAGModelEndpoint(model),
        azure_ai_project=azure_ai_foundry_project_endpoint,
        evaluators={
            "content_safety": content_safety_evaluator,
            "coherence": coherence_evaluator,
            "relevance": relevance_evaluator,
            "groundedness": groundedness_evaluator,
            "fluency": fluency_evaluator,
            "similarity": similarity_evaluator,
        },
        evaluator_config={
            "content_safety": {"column_mapping": {"query": "${data.query}", "response": "${target.response}"}},
            "coherence": {"column_mapping": {"response": "${target.response}", "query": "${data.query}"}},
            "relevance": {
                "column_mapping": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"}
            },
            "groundedness": {
                "column_mapping": {
                    "response": "${target.response}",
                    "context": "${data.context}",
                    "query": "${data.query}",
                }
            },
            "fluency": {
                "column_mapping": {"response": "${target.response}", "context": "${data.context}", "query": "${data.query}"}
            },
            "similarity": {
                "column_mapping": {"response": "${target.response}", "ground_truth": "${data.ground_truth}", "query": "${data.query}"}
            },
        },
    )

    pprint(results)

    pd.DataFrame(results["rows"])