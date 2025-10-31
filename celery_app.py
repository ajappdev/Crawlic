"""
Celery application for asynchronous web scraping tasks.
Each worker runs in isolation to prevent Chrome process interference.
"""

from celery import Celery
from celery.signals import worker_process_shutdown
import os
import subprocess
import signal
import common as common


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


@worker_process_shutdown.sender
def cleanup_chrome_on_shutdown(**kwargs):
    """
    Safety net: Kill any remaining Chrome processes when worker shuts down.
    This runs after each task due to worker_max_tasks_per_child=1
    """
    common.kill_all_chrome_processes_linux()


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
            'link': link,
            'content': content
        }
    except TimeoutException:
        error_msg = f"Page load timeout for {link}"
        print(f"⏱️ {error_msg}")
        raise self.retry(exc=TimeoutException(error_msg), countdown=10)
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'link': link,
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
            'link': link,
            'emails': emails
        }
        
    except Exception as e:
        error_msg = f"Email search failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'link': link,
            'error': error_msg
        }
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass