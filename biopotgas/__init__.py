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
    read_biopotgas_excel,
    calculate_from_excel,
    write_outputs_to_excel,
)

__version__ = "0.6.1"
