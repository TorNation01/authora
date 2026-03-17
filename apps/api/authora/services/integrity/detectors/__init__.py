"""Integrity issue detectors."""

from authora.services.integrity.detectors.base import BaseDetector
from authora.services.integrity.detectors.fiction import FictionDetector
from authora.services.integrity.detectors.general import GeneralDetector
from authora.services.integrity.detectors.memoir import MemoirDetector
from authora.services.integrity.detectors.nonfiction import NonfictionDetector
from authora.services.integrity.detectors.workbook import WorkbookDetector

DETECTORS = {
    "general": GeneralDetector,
    "fiction": FictionDetector,
    "nonfiction": NonfictionDetector,
    "memoir": MemoirDetector,
    "workbook": WorkbookDetector,
}


def get_detectors_for_project(project_type: str, guidance_mode: str) -> list[type[BaseDetector]]:
    """Return appropriate detectors for project type and guidance mode.
    Freeform: only GeneralDetector (minimal, non-policing).
    """
    if guidance_mode == "freeform":
        return [GeneralDetector]

    always = [GeneralDetector]
    if project_type == "fiction":
        always.append(FictionDetector)
    elif project_type == "nonfiction":
        always.append(NonfictionDetector)
    elif project_type == "memoir":
        always.append(MemoirDetector)
    elif project_type == "workbook":
        always.append(WorkbookDetector)
    elif project_type == "hybrid":
        always.extend([NonfictionDetector, MemoirDetector])
    return always
