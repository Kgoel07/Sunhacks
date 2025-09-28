

from dotenv import load_dotenv
from pydantic import BaseNodel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


load_dotenv()

llm = ChatOpenAIgugi