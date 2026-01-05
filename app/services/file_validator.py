"""Secure file upload validation for PowerCV."""
import hashlib
import logging
import os
import re
from pathlib import Path
from typing import Tuple, Optional

import magic
from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)


class SecureFileValidator:
    """Comprehensive file upload validation and security."""

    # Allowed file types and their MIME types
    ALLOWED_TYPES = {
        # Document formats
        'application/pdf': ['.pdf'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/msword': ['.doc'],

        # Text formats - Note: Magic library often detects markdown as text/plain
        # so we allow .md/.markdown under both text/plain and text/markdown for robustness
        'text/plain': ['.txt', '.md', '.markdown'],
        'text/markdown': ['.md', '.markdown'],

        # Additional text MIME types that might be encountered
        'text/x-markdown': ['.md', '.markdown'],
    }

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Dangerous file signatures (magic bytes)
    DANGEROUS_SIGNATURES = [
        b'MZ',      # Windows executable
        b'\x7fELF', # Linux executable
        b'#!/',     # Script files
        b'<?php',   # PHP files
        b'<%',      # ASP/JSP files
        b'<script', # HTML with scripts
    ]

    @classmethod
    async def validate_upload(cls, file: UploadFile) -> Tuple[bytes, str, str]:
        """Comprehensive file validation.

        Args:
            file: FastAPI UploadFile object

        Returns:
            Tuple of (content, safe_filename, file_hash)

        Raises:
            HTTPException: If validation fails
        """
        # 1. Validate filename
        cls._validate_filename(file.filename)

        # 2. Read and validate file content
        content = await file.read()

        # 3. Validate file size
        cls._validate_file_size(content, file.filename)

        # 4. Validate MIME type via content analysis
        cls._validate_content_type(content, file.filename)

        # 5. Check for dangerous content
        cls._check_dangerous_content(content, file.filename)

        # 6. Generate safe filename and hash
        safe_filename, file_hash = cls._generate_safe_filename(file.filename, content)

        logger.info(f"File validation passed: {safe_filename} ({len(content)} bytes)")
        return content, safe_filename, file_hash

    @classmethod
    def _validate_filename(cls, filename: str) -> None:
        """Validate filename for security issues."""
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )

        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename: path traversal not allowed"
            )

        # Check for hidden files
        if filename.startswith('.'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hidden files are not allowed"
            )

        # Check filename length
        if len(filename) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename too long"
            )

        # Check for suspicious extensions
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.jar']
        file_path = Path(filename)
        if file_path.suffix.lower() in suspicious_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )

    @classmethod
    def _validate_file_size(cls, content: bytes, filename: str) -> None:
        """Validate file size."""
        if len(content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file not allowed"
            )

    @classmethod
    def _validate_content_type(cls, content: bytes, filename: str) -> None:
        """Validate file content type via magic bytes and extension."""

        try:
            # Detect MIME type from content
            magic_result = magic.detect_from_content(content)
            if magic_result is None or magic_result.mime_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to determine file type from content"
                )

            detected_mime = magic_result.mime_type

            # Get expected extensions for this MIME type
            expected_extensions = cls.ALLOWED_TYPES.get(detected_mime, [])

            if not expected_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed: {detected_mime}"
                )

            # Check if file extension matches detected type
            file_path = Path(filename)
            if file_path.suffix.lower() not in expected_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File extension {file_path.suffix} doesn't match content type {detected_mime}"
                )

        except ImportError:
            # Fallback if python-magic is not available
            logger.warning("python-magic not available, skipping content validation")
            cls._validate_extension_only(filename)

    @classmethod
    def _validate_extension_only(cls, filename: str) -> None:
        """Fallback validation using only file extension."""
        file_path = Path(filename)
        extension = file_path.suffix.lower()

        # Check if extension is allowed
        allowed_extensions = [ext for exts in cls.ALLOWED_TYPES.values() for ext in exts]
        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed: {extension}"
            )

    @classmethod
    def _check_dangerous_content(cls, content: bytes, filename: str) -> None:
        """Check for dangerous content patterns."""
        # Check file signatures
        for signature in cls.DANGEROUS_SIGNATURES:
            if content.startswith(signature):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content not allowed"
                )

        # Check for script injection patterns
        text_content = content.decode('utf-8', errors='ignore').lower()

        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'vbscript:',
            r'data:text/html',
            r'<?php',
            r'<%.*%>',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, text_content, re.IGNORECASE | re.DOTALL):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File contains potentially dangerous content"
                )

    @classmethod
    def _generate_safe_filename(cls, original_filename: str, content: bytes) -> Tuple[str, str]:
        """Generate a safe filename and calculate hash."""
        # Calculate file hash for deduplication
        file_hash = hashlib.sha256(content).hexdigest()

        # Sanitize original filename
        safe_name = re.sub(r'[^\w\s\-_.]', '', original_filename)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)

        # Create new filename with hash prefix
        file_path = Path(original_filename)
        hash_prefix = file_hash[:8]  # First 8 chars of hash
        safe_filename = f"{hash_prefix}_{safe_name}"

        return safe_filename, file_hash


def store_file_securely(content: bytes, filename: str, user_id: str) -> str:
    """Store file in secure location with proper permissions.

    Args:
        content: File content
        filename: Safe filename
        user_id: User identifier

    Returns:
        Path to stored file
    """
    from app.config import get_settings

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)

    # Create user-specific directory
    user_dir = upload_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Save file
    file_path = user_dir / filename

    # Atomic write
    temp_path = file_path.with_suffix('.tmp')
    temp_path.write_bytes(content)
    temp_path.rename(file_path)

    # Set restrictive permissions
    os.chmod(file_path, 0o600)  # rw-------

    logger.info(f"File stored securely: {file_path}")
    return str(file_path)