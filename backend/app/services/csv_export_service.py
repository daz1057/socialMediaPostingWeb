"""
CSV export service for posts.
"""
import csv
import io
import logging
from datetime import datetime
from typing import Optional, List

from app.models.post import Post, PostStatus

logger = logging.getLogger(__name__)


class CSVExportService:
    """Service for exporting posts to CSV format."""

    CSV_HEADERS = [
        "id",
        "content",
        "status",
        "created_at",
        "updated_at",
        "scheduled_at",
        "published_at",
        "media_urls",
        "prompt_id",
    ]

    def export_posts(self, posts: List[Post]) -> str:
        """Export posts to CSV string.

        Args:
            posts: List of posts to export

        Returns:
            CSV formatted string
        """
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Write header
        writer.writerow(self.CSV_HEADERS)

        # Write data rows
        for post in posts:
            writer.writerow([
                post.id,
                post.content,
                post.status.value if post.status else "",
                self._format_datetime(post.created_at),
                self._format_datetime(post.updated_at),
                self._format_datetime(post.scheduled_at),
                self._format_datetime(post.published_at),
                self._format_media_urls(post.media_urls),
                post.prompt_id or "",
            ])

        csv_content = output.getvalue()
        output.close()

        logger.info(f"Exported {len(posts)} posts to CSV")
        return csv_content

    def _format_datetime(self, dt: Optional[datetime]) -> str:
        """Format datetime for CSV export.

        Args:
            dt: Datetime to format

        Returns:
            ISO formatted string or empty string
        """
        if dt is None:
            return ""
        return dt.isoformat()

    def _format_media_urls(self, urls: Optional[List[str]]) -> str:
        """Format media URLs for CSV export.

        Args:
            urls: List of URLs

        Returns:
            Pipe-separated string of URLs
        """
        if not urls:
            return ""
        return " | ".join(urls)


# Singleton instance
_csv_service: Optional[CSVExportService] = None


def get_csv_export_service() -> CSVExportService:
    """Get CSV export service singleton instance."""
    global _csv_service
    if _csv_service is None:
        _csv_service = CSVExportService()
    return _csv_service
