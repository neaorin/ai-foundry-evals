# This script builds an Azure AI Search index from PDF documents located in a specified folder.

pdf_folder_path = 'input/kb'
index_name: str = 'rag-index'


import os
from dotenv import load_dotenv
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient

# Configuration

load_dotenv('../.env')  # take environment variables from .env file
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDINGS_ENDPOINT = os.getenv("AZURE_OPENAI_EMBEDDINGS_ENDPOINT")
AZURE_SEARCH_API_ENDPOINT = os.getenv("AZURE_SEARCH_API_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2024-06-01"

# Get Entra access

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

credential = DefaultAzureCredential()

# Delete the index if it already exists
client = SearchIndexClient(endpoint=AZURE_SEARCH_API_ENDPOINT, credential=credential)
index_list = client.list_index_names()

if index_name in index_list:
    # Delete the index if it exists
    client.delete_index(index_name)
    print(f"Index '{index_name}' deleted successfully.")
else:
    print(f"Index '{index_name}' does not exist.")



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

# Insert text and embeddings into vector store
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# iterate over all PDF files in the folder, create embeddings and add them to the vector store
for pdf_file in os.listdir(pdf_folder_path):
    if not pdf_file.endswith('.pdf'):
        continue
    pdf_document_path = os.path.join(pdf_folder_path, pdf_file)
    print(f"Processing document: {pdf_document_path}")

    loader = PyPDFLoader(pdf_document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
    docs = text_splitter.split_documents(documents)
    vector_store.add_documents(documents=docs) 

print(f"Done adding documents to index {index_name}.")


