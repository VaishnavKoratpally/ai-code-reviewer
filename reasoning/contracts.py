from dataclasses import dataclass

@dataclass
class Issue:
    name: str
    evidence: str
    explanation: str

@dataclass
class ArchitectureAnalysis:
    architecture_summary: str
    design_smells: list[Issue]
    scalability_risks: list[Issue]
