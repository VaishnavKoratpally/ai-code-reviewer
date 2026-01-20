from dataclasses import dataclass
from typing import List


@dataclass
class ArchitectureAnalysis:
    architecture_summary: str
    design_smells: List[str]
    scalability_risks: List[str]
