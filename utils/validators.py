import re
from typing import Optional
from fastapi import HTTPException, status

def validate_phone_number(phone: Optional[str]) -> Optional[str]:
    """Validate phone number format"""
    if not phone:
        return None
    
    # Remove spaces and common separators
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Basic international phone validation
    phone_pattern = r'^\+?[\d]{7,15}$'
    
    if not re.match(phone_pattern, cleaned_phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Use international format (+34 600 123 456)"
        )
    
    return phone

def validate_email_domain(email: str) -> bool:
    """Basic email domain validation"""
    # Block common disposable email domains
    disposable_domains = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com'
    ]
    
    domain = email.split('@')[1].lower()
    return domain not in disposable_domains

def sanitize_text_input(text: Optional[str], max_length: int = 1000) -> Optional[str]:
    """Sanitize text input to prevent injection attacks"""
    if not text:
        return None
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>&"\']', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_company_name(company: str) -> str:
    """Validate company name"""
    if len(company) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name must be at least 2 characters long"
        )
    
    if len(company) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name is too long (max 200 characters)"
        )
    
    # Remove potential malicious content
    return sanitize_text_input(company, 200)

def validate_contact_name(name: str) -> str:
    """Validate contact name"""
    if len(name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact name must be at least 2 characters long"
        )
    
    if len(name) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact name is too long (max 100 characters)"
        )
    
    return sanitize_text_input(name, 100)