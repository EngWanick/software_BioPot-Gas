from __future__ import annotations

from typing import Any, Dict, Optional


def _safe_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        return None


def classify_conversion_efficiency(efficiency_percent: Optional[float]) -> str:
    if efficiency_percent is None:
        return "Não calculado"
    if efficiency_percent < 50.0:
        return "Baixa conversão experimental"
    if efficiency_percent < 80.0:
        return "Conversão intermediária"
    if efficiency_percent <= 100.0:
        return "Conversão elevada"
    return "Verificar base experimental ou composição de entrada"


def compare_experimental_to_theoretical(
    experimental_ch4_nm3: Any,
    experimental_biogas_nm3: Any,
    experimental_ch4_percent: Any,
    theoretical_ch4_nm3: float,
    theoretical_biogas_nm3: float,
) -> Dict[str, Any]:
    exp_ch4 = _safe_float(experimental_ch4_nm3)
    exp_biogas = _safe_float(experimental_biogas_nm3)
    exp_ch4_percent = _safe_float(experimental_ch4_percent)

    abs_error_ch4 = rel_error_ch4 = efficiency = None
    if exp_ch4 is not None:
        abs_error_ch4 = exp_ch4 - theoretical_ch4_nm3
        rel_error_ch4 = abs_error_ch4 / theoretical_ch4_nm3 * 100.0 if theoretical_ch4_nm3 else None
        efficiency = exp_ch4 / theoretical_ch4_nm3 * 100.0 if theoretical_ch4_nm3 else None

    abs_error_biogas = rel_error_biogas = None
    if exp_biogas is not None:
        abs_error_biogas = exp_biogas - theoretical_biogas_nm3
        rel_error_biogas = abs_error_biogas / theoretical_biogas_nm3 * 100.0 if theoretical_biogas_nm3 else None

    theoretical_ch4_percent = theoretical_ch4_nm3 / theoretical_biogas_nm3 * 100.0 if theoretical_biogas_nm3 else None
    ch4_percent_deviation = None
    if exp_ch4_percent is not None and theoretical_ch4_percent is not None:
        ch4_percent_deviation = exp_ch4_percent - theoretical_ch4_percent

    warning = ""
    if exp_ch4 is None and exp_biogas is None and exp_ch4_percent is None:
        warning = "Preencher dados experimentais para validação."
    elif efficiency is not None and efficiency > 100.0:
        warning = "Eficiência acima de 100%. Verificar base experimental, unidade ou composição informada."

    return {
        "absolute_error_CH4_Nm3": abs_error_ch4,
        "relative_error_CH4_percent": rel_error_ch4,
        "conversion_efficiency_percent": efficiency,
        "absolute_error_biogas_Nm3": abs_error_biogas,
        "relative_error_biogas_percent": rel_error_biogas,
        "CH4_percent_deviation": ch4_percent_deviation,
        "validation_status": classify_conversion_efficiency(efficiency),
        "warning": warning,
    }
