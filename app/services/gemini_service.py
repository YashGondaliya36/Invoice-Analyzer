"""
Gemini AI Service.
Handles all interactions with Google's Gemini API using the google-genai library.
"""

from typing import Optional
from functools import lru_cache
from PIL import Image

from google import genai
from google.genai import types

from app.config.settings import settings
from app.utils.logger import logger


class GeminiService:
    """
    Service class for Google Gemini AI interactions.
    Uses the new google-genai library.
    """
    
    def __init__(self):
        """Initialize the Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.gemini_model
        logger.info(f"Gemini service initialized with model: {self.model}")
    
    async def generate_content(
        self,
        prompt: str,
        images: Optional[list[Image.Image]] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
    ) -> str:
        """
        Generate content using Gemini AI.
        
        Args:
            prompt: Text prompt for the model
            images: Optional list of PIL Images to include
            temperature: Model temperature (0-1)
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
        """
        try:
            # Build contents list
            contents = []
            
            # Add images first if provided
            if images:
                for img in images:
                    contents.append(img)
            
            # Add text prompt
            contents.append(prompt)
            
            # Configure generation settings
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            
            # Generate content using async client
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            
            logger.info("Successfully generated content from Gemini")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def generate_content_sync(
        self,
        prompt: str,
        images: Optional[list[Image.Image]] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
    ) -> str:
        """
        Synchronous version of generate_content.
        Use this when async is not available.
        """
        try:
            contents = []
            
            if images:
                for img in images:
                    contents.append(img)
            
            contents.append(prompt)
            
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            
            logger.info("Successfully generated content from Gemini (sync)")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def close(self):
        """Close the Gemini client and release resources."""
        try:
            self.client.close()
            logger.info("Gemini client closed")
        except Exception as e:
            logger.warning(f"Error closing Gemini client: {e}")


@lru_cache()
def get_gemini_service() -> GeminiService:
    """
    Get a cached instance of the Gemini service.
    Uses lru_cache to ensure only one instance is created.
    """
    return GeminiService()
