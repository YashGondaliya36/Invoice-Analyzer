"""
Invoice Processor Service.
Handles extraction of structured data from invoice images using Gemini AI.
"""

import json
from pathlib import Path
from PIL import Image

from app.services.gemini_service import get_gemini_service
from app.utils.logger import logger
from app.utils.file_handler import FileHandler


class InvoiceProcessor:
    """
    Service for processing invoice images and extracting structured data.
    """
    
    # Prompt for extracting invoice data
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
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.gemini = get_gemini_service()
        self.file_handler = FileHandler(session_id)
        logger.info(f"Invoice processor initialized for session: {session_id}")
    
    def load_images(self) -> list[Image.Image]:
        """
        Load all invoice images for this session.
        
        Returns:
            List of PIL Image objects
        """
        images = []
        upload_dir = self.file_handler.get_upload_dir()
        
        if not upload_dir.exists():
            logger.warning(f"Upload directory not found: {upload_dir}")
            return images
        
        # Load all supported image files
        supported_extensions = {'.jpg', '.jpeg', '.png'}
        
        for file_path in upload_dir.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    img = Image.open(file_path)
                    images.append(img)
                    logger.info(f"Loaded image: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load image {file_path.name}: {e}")
        
        if not images:
            logger.warning("No valid images found in upload directory")
        else:
            logger.info(f"Loaded {len(images)} images for processing")
        
        return images
    
    async def process_invoices(self) -> list[dict]:
        """
        Process invoice images and extract structured data.
        
        Returns:
            List of dictionaries containing extracted invoice data
        """
        logger.info(f"Starting invoice processing for session: {self.session_id}")
        
        # Load images
        images = self.load_images()
        
        if not images:
            raise FileNotFoundError("No invoice images found to process")
        
        # Generate content with Gemini
        response_text = await self.gemini.generate_content(
            prompt=self.EXTRACTION_PROMPT,
            images=images,
            temperature=0.3,  # Lower temperature for more consistent extraction
        )
        
        # Parse the response
        structured_data = self._parse_response(response_text)
        
        # Save to CSV
        self.file_handler.save_invoice_data(structured_data)
        
        logger.info(f"Successfully processed {len(structured_data)} invoice items")
        return structured_data
    
    def process_invoices_sync(self) -> list[dict]:
        """
        Synchronous version of process_invoices.
        """
        logger.info(f"Starting invoice processing (sync) for session: {self.session_id}")
        
        images = self.load_images()
        
        if not images:
            raise FileNotFoundError("No invoice images found to process")
        
        response_text = self.gemini.generate_content_sync(
            prompt=self.EXTRACTION_PROMPT,
            images=images,
            temperature=0.3,
        )
        
        structured_data = self._parse_response(response_text)
        self.file_handler.save_invoice_data(structured_data)
        
        logger.info(f"Successfully processed {len(structured_data)} invoice items")
        return structured_data
    
    def _parse_response(self, response_text: str) -> list[dict]:
        """
        Parse the Gemini response into structured data.
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            List of dictionaries with invoice data
        """
        try:
            # Clean up response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Find JSON array boundaries
            start_idx = cleaned_text.find('[')
            end_idx = cleaned_text.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                cleaned_text = cleaned_text[start_idx:end_idx + 1]
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            if not isinstance(data, list):
                raise ValueError("Expected a list of invoice items")
            
            logger.info(f"Successfully parsed {len(data)} items from response")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
    
    def get_processed_data(self) -> list[dict]:
        """
        Get previously processed invoice data.
        
        Returns:
            List of dictionaries with invoice data
        """
        return self.file_handler.load_invoice_data()
