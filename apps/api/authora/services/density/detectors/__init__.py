"""Story Density Engine detectors."""

from authora.services.density.detectors.base import BaseDensityDetector
from authora.services.density.detectors.general import GeneralDensityDetector
from authora.services.density.detectors.fiction import FictionDensityDetector
from authora.services.density.detectors.nonfiction import NonfictionDensityDetector
from authora.services.density.detectors.memoir import MemoirDensityDetector
from authora.services.density.detectors.workbook import WorkbookDensityDetector


def get_density_detectors_for_project(project_type: str, guidance_mode: str) -> list[type[BaseDensityDetector]]:
    """Return density detectors for project type and guidance mode."""
    if guidance_mode == "freeform":
        return [GeneralDensityDetector]

    always = [GeneralDensityDetector]
    if project_type == "fiction":
        always.append(FictionDensityDetector)
    elif project_type == "nonfiction":
        always.append(NonfictionDensityDetector)
    elif project_type == "memoir":
        always.append(MemoirDensityDetector)
    elif project_type == "workbook":
        always.append(WorkbookDensityDetector)
    elif project_type == "hybrid":
        always.extend([NonfictionDensityDetector, MemoirDensityDetector])
    return always
