"""
Gemini AI Service.

This module provides an abstraction layer for interactions with Google's Gemini API via the 
google-genai library. It supports both synchronous and asynchronous content generation,
including automatic retries with exponential backoff for network resilience.
"""

import asyncio
from functools import lru_cache
from typing import Optional, List

from PIL import Image
from google import genai
from google.genai import types

from app.config.settings import settings
from app.utils.logger import logger


class GeminiService:
    """
    Service class for managing Google Gemini AI interactions.
    
    Attributes:
        client (genai.Client): The authenticated Gemini API client.
        model (str): The specific Gemini model identifier (e.g., 'gemini-1.5-pro').
    """
    
    def __init__(self):
        """
        Initialize the Gemini service client.
        
        Using the API key from application settings.
        """
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.gemini_model
        logger.info(f"GeminiService initialized with model: {self.model}")
    
    async def generate_content(
        self,
        prompt: str,
        images: Optional[List[Image.Image]] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
        max_retries: int = 3,
    ) -> str:
        """
        Generate content asynchronously using the Gemini model.
        
        Includes built-in retry logic with exponential backoff to handle transient API errors.
        
        Args:
            prompt (str): The text instruction for the model.
            images (Optional[List[Image.Image]]): Optional list of PIL Image objects to include in the context.
            temperature (float): Controls randomness (0.0 to 1.0). Lower is more deterministic.
            max_output_tokens (int): Maximum number of tokens allowed in the response.
            max_retries (int): Maximum number of retry attempts for failed API calls.
            
        Returns:
            str: The generated text content from the model.
            
        Raises:
            RuntimeError: If the API call fails after all retry attempts.
        """
        # Construct request payload
        request_contents = []
        if images:
            request_contents.extend(images)
        request_contents.append(prompt)
            
        generation_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=request_contents,
                    config=generation_config,
                )
                logger.info("Content generated successfully via Gemini API.")
                return response.text
                
            except Exception as e:
                last_exception = e
                backoff_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                
                logger.warning(
                    f"Gemini API attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {backoff_time}s..."
                )
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_time)
        
        logger.error(f"Gemini API request failed after {max_retries} attempts. Last error: {last_exception}")
        raise RuntimeError(f"Gemini API failed after {max_retries} retries: {last_exception}")
    
    def generate_content_sync(
        self,
        prompt: str,
        images: Optional[List[Image.Image]] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
    ) -> str:
        """
        Generate content synchronously using the Gemini model.
        
        This method is a blocking call and should be used only when async execution 
        is not feasible.
        
        Args:
            prompt (str): The text instruction.
            images (Optional[List[Image.Image]]): Optional images.
            temperature (float): Creativity control.
            max_output_tokens (int): Response length limit.
            
        Returns:
            str: Generated text response.
            
        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            request_contents = []
            
            if images:
                request_contents.extend(images)
            
            request_contents.append(prompt)
            
            generation_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=request_contents,
                config=generation_config,
            )
            
            logger.info("Content generated successfully via Gemini API (Sync).")
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API Sync Error: {e}")
            raise RuntimeError(f"Gemini API error: {e}")
    
    def close(self):
        """
        Close the Gemini client connection and release resources.
        """
        try:
            self.client.close()
            logger.info("Gemini client connection closed.")
        except Exception as e:
            logger.warning(f"Error while closing Gemini client: {e}")


@lru_cache()
def get_gemini_service() -> GeminiService:
    """
    Retrieve the singleton instance of the Gemini Service.
    
    Uses lru_cache to ensure only one instance is initialized during the application lifecycle.
    
    Returns:
        GeminiService: The active service instance.
    """
    return GeminiService()
