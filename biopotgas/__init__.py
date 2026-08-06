"""
BioPot-Gas

Software independente para estimativa, análise energética e validação experimental
do potencial teórico de biogás e biometano a partir de substratos orgânicos.
"""

from .core import (
    BiogasResult,
    ElementalComposition,
    calculate_biogas_from_elements,
    calculate_biogas_from_formula,
    calculate_biogas_from_components,
)
from .excel_reader import (
    ExcelInputData,
    read_biopotgas_excel,
)
from .excel_writer import write_outputs_to_excel
from .pipeline import calculate_from_excel
from .io import read_components_csv
from .report import result_to_dict

__version__ = "0.6.1"
