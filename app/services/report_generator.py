"""
Report Generator Service.
Generates AI-powered analytics reports from invoice data.
"""

from PIL import Image

from app.services.gemini_service import get_gemini_service
from app.utils.logger import logger
from app.utils.file_handler import FileHandler


from app.prompts.analytics import REPORT_GENERATION_PROMPT


class ReportGenerator:
    """
    Service for generating analytics reports from invoice images.
    """
    
    # Prompt for generating analytics report
    REPORT_PROMPT = REPORT_GENERATION_PROMPT
    
    def __init__(self, session_id: str):
        """
        Initialize the report generator.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.gemini = get_gemini_service()
        self.file_handler = FileHandler(session_id)
        logger.info(f"Report generator initialized for session: {session_id}")
    
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
        
        supported_extensions = {'.jpg', '.jpeg', '.png'}
        
        for file_path in upload_dir.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    img = Image.open(file_path)
                    images.append(img)
                    logger.info(f"Loaded image for report: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load image {file_path.name}: {e}")
        
        return images
    
    def load_csv_data(self) -> str | None:
        """
        Load CSV data from upload directory for report generation.
        
        Returns:
            CSV content as string or None if no CSV found
        """
        upload_dir = self.file_handler.get_upload_dir()
        if not upload_dir.exists():
            return None
            
        # Find first CSV file
        for file_path in upload_dir.glob("*.csv"):
            try:
                # Read CSV content
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read CSV {file_path.name}: {e}")
        
        return None

    async def generate_report(self) -> str:
        """
        Generate an analytics report from invoice images or CSV data.
        
        Returns:
            Generated report text in markdown format
        """
        logger.info(f"Starting report generation for session: {self.session_id}")
        
        # 1. Try Loading Images
        images = self.load_images()
        
        if images:
            logger.info(f"Generating report from {len(images)} invoice images")
            report_text = await self.gemini.generate_content(
                prompt=self.REPORT_PROMPT,
                images=images,
                temperature=0.5,
                max_output_tokens=4096,
            )
        else:
            # 2. Try Loading CSV
            csv_data = self.load_csv_data()
            if csv_data:
                logger.info("Generating report from CSV data")
                # Append CSV data to prompt
                prompt = (
                    f"{self.REPORT_PROMPT}\n\n"
                    f"## Invoice Data (CSV)\n"
                    f"Please base your analysis on the following structured data instead of images:\n\n"
                    f"```csv\n{csv_data[:100000]}  # Truncate to avoid context limits if huge\n```"
                )
                
                report_text = await self.gemini.generate_content(
                    prompt=prompt,
                    images=None,
                    temperature=0.5,
                    max_output_tokens=4096,
                )
            else:
                raise FileNotFoundError("No invoice images or CSV data found for report generation")
        
        # Save report
        self.file_handler.save_report(report_text)
        
        logger.info("Successfully generated analytics report")
        return report_text
    
    def generate_report_sync(self) -> str:
        """
        Synchronous version of generate_report.
        """
        logger.info(f"Starting report generation (sync) for session: {self.session_id}")
        
        images = self.load_images()
        
        if not images:
            raise FileNotFoundError("No invoice images found for report generation")
        
        report_text = self.gemini.generate_content_sync(
            prompt=self.REPORT_PROMPT,
            images=images,
            temperature=0.5,
            max_output_tokens=4096,
        )
        
        self.file_handler.save_report(report_text)
        
        logger.info("Successfully generated analytics report")
        return report_text
    
    def get_saved_report(self) -> str:
        """
        Get previously generated report.
        
        Returns:
            Report text or empty string if not found
        """
        return self.file_handler.load_report()
