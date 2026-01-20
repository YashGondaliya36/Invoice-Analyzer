"""
Report Generator Service.
Generates AI-powered analytics reports from invoice data.
"""

from PIL import Image

from app.services.gemini_service import get_gemini_service
from app.utils.logger import logger
from app.utils.file_handler import FileHandler


class ReportGenerator:
    """
    Service for generating analytics reports from invoice images.
    """
    
    # Prompt for generating analytics report
    REPORT_PROMPT = '''
    You are a financial analyst tasked with reviewing a dataset of invoices. 
    Based on the provided invoice images, create a detailed and structured report covering the following aspects:

    ## Spending Trends:
    - Summarize the overall spending patterns, including total spending, average spending per invoice, and spending fluctuations over time.
    - Highlight the top spending periods (e.g., months, quarters, or years).
    - Identify categories, vendors, or clients contributing the most to spending.

    ## Key Performance Indicators (KPIs):
    - Analyze the total number of invoices and the average number of items per invoice.
    - Highlight high-value invoices (e.g., those exceeding a specific threshold).
    - Report on vendor/client contributions to spending or revenue.

    ## Product or Service Usage Insights:
    - Identify the most frequently purchased products or services and their revenue contributions.
    - Highlight any underutilized or low-demand products/services.
    - Note trends in product/service usage (e.g., increasing or decreasing demand).
    - Rank the top product/service categories based on sales volume or revenue.

    ## Actionable Insights:
    - Provide recommendations for optimizing spending, improving product/service utilization, or addressing any identified issues.
    
    ## Additional Instructions:
    - Format the report with clear sections and bullet points for readability.
    - Use quantitative metrics and percentages wherever possible.
    - Ensure insights are actionable and backed by data trends.
    - Use markdown formatting for headers and lists.
    '''
    
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
    
    async def generate_report(self) -> str:
        """
        Generate an analytics report from invoice images.
        
        Returns:
            Generated report text in markdown format
        """
        logger.info(f"Starting report generation for session: {self.session_id}")
        
        # Load images
        images = self.load_images()
        
        if not images:
            raise FileNotFoundError("No invoice images found for report generation")
        
        # Generate report with Gemini
        report_text = await self.gemini.generate_content(
            prompt=self.REPORT_PROMPT,
            images=images,
            temperature=0.5,  # Balanced temperature for creative yet accurate reports
            max_output_tokens=4096,
        )
        
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
