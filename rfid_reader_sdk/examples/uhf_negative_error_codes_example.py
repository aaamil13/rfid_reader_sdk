#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UHF Protocol Negative Error Codes Example

This file demonstrates how to handle negative error codes that are often
returned from the SDK but are not part of the standard UHF protocol specification.
"""

import logging

# UHF Protocol imports
from rfid.reader.uhf_protocol import (
    Language,
    get_error_message,
    set_default_language,
    add_translation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger("UHF_NEGATIVE_ERRORS_EXAMPLE")


def demonstrate_negative_error_codes():
    """
    Demonstrate negative error code translations in different languages
    """
    # Define some error codes to test
    test_error_codes = [
        -1,  # General communication error
        -2,  # Port access error
        -3,  # Port configuration error
        -4,  # Operation timeout
        -10,  # Device not found
        -99,  # Undefined error
        -123  # Unknown error code
    ]

    # Test languages
    test_languages = [
        Language.ENGLISH,
        Language.BULGARIAN,
        Language.RUSSIAN,
        Language.GERMAN,
        Language.FRENCH,
        Language.CHINESE
    ]

    logger.info("===== Negative Error Code Translations =====")

    # Print translations for each error code in each language
    for error_code in test_error_codes:
        logger.info(f"\nError Code: {error_code}")

        for language in test_languages:
            message = get_error_message(error_code, language)
            logger.info(f"  {language.upper()}: {message}")


def handle_custom_error_codes():
    """
    Demonstrate how to handle custom error codes
    """
    logger.info("\n===== Custom Error Codes =====")

    # Simulate error codes from different contexts or implementations
    custom_error_codes = {
        -42: "Reader not initialized",
        -50: "Transport layer error",
        -60: "Protocol mismatch",
        -100: "Driver error"
    }

    # Add translations for custom error code
    for code, description in custom_error_codes.items():
        # Add English descriptions
        add_translation(code, Language.ENGLISH, description)

        # Add translations for other languages (example for -42)
        if code == -42:
            add_translation(code, Language.BULGARIAN, "Четецът не е инициализиран")
            add_translation(code, Language.RUSSIAN, "Считыватель не инициализирован")
            add_translation(code, Language.GERMAN, "Lesegerät nicht initialisiert")
            add_translation(code, Language.FRENCH, "Lecteur non initialisé")
            add_translation(code, Language.CHINESE, "读取器未初始化")

    # Test custom error codes
    logger.info("Custom error code -42:")
    for language in [Language.ENGLISH, Language.BULGARIAN, Language.GERMAN]:
        message = get_error_message(-42, language)
        logger.info(f"  {language.upper()}: {message}")

    # Test other custom error codes (with no specific translations)
    logger.info("\nOther custom error codes:")
    for code in [-50, -60, -100]:
        english_message = get_error_message(code, Language.ENGLISH)
        bulgarian_message = get_error_message(code, Language.BULGARIAN)
        logger.info(f"  Error code {code}:")
        logger.info(f"    EN: {english_message}")
        logger.info(f"    BG: {bulgarian_message}")


def simulate_error_handling():
    """
    Simulate handling errors from SDK functions
    """
    logger.info("\n===== Error Handling Simulation =====")

    def simulate_sdk_function(operation, error_code=0):
        """Simulate an SDK function that might return an error code"""
        logger.info(f"Attempting operation: {operation}")
        if error_code != 0:
            logger.info(f"Operation failed with code: {error_code}")
            return error_code
        logger.info("Operation successful")
        return 0

    def handle_error(error_code, language=Language.ENGLISH, context=""):
        """Handle error codes with proper translation"""
        if error_code != 0:
            error_message = get_error_message(error_code, language)
            context_info = f" during {context}" if context else ""
            logger.error(f"Error{context_info}: {error_message} (Code: {error_code})")
            return False
        return True

    # Simulate different operations with error codes
    operations = [
        ("Connect to reader", 0),  # Success
        ("Configure reader", -3),  # Port configuration error
        ("Start inventory", -1),  # General communication error
        ("Read tag memory", -10),  # Device not found
        ("Custom operation", -42),  # Custom error
        ("Another operation", 0x14)  # Standard UHF protocol error
    ]

    # Set language for this simulation
    current_language = Language.BULGARIAN
    logger.info(f"Using language: {current_language}")

    # Process operations
    for operation, error_code in operations:
        result = simulate_sdk_function(operation, error_code)
        handle_error(result, current_language, operation)
        logger.info("---")


def main():
    """Main function"""
    logger.info("UHF Protocol Negative Error Codes Example")

    # Demonstrate negative error codes
    demonstrate_negative_error_codes()

    # Handle custom error codes
    handle_custom_error_codes()

    # Simulate error handling
    simulate_error_handling()

    logger.info("\nExample completed.")


if __name__ == "__main__":
    main()