# This script retrieves context documents from an Azure AI Search index for each query in a validation dataset and saves the results to a new CSV file.
index_name: str = 'rag-index'
output_file_name = 'temp/validation_data_with_context.csv'
validation_data_file = 'input/validation_data.csv'

import os
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import pandas as pd

df = pd.read_csv(validation_data_file)

# Configuration

load_dotenv('../.env')  # take environment variables from .env file
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDINGS_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDINGS_ENDPOINT")
AZURE_SEARCH_API_ENDPOINT = os.getenv("AZURE_SEARCH_API_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2024-06-01"

# create temp folder if it doesn't exist
if not os.path.exists("temp"):
    os.makedirs("temp")

# Get Entra access

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

credential = DefaultAzureCredential()

# Create embeddings and vector store instances
embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_EMBEDDINGS_ENDPOINT,
    azure_ad_token_provider=token_provider,
)

vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=AZURE_SEARCH_API_ENDPOINT,
    azure_search_key=None,
    azure_credential=credential,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 2},
)

# add a new column to the dataframe with a function that will contain the context docs
df['context'] = df['query'].apply(lambda x: [doc.page_content for doc in vector_store.similarity_search(query=x, k=3)])

# save the dataframe to a new csv file
df.to_csv(output_file_name, index=False)

print(f"Validation data with context saved to {output_file_name}")

