"""
Text Normalization Service for AULA+

This service normalizes text to ensure consistency before generating embeddings
and storing in the database. Normalization includes:
- Cleaning extra whitespace
- Standardizing capitalization
- Normalizing punctuation
- Removing control characters
"""

import re
from typing import Optional


class TextNormalizer:
    """
    Service for normalizing text to ensure consistency.
    
    Normalization ensures that:
    - Embeddings are generated from consistent text
    - Search and comparison work correctly
    - Text is clean and readable
    """
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text.
        
        - Removes leading and trailing whitespace
        - Replaces multiple spaces with single space
        - Removes tabs and newlines (replaces with space)
        - Removes multiple consecutive spaces
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Text with normalized whitespace
        """
        if not text:
            return ""
        
        # Replace tabs and newlines with spaces
        text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Remove leading and trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def normalize_capitalization(text: str, mode: str = "sentence") -> str:
        """
        Normalize capitalization in text.
        
        Modes:
        - "sentence": First letter uppercase, rest lowercase (default)
        - "preserve": Keep original capitalization
        - "lower": All lowercase
        - "upper": All uppercase
        
        Args:
            text: Text to normalize
            mode: Capitalization mode ("sentence", "preserve", "lower", "upper")
            
        Returns:
            str: Text with normalized capitalization
        """
        if not text:
            return ""
        
        if mode == "preserve":
            return text
        elif mode == "lower":
            return text.lower()
        elif mode == "upper":
            return text.upper()
        elif mode == "sentence":
            # First letter uppercase, rest lowercase
            if len(text) == 0:
                return text
            return text[0].upper() + text[1:].lower()
        else:
            # Default to sentence case
            return text[0].upper() + text[1:].lower() if text else ""
    
    @staticmethod
    def remove_control_characters(text: str) -> str:
        """
        Remove control characters from text.
        
        Removes characters that are not printable (except spaces and newlines).
        
        Args:
            text: Text to clean
            
        Returns:
            str: Text without control characters
        """
        if not text:
            return ""
        
        # Remove control characters (except space, tab, newline, carriage return)
        # Control characters are typically in range \x00-\x1F and \x7F-\x9F
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        return text
    
    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """
        Normalize punctuation in text.
        
        - Ensures proper spacing around punctuation
        - Normalizes quotes (straight to curly quotes if needed)
        - Removes multiple consecutive punctuation marks
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Text with normalized punctuation
        """
        if not text:
            return ""
        
        # Ensure space after punctuation (period, comma, semicolon, colon)
        # But not if it's already followed by space or end of string
        text = re.sub(r'([.,;:])([^\s])', r'\1 \2', text)
        
        # Remove multiple consecutive punctuation marks (except ellipsis)
        text = re.sub(r'([.,;:!?]){3,}', r'\1\1\1', text)
        
        # Normalize multiple spaces that might have been created
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_text(
        text: str,
        normalize_whitespace: bool = True,
        normalize_capitalization: bool = False,  # Default False to preserve original
        capitalization_mode: str = "sentence",
        remove_control_chars: bool = True,
        normalize_punctuation: bool = False  # Default False to preserve original
    ) -> str:
        """
        Normalize text using all normalization methods.
        
        This is the main method that applies all normalizations in the correct order.
        
        Args:
            text: Text to normalize
            normalize_whitespace: Whether to normalize whitespace (default: True)
            normalize_capitalization: Whether to normalize capitalization (default: False)
            capitalization_mode: Mode for capitalization ("sentence", "preserve", "lower", "upper")
            remove_control_chars: Whether to remove control characters (default: True)
            normalize_punctuation: Whether to normalize punctuation (default: False)
            
        Returns:
            str: Fully normalized text
        """
        if not text:
            return ""
        
        normalized = text
        
        # Step 1: Remove control characters first (before other operations)
        if remove_control_chars:
            normalized = TextNormalizer.remove_control_characters(normalized)
        
        # Step 2: Normalize whitespace
        if normalize_whitespace:
            normalized = TextNormalizer.normalize_whitespace(normalized)
        
        # Step 3: Normalize punctuation (before capitalization)
        if normalize_punctuation:
            normalized = TextNormalizer.normalize_punctuation(normalized)
        
        # Step 4: Normalize capitalization (last, as it affects the final output)
        if normalize_capitalization:
            normalized = TextNormalizer.normalize_capitalization(
                normalized,
                mode=capitalization_mode
            )
        
        return normalized
    
    @staticmethod
    def normalize_event_text(
        description: str,
        additional_supports: Optional[str] = None,
        observations: Optional[str] = None
    ) -> dict[str, str]:
        """
        Normalize all text fields of an event.
        
        Applies normalization to description, additional_supports, and observations.
        Uses conservative settings to preserve original meaning while ensuring consistency.
        
        Args:
            description: Event description (required)
            additional_supports: Additional supports text (optional)
            observations: Observations text (optional)
            
        Returns:
            dict: Dictionary with normalized fields:
                - "description": Normalized description
                - "additional_supports": Normalized additional_supports (or None)
                - "observations": Normalized observations (or None)
        """
        normalized = {
            "description": TextNormalizer.normalize_text(
                description,
                normalize_whitespace=True,
                normalize_capitalization=False,  # Preserve original capitalization
                remove_control_chars=True,
                normalize_punctuation=False  # Preserve original punctuation
            )
        }
        
        if additional_supports:
            normalized["additional_supports"] = TextNormalizer.normalize_text(
                additional_supports,
                normalize_whitespace=True,
                normalize_capitalization=False,
                remove_control_chars=True,
                normalize_punctuation=False
            )
        else:
            normalized["additional_supports"] = None
        
        if observations:
            normalized["observations"] = TextNormalizer.normalize_text(
                observations,
                normalize_whitespace=True,
                normalize_capitalization=False,
                remove_control_chars=True,
                normalize_punctuation=False
            )
        else:
            normalized["observations"] = None
        
        return normalized

