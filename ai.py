# General Imports
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal
import re
import json

# App Imports
import common as common

# OpenAI Client Initialization
client = OpenAI(
        organization=common.OPENAI_ORGANIZATION_ID,
        project=common.OPENAI_PROJECT_ID,
        api_key=common.OPENAI_API_KEY)


# AI Related Functions
def get_answer_from_page(html_content: str, user_query: str) -> str:
    """
    This function used OPEN AI Responses API and takes HTML content of a web page and a user query,
    and returns a concise answer for the user query.
    ARGS:
        html_content (str): The HTML content of the web page.
        user_query (str): The user's question about the web page.
    RETURNS:
        str: A concise answer to the user's query based on the provided web page HTML.
    """

    instructions = """
        You are an expert web content analyzer and reader.
        I want you to read all the content in the provided HTML content and then answer the user's query
        based on that content.
        Do not add any additional text outside the answer. Avoid fluff like good question, smart query, etc.
        Start directly with the answer.
    """

    query = f"""
        Here is the HTML content of the web page:
        {html_content}

        The user query is:
        {user_query}
        """

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=query,
    )

    answer = response.output_text.strip()

    return answer


def return_custom_page_content(html_content: str, user_query: str, output_format: str) -> str:
    """
    This function used OPEN AI Responses API and takes HTML content of a web page and a user query,
    and returns a concise answer in a predefined JSON format.
    ARGS:
        html_content (str): The HTML content of the web page.
        user_query (str): The user's question about the web page.
        json_format (str): The desired JSON format for the response.
    RETURNS:
        str: A concise answer to the user's query in the specified JSON format.
    """

    instructions = """
        You are an expert web content analyzer and reader.
        I want you to read all the content in the provided HTML content and then answer the user's query
        based on that content. Your answer must be concise and strictly follow the JSON format provided.
        Do not add any additional text outside the JSON structure. But do not put the JSON inside markdown code fences.
        I mean, do not use ```json ... ``` around your answer. Start directly with the JSON object.
    """

    query = f"""
        Here is the HTML content of the web page:
        {html_content}

        The user query is:
        {user_query}

        Your answer must strictly be in the following JSON format:
        {output_format}
        """

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=query,
    )

    answer = response.output_text.strip()

    # Remove markdown code fences like ```json ... ```
    answer = re.sub(r"^```json|```$", "", answer, flags=re.IGNORECASE).strip()

    # Replace single quotes with double quotes (quick patch, works for simple JSON)
    answer = answer.replace("'", '"')

    json_answer = json.loads(answer)

    return json_answer

def describe_web_page_content(html_content: str) -> str:
    """
    Analyze and describe the content of a web page given its HTML content.
    Returns a summary and classification of the page type.
    ARGS:
        html_content (str): The HTML content of the web page to analyze.
    RETURNS:
        ContentDescription: An object containing the summary and type of the web page
    """
    class ContentDescription(BaseModel):
        summary: str = Field(..., description="Summary of the web page content")
        type: Literal[
            "Blog",
            "News Article", 
            "Product Page",
            "Landing Page",
            "Documentation",
            "Tutorial",
            "Job Board",
            "Job Description",
            "Forum",
            "Other"
        ] = Field(..., description="I want you to classify the web page into one of the following types: Blog, News Article, Product Page, Landing Page, Documentation, Tutorial, Job Board, Forum, or Other")

    instructions = """
        You are an expert web content analyzer.
        Given the HTML content of a web page, you will provide a concise summary
        of its content and classify the page into one of the specified types:
        Blog, News Article, Product Page, Landing Page, Documentation, Tutorial, Job Board, Forum, or Other
    """

    query = f"""
        Here is the HTML content of the web page:
        {html_content}
        """
    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=instructions,
        input=query,
        ext_format=ContentDescription
    )

    page_description = response.output_parsed

    return page_description


