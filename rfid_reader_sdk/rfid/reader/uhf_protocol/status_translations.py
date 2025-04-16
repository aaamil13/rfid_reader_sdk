"""
UHF Protocol Status Code Translations

This module provides translations for UHF protocol status codes in multiple languages.
It supports English, Bulgarian, Russian, German, French, Chinese, and can be extended for other languages.
"""

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


# Language codes
class Language:
    """Supported language codes"""
    ENGLISH = "en"
    BULGARIAN = "bg"
    RUSSIAN = "ru"
    GERMAN = "de"
    FRENCH = "fr"
    CHINESE = "zh"


# Default language
DEFAULT_LANGUAGE = Language.ENGLISH

# Import StatusCode after defining Language to avoid circular imports
try:
    from .status_codes import StatusCode
except ImportError:
    # Define placeholder for when used standalone
    class StatusCode:
        """Placeholder for StatusCode enum"""
        SUCCESS = 0x00
        GENERAL_ERROR = 0x01
        MEMORY_OVERRUN = 0x02
        MEMORY_LOCKED = 0x03
        AUTH_FAIL = 0x04
        NO_TAG = 0x0B
        RF_TIMEOUT = 0x0C
        PARAMETER_UNSUPPORTED = 0x14
        PARAMETER_LENGTH_ERROR = 0x15
        PARAMETER_CONTEXT_ERROR = 0x16
        UNSUPPORTED_COMMAND = 0x17
        ADDRESS_ERROR = 0x18
        CHECKSUM_ERROR = 0x20
        UNSUPPORTED_TLV_TYPE = 0x21
        FLASH_ERROR = 0x22
        INTERNAL_ERROR = 0xFF

# Status code translations
# Format: {status_code: {language_code: translation}}
STATUS_TRANSLATIONS: Dict[int, Dict[str, str]] = {
    StatusCode.SUCCESS: {
        Language.ENGLISH: "Operation successful",
        Language.BULGARIAN: "Операцията е успешна",
        Language.RUSSIAN: "Операция выполнена успешно",
        Language.GERMAN: "Operation erfolgreich",
        Language.FRENCH: "Opération réussie",
        Language.CHINESE: "操作成功"
    },
    StatusCode.GENERAL_ERROR: {
        Language.ENGLISH: "General error",
        Language.BULGARIAN: "Обща грешка",
        Language.RUSSIAN: "Общая ошибка",
        Language.GERMAN: "Allgemeiner Fehler",
        Language.FRENCH: "Erreur générale",
        Language.CHINESE: "一般错误"
    },
    StatusCode.MEMORY_OVERRUN: {
        Language.ENGLISH: "Memory overrun",
        Language.BULGARIAN: "Препълване на паметта",
        Language.RUSSIAN: "Переполнение памяти",
        Language.GERMAN: "Speicherüberlauf",
        Language.FRENCH: "Dépassement de mémoire",
        Language.CHINESE: "内存溢出"
    },
    StatusCode.MEMORY_LOCKED: {
        Language.ENGLISH: "Memory locked",
        Language.BULGARIAN: "Паметта е заключена",
        Language.RUSSIAN: "Память заблокирована",
        Language.GERMAN: "Speicher gesperrt",
        Language.FRENCH: "Mémoire verrouillée",
        Language.CHINESE: "内存已锁定"
    },
    StatusCode.AUTH_FAIL: {
        Language.ENGLISH: "Authentication failed",
        Language.BULGARIAN: "Неуспешна автентикация",
        Language.RUSSIAN: "Ошибка аутентификации",
        Language.GERMAN: "Authentifizierung fehlgeschlagen",
        Language.FRENCH: "Échec d'authentification",
        Language.CHINESE: "认证失败"
    },
    StatusCode.NO_TAG: {
        Language.ENGLISH: "No tag responding",
        Language.BULGARIAN: "Няма отговор от таг",
        Language.RUSSIAN: "Нет ответа от метки",
        Language.GERMAN: "Kein Tag antwortet",
        Language.FRENCH: "Aucune étiquette ne répond",
        Language.CHINESE: "无标签响应"
    },
    StatusCode.RF_TIMEOUT: {
        Language.ENGLISH: "RF communication timeout",
        Language.BULGARIAN: "Изтекло време за RF комуникация",
        Language.RUSSIAN: "Тайм-аут RF-связи",
        Language.GERMAN: "RF-Kommunikations-Timeout",
        Language.FRENCH: "Timeout de communication RF",
        Language.CHINESE: "RF通信超时"
    },
    StatusCode.PARAMETER_UNSUPPORTED: {
        Language.ENGLISH: "Parameter unsupported",
        Language.BULGARIAN: "Неподдържан параметър",
        Language.RUSSIAN: "Неподдерживаемый параметр",
        Language.GERMAN: "Parameter nicht unterstützt",
        Language.FRENCH: "Paramètre non pris en charge",
        Language.CHINESE: "参数不支持"
    },
    StatusCode.PARAMETER_LENGTH_ERROR: {
        Language.ENGLISH: "Parameter length error",
        Language.BULGARIAN: "Грешка в дължината на параметъра",
        Language.RUSSIAN: "Ошибка длины параметра",
        Language.GERMAN: "Fehler in der Parameterlänge",
        Language.FRENCH: "Erreur de longueur de paramètre",
        Language.CHINESE: "参数长度错误"
    },
    StatusCode.PARAMETER_CONTEXT_ERROR: {
        Language.ENGLISH: "Parameter context error",
        Language.BULGARIAN: "Грешка в контекста на параметъра",
        Language.RUSSIAN: "Ошибка контекста параметра",
        Language.GERMAN: "Parameterkontextfehler",
        Language.FRENCH: "Erreur de contexte de paramètre",
        Language.CHINESE: "参数上下文错误"
    },
    StatusCode.UNSUPPORTED_COMMAND: {
        Language.ENGLISH: "Unsupported command",
        Language.BULGARIAN: "Неподдържана команда",
        Language.RUSSIAN: "Неподдерживаемая команда",
        Language.GERMAN: "Nicht unterstützter Befehl",
        Language.FRENCH: "Commande non prise en charge",
        Language.CHINESE: "不支持的命令"
    },
    StatusCode.ADDRESS_ERROR: {
        Language.ENGLISH: "Address error",
        Language.BULGARIAN: "Грешка в адреса",
        Language.RUSSIAN: "Ошибка адреса",
        Language.GERMAN: "Adressfehler",
        Language.FRENCH: "Erreur d'adresse",
        Language.CHINESE: "地址错误"
    },
    StatusCode.CHECKSUM_ERROR: {
        Language.ENGLISH: "Checksum error",
        Language.BULGARIAN: "Грешка в контролната сума",
        Language.RUSSIAN: "Ошибка контрольной суммы",
        Language.GERMAN: "Prüfsummenfehler",
        Language.FRENCH: "Erreur de somme de contrôle",
        Language.CHINESE: "校验和错误"
    },
    StatusCode.UNSUPPORTED_TLV_TYPE: {
        Language.ENGLISH: "Unsupported TLV type",
        Language.BULGARIAN: "Неподдържан TLV тип",
        Language.RUSSIAN: "Неподдерживаемый тип TLV",
        Language.GERMAN: "Nicht unterstützter TLV-Typ",
        Language.FRENCH: "Type TLV non pris en charge",
        Language.CHINESE: "不支持的TLV类型"
    },
    StatusCode.FLASH_ERROR: {
        Language.ENGLISH: "Flash memory error",
        Language.BULGARIAN: "Грешка във флаш паметта",
        Language.RUSSIAN: "Ошибка флэш-памяти",
        Language.GERMAN: "Flash-Speicherfehler",
        Language.FRENCH: "Erreur de mémoire flash",
        Language.CHINESE: "闪存错误"
    },
    StatusCode.INTERNAL_ERROR: {
        Language.ENGLISH: "Internal error",
        Language.BULGARIAN: "Вътрешна грешка",
        Language.RUSSIAN: "Внутренняя ошибка",
        Language.GERMAN: "Interner Fehler",
        Language.FRENCH: "Erreur interne",
        Language.CHINESE: "内部错误"
    },

    # Add non-standard error codes that appear in practice
    -1: {
        Language.ENGLISH: "General communication error",
        Language.BULGARIAN: "Обща комуникационна грешка",
        Language.RUSSIAN: "Общая ошибка связи",
        Language.GERMAN: "Allgemeiner Kommunikationsfehler",
        Language.FRENCH: "Erreur de communication générale",
        Language.CHINESE: "通信总错误"
    },
    -2: {
        Language.ENGLISH: "Port access error",
        Language.BULGARIAN: "Грешка при достъп до порт",
        Language.RUSSIAN: "Ошибка доступа к порту",
        Language.GERMAN: "Portzugriffsfehler",
        Language.FRENCH: "Erreur d'accès au port",
        Language.CHINESE: "端口访问错误"
    },
    -3: {
        Language.ENGLISH: "Port configuration error",
        Language.BULGARIAN: "Грешка в конфигурацията на порта",
        Language.RUSSIAN: "Ошибка конфигурации порта",
        Language.GERMAN: "Portkonfigurationsfehler",
        Language.FRENCH: "Erreur de configuration du port",
        Language.CHINESE: "端口配置错误"
    },
    -10: {
        Language.ENGLISH: "Device not found",
        Language.BULGARIAN: "Устройството не е намерено",
        Language.RUSSIAN: "Устройство не найдено",
        Language.GERMAN: "Gerät nicht gefunden",
        Language.FRENCH: "Périphérique introuvable",
        Language.CHINESE: "未找到设备"
    },
    -99: {
        Language.ENGLISH: "Undefined error",
        Language.BULGARIAN: "Неопределена грешка",
        Language.RUSSIAN: "Неопределенная ошибка",
        Language.GERMAN: "Undefinierter Fehler",
        Language.FRENCH: "Erreur non définie",
        Language.CHINESE: "未定义的错误"
    },
    # Additional common negative error codes
    -4: {
        Language.ENGLISH: "Operation timeout",
        Language.BULGARIAN: "Изтекло време за операцията",
        Language.RUSSIAN: "Тайм-аут операции",
        Language.GERMAN: "Zeitüberschreitung bei der Operation",
        Language.FRENCH: "Délai d'opération expiré",
        Language.CHINESE: "操作超时"
    },
    -5: {
        Language.ENGLISH: "Invalid parameter",
        Language.BULGARIAN: "Невалиден параметър",
        Language.RUSSIAN: "Недопустимый параметр",
        Language.GERMAN: "Ungültiger Parameter",
        Language.FRENCH: "Paramètre invalide",
        Language.CHINESE: "无效参数"
    },
    -6: {
        Language.ENGLISH: "Resource busy",
        Language.BULGARIAN: "Ресурсът е зает",
        Language.RUSSIAN: "Ресурс занят",
        Language.GERMAN: "Ressource beschäftigt",
        Language.FRENCH: "Ressource occupée",
        Language.CHINESE: "资源繁忙"
    }
}


class StatusTranslator:
    """
    Status code translator for multiple languages

    This class provides translations for UHF protocol status codes
    in different languages.
    """

    def __init__(self, default_language: str = DEFAULT_LANGUAGE):
        """
        Initialize the translator

        Args:
            default_language: Default language code
        """
        self.default_language = default_language
        self._translations = STATUS_TRANSLATIONS

    def get_translation(self, status_code: int, language: str = None) -> str:
        """
        Get translation for a status code

        Args:
            status_code: Status code to translate
            language: Language code (or None for default)

        Returns:
            str: Translated status message
        """
        language = language or self.default_language

        # Try to get translation for the specified language
        if status_code in self._translations:
            translations = self._translations[status_code]

            # Return translation in requested language if available
            if language in translations:
                return translations[language]

            # Fall back to English if the requested language is not available
            if Language.ENGLISH in translations:
                return translations[Language.ENGLISH]

        # If no translation found, return a default message based on the code
        if status_code < 0:
            default_msg = f"System error code {status_code}"
        else:
            default_msg = f"Status code 0x{status_code:02X}"

        # Return default message in English or translate it for other languages
        if language == Language.ENGLISH:
            return default_msg
        elif language == Language.BULGARIAN:
            return f"Системен код за грешка {status_code}" if status_code < 0 else f"Статус код 0x{status_code:02X}"
        elif language == Language.RUSSIAN:
            return f"Системный код ошибки {status_code}" if status_code < 0 else f"Код состояния 0x{status_code:02X}"
        elif language == Language.GERMAN:
            return f"Systemfehlercode {status_code}" if status_code < 0 else f"Statuscode 0x{status_code:02X}"
        elif language == Language.FRENCH:
            return f"Code d'erreur système {status_code}" if status_code < 0 else f"Code d'état 0x{status_code:02X}"
        elif language == Language.CHINESE:
            return f"系统错误代码 {status_code}" if status_code < 0 else f"状态码 0x{status_code:02X}"
        else:
            return default_msg

    def add_translation(self, status_code: int, language: str, translation: str) -> None:
        """
        Add a new translation

        Args:
            status_code: Status code
            language: Language code
            translation: Translated message
        """
        if status_code not in self._translations:
            self._translations[status_code] = {}

        self._translations[status_code][language] = translation

    def set_default_language(self, language: str) -> None:
        """
        Set default language

        Args:
            language: Language code
        """
        self.default_language = language


# Global translator instance
_translator = StatusTranslator()


def get_error_message(status_code: int, language: str = None) -> str:
    """
    Get error message for a status code

    Args:
        status_code: Status code
        language: Language code (or None for default)

    Returns:
        str: Translated error message
    """
    return _translator.get_translation(status_code, language)


def set_default_language(language: str) -> None:
    """
    Set default language for error messages

    Args:
        language: Language code
    """
    _translator.set_default_language(language)


def add_translation(status_code: int, language: str, translation: str) -> None:
    """
    Add a new translation for a status code

    Args:
        status_code: Status code
        language: Language code
        translation: Translated message
    """
    _translator.add_translation(status_code, language, translation)