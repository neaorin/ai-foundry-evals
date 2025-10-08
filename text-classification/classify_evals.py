eval_prefix = "text-classification"
validation_data_file = "input/validation_data.csv"

import json
from pprint import pprint
import pandas as pd
import os
from dotenv import load_dotenv
from classify_model_endpoint import ClassifyModelEndpoint
from azure.ai.evaluation import AzureAIProject 

# Load environment variables from .env file
load_dotenv('../.env')

class ClassifierEvaluator():

    def __call__(
        self,
        *,
        response: str,
        ground_truth: str,
    ): 
        if not response or not ground_truth:
            return 0
        # some models (Phi-4 etc) return markdown formatting, so we need to clean that up
        response = response.strip().replace("```json", "").replace("```", "").replace("```json\n", "").replace("```json\r\n", "")

        # read response as JSON and take the category field
        response_json = json.loads(response)
        response_category = response_json.get("categorie", "").strip().lower()

        ground_truth_category = ground_truth.strip().lower()

        if response_category == ground_truth_category:
            return 1
        else:
            return 0

azure_ai_project = AzureAIProject(
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    resource_group_name=os.getenv("AZURE_RESOURCE_GROUP_NAME"),
    project_name=os.getenv("AZURE_PROJECT_NAME"),
)

# create temp folder if it doesn't exist
if not os.path.exists("temp"):
    os.makedirs("temp")

df = pd.read_csv(validation_data_file)
# save as JSONL
df.to_json("temp/data.jsonl", orient="records", lines=True, force_ascii=False)

import pathlib

from azure.ai.evaluation import evaluate

path = str(pathlib.Path(pathlib.Path.cwd(), "temp", "data.jsonl"))
print(path)

# read models.json file
with open("models.json") as f:
    models = json.load(f)

# iterate through all the items in the models.json array
for model in models:
    print(f"Evaluating model: {model['azure-deployment']}")

    results = evaluate(
        evaluation_name=eval_prefix + " - " + model['azure-deployment'],
        data=path,
        target=ClassifyModelEndpoint(model),
        azure_ai_project=azure_ai_project,
        evaluators={
            "classification_accuracy": ClassifierEvaluator(),
        },
        evaluator_config={
            "classification_accuracy": {
                "column_mapping": {"response": "${target.response}", "ground_truth": "${data.ground_truth}", "query": "${data.query}"}
            },
        },
    )

    #pprint(results)