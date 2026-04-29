from abc import ABC, abstractmethod
from datetime import date
from typing import Optional


class LicenseSource(ABC):
    source_state: str
    source_agency: str
    license_type_codes: tuple[str, ...]

    @abstractmethod
    def fetch(self, since: Optional[date] = None) -> list[dict]:
        """Return source-native records shaped for the normalizer."""
