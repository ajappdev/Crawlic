"""
Celery application for asynchronous web scraping tasks.
Each worker runs in isolation to prevent Chrome process interference.
"""

from celery import Celery
from celery.signals import worker_process_shutdown
import os
import common as common
import ai as ai

# Initialize Celery
celery = Celery(
    'crawlic_tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)


# Celery Configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=280,  # 4:40 soft limit
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=1,  # Restart worker after each task (ensures Chrome cleanup)
    task_acks_late=True,  # Only ack after task completes
    task_reject_on_worker_lost=True,  # Requeue if worker dies
    result_expires=3600,  # Results expire after 1 hour
)


@celery.task(bind=True, max_retries=3, name='crawlic_tasks.scrape_page_content')
def scrape_page_content_task(self, link):
    """
    Scrapes page content using Selenium in an isolated worker.
    
    Args:
        link (str): URL to scrape
        
    Returns:
        dict: Contains success status and content or error
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Extracting content'})
        content = common.get_source_content(link)
        return {
            'success': True,
            'content': content
        }
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    

@celery.task(bind=True, max_retries=3, name='crawlic_tasks.get_answer_from_page')
def get_answer_from_page_task(self, link, user_query):
    """
    Scrapes page content using Selenium in an isolated worker then analyzes its
    content with OpenAI Responses API then answers the user query
    
    Args:
        link (str): URL to scrape
        user_query (str): The question of the user 
        
    Returns:
        dict: Contains success status and AI answer or error
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Answering user query about content'})
        content = common.get_source_content(link)
        answer = ai.get_answer_from_page(content, user_query)
        return {
            'success': True,
            'answer': answer
        }
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    

@celery.task(bind=True, max_retries=3, name='crawlic_tasks.custom_page_content')
def custom_page_content_task(self, link, output_format, user_query):
    """
    Scrapes page content using Selenium in an isolated worker and then
    analyzes its content with OpenAI Responses API and answers the user query
    in a structured JSON format
    
    Args:
        link (str): URL to scrape
        user_query (str): The question of the user 
        output_format (str): The required JSON structure from AI response
        
    Returns:
        dict: Contains success status and custom AI answer in specified
        JSON format or error
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Answering user query about content'})
        content = common.get_source_content(link)

        # Check if output_format is valid JSON
        is_valid, error_msg = common.is_valid_json(
            output_format,
            strict=True
        )

        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid JSON format for 'output_format' - {error_msg}"
            }

        custom_answer = ai.return_custom_page_content(
            content, user_query, output_format)

        return {
            "success": True,
            "custom_answer": custom_answer
        }
    
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


@celery.task(bind=True, max_retries=3, name='crawlic_tasks.describe_page')
def describe_page_task(self, link):
    """
    Scrapes page content using Selenium in an isolated worker and then
    analyzes its content with OpenAI Responses API
    
    Args:
        link (str): URL to scrape
        
    Returns:
        dict: Contains success status, content type, and content summary or error
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Analyzing content'})
        content = common.get_source_content(link)

        # Analyze content using AI module
        description = ai.describe_web_page_content(content)
        
        # Return structured response
        return{
            "success": True,
            "summary": description.summary,
            "type": description.type
        }

    except Exception as e:
        error_msg = f"Analyzing failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


@celery.task(bind=True, max_retries=3, name='crawlic_tasks.find_contact_email')
def find_contact_email_task(self, link):
    """
    Finds contact emails from a webpage.
    
    Args:
        link (str): URL to search for emails
        
    Returns:
        dict: Contains success status and found emails or error
    """
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Starting email search'})
        emails = common.find_contact_email(link)
        
        return {
            'success': True,
            'emails': emails
        }
        
    except Exception as e:
        error_msg = f"Email search failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }