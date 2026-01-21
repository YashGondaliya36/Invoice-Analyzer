"""
Invoice Processor Service.

This module handles the extraction of structured data from invoice images using the Gemini AI model.
It supports both synchronous and asynchronous processing, with parallel execution for efficiency.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional

from PIL import Image

from app.services.gemini_service import get_gemini_service
from app.utils.logger import logger
from app.utils.file_handler import FileHandler


class InvoiceProcessor:
    """
    Service for processing invoice images and extracting structured data.
    
    Attributes:
        session_id (str): Unique identifier for the current user session.
        gemini (GeminiService): Service instance for interacting with Google Gemini API.
        file_handler (FileHandler): Utility for managing session-specific files.
    """
    
    # Prompt for extracting invoice data - Instructions for the AI model
    EXTRACTION_PROMPT = '''
    Now be serious. I have given you various images of invoices. Your task is to extract all the information from the invoices
    and give me the structured output like the below example. Make sure you use entities that are common in all the invoices.

    1. Required Fields (Use exact field names):
    - "Invoice No" - Extract invoice number/reference exactly as shown
    - "Product Name" - Include full product description 
    - "Qty" - Convert all quantities to numbers only
    - "Amount" - Extract as number only (no currency symbols)
    - "Date" - Convert all dates to DD-MM-YY format

    2. Quality Control Steps:
    - Double-check all extracted values against original
    - Verify no data was missed or incorrectly parsed
    - Ensure numbers make mathematical sense
    - Confirm date is logically valid
    - Verify invoice number format is consistent
    - ex. Qty : 20.00 -> 20 (keep only integer value)
          amount : 3000.3500 -> 3000.35(keep two digit after .)

    Example of structured response:
    [
        {"Invoice No": "INV001", "Product Name": "Pipe A", "Qty": 25, "Amount": 3593.10, "Date": "2025-01-01"},
        {"Invoice No": "INV002", "Product Name": "Pipe B", "Qty": 50, "Amount": 3849.76, "Date": "2025-01-02"}
    ]
    
    IMPORTANT: Return ONLY the JSON array, no other text or markdown formatting.
    '''
    
    def __init__(self, session_id: str):
        """
        Initialize the invoice processor.
        
        Args:
            session_id: The unique session identifier.
        """
        self.session_id = session_id
        self.gemini = get_gemini_service()
        self.file_handler = FileHandler(session_id)
        logger.info(f"InvoiceProcessor initialized for session: {session_id}")
    
    def load_images(self) -> List[Image.Image]:
        """
        Load all valid invoice images from the session's upload directory.
        
        Returns:
            List[Image.Image]: A list of PIL Image objects ready for processing.
        """
        images = []
        upload_dir = self.file_handler.get_upload_dir()
        
        if not upload_dir.exists():
            logger.warning(f"Upload directory missing: {upload_dir}")
            return images
        
        supported_extensions = {'.jpg', '.jpeg', '.png'}
        
        for file_path in upload_dir.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    img = Image.open(file_path)
                    images.append(img)
                    logger.info(f"Loaded image: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load image '{file_path.name}': {e}")
        
        if not images:
            logger.warning("No valid images found in session upload directory.")
        else:
            logger.info(f"Loaded {len(images)} images for processing.")
        
        return images
    
    async def process_invoices(self) -> List[Dict[str, Any]]:
        """
        Process invoice images asynchronously to extract structured data.
        
        Implements chunked parallel processing to efficiently handle multiple images
        by processing them in batches concurrently.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents 
            a line item extracted from the invoices.
            
        Raises:
            FileNotFoundError: If no images are available for processing.
        """
        logger.info(f"Starting async invoice processing for session: {self.session_id}")
        
        images = self.load_images()
        if not images:
            raise FileNotFoundError("No invoice images found to process.")
        
        # Batch size for parallel processing
        chunk_size = 5
        image_chunks = [images[i:i + chunk_size] for i in range(0, len(images), chunk_size)]
        
        logger.info(f"Processing {len(images)} images in {len(image_chunks)} batches (Chunk size: {chunk_size}).")
        
        async def _process_batch(batch_images: List[Image.Image]) -> List[Dict[str, Any]]:
            """
            Process a single batch of images via the Gemini API.
            
            Args:
                batch_images: subset of images to process.
            
            Returns:
                List of extracted items from this batch.
            """
            try:
                response = await self.gemini.generate_content(
                    prompt=self.EXTRACTION_PROMPT,
                    images=batch_images,
                    temperature=0.3,  # Low temperature for factual extraction
                )
                return self._parse_json_response(response)
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                return []

        # Execute all batches concurrently
        tasks = [_process_batch(chunk) for chunk in image_chunks]
        batch_results = await asyncio.gather(*tasks)
        
        # Aggregate results
        extracted_items = []
        for result in batch_results:
            extracted_items.extend(result)
        
        if not extracted_items:
             logger.warning("No data extracted from any invoice batch.")
        
        self.file_handler.save_invoice_data(extracted_items)
        
        logger.info(f"Completed processing. Total items extracted: {len(extracted_items)}.")
        return extracted_items
    
    def process_invoices_sync(self) -> List[Dict[str, Any]]:
        """
        Process invoice images synchronously.
        
        This method processes all images in a single batch. Useful for environments
        where asynchronous execution is not supported.
        
        Returns:
            List[Dict[str, Any]]: A list of extracted invoice line items.
            
        Raises:
            FileNotFoundError: If no images are available for processing.
        """
        logger.info(f"Starting sync invoice processing for session: {self.session_id}")
        
        images = self.load_images()
        
        if not images:
            raise FileNotFoundError("No invoice images found to process.")
            
        response_text = self.gemini.generate_content_sync(
            prompt=self.EXTRACTION_PROMPT,
            images=images,
            temperature=0.3,
        )
        
        extracted_items = self._parse_json_response(response_text)
        self.file_handler.save_invoice_data(extracted_items)
        
        logger.info(f"Completed sync processing. Total items extracted: {len(extracted_items)}.")
        return extracted_items
    
    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse the JSON response extracted from the AI model.
        
        Handles potential markdown formatting (code blocks) often returned by LLMs.
        
        Args:
            response_text: The raw text response from the AI.
            
        Returns:
            List[Dict[str, Any]]: The parsed list of data dictionaries.
            
        Raises:
            ValueError: If the response cannot be parsed into a valid JSON list.
        """
        try:
            cleaned_text = response_text.strip()
            
            # Remove markdown code formatting
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
                
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Locate JSON array boundaries
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                cleaned_text = cleaned_text[start_idx:end_idx + 1]
            
            data = json.loads(cleaned_text)
            
            if not isinstance(data, list):
                raise ValueError("Parsed data is not a list as expected.")
            
            logger.debug(f"Successfully parsed {len(data)} items.")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Error: {e}")
            logger.debug(f"Failed Response Content: {response_text[:200]}...")
            raise ValueError(f"Invalid JSON response from AI model: {e}")
    
    def get_processed_data(self) -> List[Dict[str, Any]]:
        """
        Retrieve previously processed invoice data from storage.
        
        Returns:
            List[Dict[str, Any]]: List of invoice data items.
        """
        return self.file_handler.load_invoice_data()
