#!/usr/bin/env python3
"""
Monday.com API Client with modern best practices

Implements:
- API version 2024-10+ compatibility
- Complexity budget management
- Exponential backoff retry logic
- Proper pagination support
- Comprehensive error handling
"""

import os
import requests
import json
import time
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MondayConfig:
    """Configuration for Monday.com API client"""
    api_token: str
    api_version: str = "2024-10"
    max_retries: int = 3
    base_delay: float = 1.0
    max_complexity: int = 1000000
    default_page_size: int = 500
    base_url: str = "https://api.monday.com/v2"

    @classmethod
    def from_env(cls) -> 'MondayConfig':
        api_token = os.getenv('MONDAY_API_TOKEN')
        if not api_token:
            raise ValueError("MONDAY_API_TOKEN environment variable is required")

        return cls(
            api_token=api_token,
            api_version=os.getenv('MONDAY_API_VERSION', '2024-10'),
            max_retries=int(os.getenv('MONDAY_MAX_RETRIES', '3')),
            base_delay=float(os.getenv('MONDAY_BASE_DELAY', '1.0')),
            max_complexity=int(os.getenv('MONDAY_MAX_COMPLEXITY', '1000000')),
            default_page_size=int(os.getenv('MONDAY_PAGE_SIZE', '500'))
        )

class MondayAPIError(Exception):
    """Base exception for Monday.com API errors"""
    pass

class MondayRateLimitError(MondayAPIError):
    """Raised when API rate limit is exceeded"""
    pass

class MondayComplexityError(MondayAPIError):
    """Raised when complexity budget is exceeded"""
    pass

def retry_with_exponential_backoff(max_retries=3, base_delay=1.0):
    """Decorator for exponential backoff retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise e

                    # Check if error is retryable
                    if not _is_retryable_error(e):
                        raise e

                    # Calculate delay with jitter
                    delay = (base_delay * (2 ** attempt)) + random.uniform(0, 1)
                    logger.warning(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)

        return wrapper
    return decorator

def _is_retryable_error(error) -> bool:
    """Check if an error is retryable"""
    if isinstance(error, requests.exceptions.RequestException):
        if hasattr(error, 'response') and error.response:
            return error.response.status_code in [429, 500, 502, 503, 504]
    return isinstance(error, (MondayRateLimitError, MondayComplexityError))

class ComplexityManager:
    """Manages GraphQL complexity budget"""

    def __init__(self, max_complexity: int = 1000000):
        self.max_complexity = max_complexity
        self.current_complexity = 0
        self.reset_time = datetime.now() + timedelta(minutes=1)

    def check_complexity(self, query_complexity: int):
        """Check if query complexity is within budget"""
        now = datetime.now()

        # Reset complexity if time window has passed
        if now >= self.reset_time:
            self.current_complexity = 0
            self.reset_time = now + timedelta(minutes=1)

        # Check if query would exceed budget
        if self.current_complexity + query_complexity > self.max_complexity:
            wait_time = (self.reset_time - now).total_seconds()
            if wait_time > 0:
                logger.warning(f"Complexity budget exceeded. Waiting {wait_time:.1f}s for reset")
                time.sleep(wait_time)
                self.current_complexity = 0
                self.reset_time = datetime.now() + timedelta(minutes=1)

        self.current_complexity += query_complexity

class MondayAPIClient:
    """Modern Monday.com API client with best practices"""

    def __init__(self, config: Optional[MondayConfig] = None):
        self.config = config or MondayConfig.from_env()
        self.complexity_manager = ComplexityManager(self.config.max_complexity)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.config.api_token,
            'Content-Type': 'application/json',
            'API-Version': self.config.api_version
        })

    @retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
    def execute_query(self, query: str, variables: Optional[Dict] = None, complexity: int = 1000) -> Dict[str, Any]:
        """Execute a GraphQL query with error handling and retry logic"""

        # Check complexity budget
        self.complexity_manager.check_complexity(complexity)

        payload = {
            'query': query,
            'variables': variables or {}
        }

        try:
            response = self.session.post(self.config.base_url, json=payload)
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if 'errors' in data:
                error_messages = [error.get('message', str(error)) for error in data['errors']]

                # Check for specific error types
                for error in data['errors']:
                    if 'complexity budget exhausted' in error.get('message', '').lower():
                        raise MondayComplexityError(f"Complexity budget exhausted: {error['message']}")
                    elif 'rate limit' in error.get('message', '').lower():
                        raise MondayRateLimitError(f"Rate limit exceeded: {error['message']}")

                raise MondayAPIError(f"GraphQL errors: {'; '.join(error_messages)}")

            logger.info(f"Query executed successfully. Complexity: {complexity}")
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise MondayRateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise MondayAPIError(f"HTTP error {e.response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise MondayAPIError(f"Request failed: {e}")

    def get_boards_with_groups(self, board_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get boards with their groups using modern API"""

        query = """
        query GetBoardsWithGroups($boardIds: [ID!]) {
            boards(ids: $boardIds) {
                id
                name
                description
                state
                groups {
                    id
                    title
                    color
                    position
                }
            }
        }
        """

        variables = {"boardIds": board_ids} if board_ids else {}
        result = self.execute_query(query, variables, complexity=5000)

        return result['data']['boards']

    def get_board_items_paginated(self, board_id: str, group_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get all items from a board using pagination"""

        all_items = []
        cursor = None

        while True:
            query = """
            query GetBoardItems($boardId: ID!, $cursor: String) {
                boards(ids: [$boardId]) {
                    items_page(limit: 500, cursor: $cursor) {
                        items {
                            id
                            name
                            state
                            created_at
                            updated_at
                            group {
                                id
                                title
                            }
                            column_values {
                                id
                                text
                                value
                                type
                            }
                        }
                        cursor
                    }
                }
            }
            """

            variables = {
                "boardId": board_id,
                "cursor": cursor
            }

            result = self.execute_query(query, variables, complexity=10000)
            items_page = result['data']['boards'][0]['items_page']

            # Filter by group if specified
            items = items_page['items']
            if group_ids:
                items = [item for item in items if item['group']['id'] in group_ids]

            all_items.extend(items)

            cursor = items_page.get('cursor')
            if not cursor:
                break

        logger.info(f"Retrieved {len(all_items)} items from board {board_id}")
        return all_items

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""

        query = """
        query GetUserInfo {
            me {
                id
                name
                email
                account {
                    id
                    name
                }
            }
        }
        """

        result = self.execute_query(query, complexity=1000)
        return result['data']['me']

    def get_board_columns(self, board_id: str) -> List[Dict[str, Any]]:
        """Get column definitions for a board"""

        query = """
        query GetBoardColumns($boardId: ID!) {
            boards(ids: [$boardId]) {
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """

        variables = {"boardId": board_id}
        result = self.execute_query(query, variables, complexity=3000)

        return result['data']['boards'][0]['columns']

    def search_items_by_name(self, board_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search items by name in a specific board"""

        query = """
        query SearchItems($boardId: ID!) {
            boards(ids: [$boardId]) {
                items_page(limit: 500) {
                    items {
                        id
                        name
                        state
                        group {
                            id
                            title
                        }
                        column_values {
                            id
                            text
                            value
                            type
                        }
                    }
                }
            }
        }
        """

        variables = {"boardId": board_id}
        result = self.execute_query(query, variables, complexity=8000)

        all_items = result['data']['boards'][0]['items_page']['items']

        # Filter items by search term
        filtered_items = [
            item for item in all_items
            if search_term.lower() in item['name'].lower()
        ]

        logger.info(f"Found {len(filtered_items)} items matching '{search_term}'")
        return filtered_items

# Convenience function for quick API access
def get_monday_client() -> MondayAPIClient:
    """Get a configured Monday.com API client"""
    return MondayAPIClient()