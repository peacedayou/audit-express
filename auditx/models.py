from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Severity(IntEnum):
    INFORMATIONAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return {0: "Information", 1: "Faible", 2: "Moyenne", 3: "Élevée", 4: "Critique"}[self.value]

    @classmethod
    def from_slither(cls, impact: str) -> Severity:
        return {
            "high": cls.HIGH,
            "medium": cls.MEDIUM,
            "low": cls.LOW,
            "informational": cls.INFORMATIONAL,
            "optimization": cls.INFORMATIONAL,
        }.get(impact.lower(), cls.INFORMATIONAL)


@dataclass(frozen=True)
class Location:
    file: str
    line: int | None = None

    def __str__(self) -> str:
        return f"{self.file}:{self.line}" if self.line else self.file


@dataclass
class Finding:
    detector: str
    title: str
    severity: Severity
    description: str
    recommendation: str = ""
    confidence: str = "Moyenne"
    source: str = "slither"
    locations: list[Location] = field(default_factory=list)
    id: str = ""


@dataclass
class SuiteSummary:
    passed: int = 0
    failed: int = 0
    ran: bool = False
