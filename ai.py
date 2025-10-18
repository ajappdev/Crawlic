# General Imports
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal

# App Imports
import common as common

# OpenAI Client Initialization
client = OpenAI(
        organization=common.OPENAI_ORGANIZATION_ID,
        project=common.OPENAI_PROJECT_ID,
        api_key=common.OPENAI_API_KEY)

# AI Related Functions
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
        text_format=ContentDescription,
    )

    page_description = response.output_parsed

    return page_description


