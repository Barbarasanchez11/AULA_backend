"""
PII (Personally Identifiable Information) Validation Service for AULA+

This service detects PII in text before storing events in the database.
Prevents storage of personal data to ensure privacy compliance.

Uses regex patterns for common PII types and can be extended with
libraries like Presidio or spaCy NER for more advanced detection.
"""

import re
from typing import List, Dict, Optional, Tuple
from enum import Enum


class PIIType(str, Enum):
    """Types of PII that can be detected"""
    NAME = "NAME"
    DNI_NIE = "DNI_NIE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    ADDRESS = "ADDRESS"
    BIRTH_DATE = "BIRTH_DATE"
    OTHER_IDENTIFIER = "OTHER_IDENTIFIER"


class PIIValidationResult:
    """Result of PII validation"""
    
    def __init__(self, is_valid: bool, detected_pii: List[Dict[str, str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: True if no PII detected, False otherwise
            detected_pii: List of detected PII items, each with:
                - "type": Type of PII (PIIType)
                - "value": Detected value
                - "context": Context where it was found
        """
        self.is_valid = is_valid
        self.detected_pii = detected_pii or []
    
    def add_pii(self, pii_type: PIIType, value: str, context: str = ""):
        """Add detected PII to the result"""
        self.detected_pii.append({
            "type": pii_type.value,
            "value": value,
            "context": context
        })
        self.is_valid = False
    
    def get_error_message(self) -> str:
        """Get human-readable error message"""
        if self.is_valid:
            return "No PII detected"
        
        pii_types = [item["type"] for item in self.detected_pii]
        unique_types = list(set(pii_types))
        
        if len(unique_types) == 1:
            return f"Se detectó información personal: {unique_types[0]}. Por favor, elimina los datos personales antes de guardar."
        else:
            return f"Se detectó información personal: {', '.join(unique_types)}. Por favor, elimina los datos personales antes de guardar."


class PIIValidator:
    """
    Service for validating that text does not contain PII.
    
    Detects:
    - Names (common Spanish names)
    - DNI/NIE (Spanish ID numbers)
    - Phone numbers
    - Email addresses
    - Addresses (basic patterns)
    - Birth dates
    """
    
    # Common Spanish first names (expanded list)
    COMMON_SPANISH_NAMES = [
        # Most common
        "maria", "carmen", "jose", "juan", "francisco", "antonio", "manuel",
        "laura", "ana", "cristina", "miguel", "david", "pablo", "daniel",
        "javier", "alejandro", "carlos", "luis", "jesus", "pedro",
        "lucia", "sofia", "paula", "martina", "elena", "claudia",
        "sergio", "adrian", "alvaro", "mario", "raul", "oscar",
        # Additional common names
        "isabel", "patricia", "monica", "andrea", "beatriz", "nuria",
        "roberto", "fernando", "jorge", "ricardo", "alberto", "jose luis",
        "maria jose", "maria carmen", "jose maria", "jose antonio",
        # Common in educational contexts
        "alumno", "alumna", "estudiante", "niño", "niña"  # These might be false positives, but better safe
    ]
    
    # Common Spanish surnames
    COMMON_SPANISH_SURNAMES = [
        "garcia", "rodriguez", "gonzalez", "fernandez", "lopez", "martinez",
        "sanchez", "perez", "gomez", "martin", "jimenez", "ruiz",
        "hernandez", "diaz", "moreno", "muñoz", "alvarez", "romero",
        "torres", "vazquez", "ramos", "gil", "ramirez", "serrano",
        "blanco", "suarez", "ortega", "delgado", "castro", "ortiz"
    ]
    
    def __init__(self):
        """Initialize PII validator with regex patterns"""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for PII detection"""
        
        # DNI/NIE pattern (Spanish ID)
        # Format: 8 digits + 1 letter, or 1 letter + 7 digits + 1 letter (NIE)
        self.dni_pattern = re.compile(
            r'\b(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b',
            re.IGNORECASE
        )
        
        # Phone number patterns (Spanish)
        # Mobile: 6XX XXX XXX or 7XX XXX XXX
        # Landline: 9XX XXX XXX
        # With country code: +34 or 0034
        self.phone_pattern = re.compile(
            r'\b(?:\+34|0034)?\s?[679]\d{2}\s?\d{3}\s?\d{3}\b',
            re.IGNORECASE
        )
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Date pattern (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
        # Also detects "nacido el", "fecha de nacimiento", etc.
        self.date_pattern = re.compile(
            r'\b(?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|nacido\s+(?:el|en)|fecha\s+de\s+nacimiento)\b',
            re.IGNORECASE
        )
        
        # Address pattern (basic - detects "calle", "avenida", "plaza", etc.)
        self.address_pattern = re.compile(
            r'\b(?:calle|avenida|av\.|plaza|paseo|carretera|ctra\.)\s+[A-Za-z0-9\s]+(?:\s+\d+)?\b',
            re.IGNORECASE
        )
    
    def detect_dni_nie(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect DNI/NIE numbers in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        for match in self.dni_pattern.finditer(text):
            matches.append((match.group(), match.start()))
        return matches
    
    def detect_phone(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect phone numbers in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        for match in self.phone_pattern.finditer(text):
            matches.append((match.group(), match.start()))
        return matches
    
    def detect_email(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect email addresses in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        for match in self.email_pattern.finditer(text):
            matches.append((match.group(), match.start()))
        return matches
    
    def detect_dates(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect dates (especially birth dates) in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        for match in self.date_pattern.finditer(text):
            matches.append((match.group(), match.start()))
        return matches
    
    def detect_addresses(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect addresses in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        for match in self.address_pattern.finditer(text):
            matches.append((match.group(), match.start()))
        return matches
    
    def detect_names(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect names in text using improved heuristics.
        
        Uses multiple strategies:
        1. Common Spanish names list (expanded)
        2. Capitalized words at sentence start or after punctuation
        3. Pattern: "Nombre Apellido" (two capitalized words together)
        
        This is an improved basic detection. For production, consider using
        Presidio or spaCy NER for more accurate detection.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of tuples (matched_text, start_position)
        """
        matches = []
        text_lower = text.lower()
        
        # Strategy 1: Check for common names (with word boundaries)
        all_names = self.COMMON_SPANISH_NAMES + self.COMMON_SPANISH_SURNAMES
        
        for name in all_names:
            # Pattern: name at start of sentence or after space/punctuation
            pattern = r'\b' + re.escape(name) + r'\b'
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                # Check if it's capitalized (likely a name)
                original_match = text[match.start():match.end()]
                if original_match[0].isupper():
                    matches.append((original_match, match.start()))
        
        # Strategy 2: Detect capitalized words that look like names
        # Pattern: Capitalized word at start of sentence or after punctuation
        # But exclude common words that are capitalized (like "Transición", "Anticipación")
        common_capitalized_words = [
            "transición", "transiciones", "cambio", "aprendizaje", "regulación",
            "anticipación", "mediación", "adaptación", "pausa", "apoyo",
            "estudiantes", "estudiante", "alumnos", "alumna", "alumno",
            "todos", "todos", "algunos", "algunas", "muchos", "muchas"
        ]
        
        # Find capitalized words (potential names)
        # Pattern: Word starting with capital letter, at sentence start or after punctuation
        capitalized_pattern = r'(?:^|[.!?]\s+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?'
        
        for match in re.finditer(capitalized_pattern, text):
            potential_name = match.group(1)
            potential_name_lower = potential_name.lower()
            
            # Skip if it's a common capitalized word (not a name)
            if potential_name_lower in common_capitalized_words:
                continue
            
            # Skip if it's a known event type or support type
            if potential_name_lower in ["exitoso", "parcial", "dificultad"]:
                continue
            
            # Skip if it's too short (likely not a name)
            if len(potential_name) < 3:
                continue
            
            # If it's not in our common names list but looks like a name, check context
            # Names are usually followed by verbs or at the start of sentences
            start_pos = match.start(1)
            end_pos = match.end(1)
            
            # Check if followed by common verb patterns (likely a name)
            context_after = text[end_pos:end_pos+20].lower()
            name_indicators = [" tuvo", " tuvo", " mostró", " necesitó", " trabajó", " participó"]
            
            # Also check for "Nombre y Nombre" pattern (two names)
            if start_pos > 0:
                context_before = text[max(0, start_pos-10):start_pos].lower()
                if " y " in context_before or " con " in context_before:
                    matches.append((potential_name, start_pos))
                    continue
            
            # If followed by name indicators or at sentence start, likely a name
            if any(indicator in context_after for indicator in name_indicators) or start_pos == 0:
                matches.append((potential_name, start_pos))
        
        # Strategy 3: Detect "Nombre Apellido" pattern (two capitalized words together)
        name_surname_pattern = r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\b'
        for match in re.finditer(name_surname_pattern, text):
            first_word = match.group(1)
            second_word = match.group(2)
            
            # Skip if either word is in common capitalized words
            if first_word.lower() in common_capitalized_words or second_word.lower() in common_capitalized_words:
                continue
            
            # If both words are capitalized and not common words, likely "Nombre Apellido"
            full_name = f"{first_word} {second_word}"
            matches.append((full_name, match.start()))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match_text, pos in matches:
            # Normalize for comparison (ignore case and position)
            key = (match_text.lower(), pos)
            if key not in seen:
                seen.add(key)
                unique_matches.append((match_text, pos))
        
        return unique_matches
    
    def validate_text(self, text: str, context: str = "") -> PIIValidationResult:
        """
        Validate that text does not contain PII.
        
        Args:
            text: Text to validate
            context: Context where the text was found (e.g., "description", "observations")
            
        Returns:
            PIIValidationResult with validation status and detected PII
        """
        result = PIIValidationResult(is_valid=True)
        
        if not text or not text.strip():
            return result
        
        # Detect DNI/NIE
        dni_matches = self.detect_dni_nie(text)
        for match_text, _ in dni_matches:
            result.add_pii(PIIType.DNI_NIE, match_text, context)
        
        # Detect phone numbers
        phone_matches = self.detect_phone(text)
        for match_text, _ in phone_matches:
            result.add_pii(PIIType.PHONE, match_text, context)
        
        # Detect emails
        email_matches = self.detect_email(text)
        for match_text, _ in email_matches:
            result.add_pii(PIIType.EMAIL, match_text, context)
        
        # Detect dates (especially birth dates)
        date_matches = self.detect_dates(text)
        for match_text, _ in date_matches:
            result.add_pii(PIIType.BIRTH_DATE, match_text, context)
        
        # Detect addresses
        address_matches = self.detect_addresses(text)
        for match_text, _ in address_matches:
            result.add_pii(PIIType.ADDRESS, match_text, context)
        
        # Detect names (basic detection)
        name_matches = self.detect_names(text)
        for match_text, _ in name_matches:
            result.add_pii(PIIType.NAME, match_text, context)
        
        return result
    
    def validate_event_text(
        self,
        description: str,
        additional_supports: Optional[str] = None,
        observations: Optional[str] = None
    ) -> PIIValidationResult:
        """
        Validate all text fields of an event.
        
        Args:
            description: Event description (required)
            additional_supports: Additional supports text (optional)
            observations: Observations text (optional)
            
        Returns:
            PIIValidationResult with validation status and all detected PII
        """
        result = PIIValidationResult(is_valid=True)
        
        # Validate description
        desc_result = self.validate_text(description, context="description")
        if not desc_result.is_valid:
            result.detected_pii.extend(desc_result.detected_pii)
            result.is_valid = False
        
        # Validate additional_supports
        if additional_supports:
            supports_result = self.validate_text(additional_supports, context="additional_supports")
            if not supports_result.is_valid:
                result.detected_pii.extend(supports_result.detected_pii)
                result.is_valid = False
        
        # Validate observations
        if observations:
            obs_result = self.validate_text(observations, context="observations")
            if not obs_result.is_valid:
                result.detected_pii.extend(obs_result.detected_pii)
                result.is_valid = False
        
        return result

