from __future__ import annotations

from typing import Any, Dict, Optional


def _safe_float(value: Any, field_name: str, warning: list[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except Exception:
        warning.append(f"Invalid {field_name} value ignored: {value!r}.")
        return None


def classify_conversion_efficiency(efficiency_percent: Optional[float]) -> str:
    """Classify CH4 conversion efficiency using internal BioPot-Gas thresholds.

    Thresholds:
    - < 50%: low experimental conversion
    - 50% to < 80%: intermediate conversion
    - 80% to 100%: high conversion
    - > 100%: review experimental basis, units, or input composition

    These thresholds are internal classification criteria and are not intended
    to represent external regulatory or universal validation standards.
    """
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
    warnings: list[str] = []

    exp_ch4 = _safe_float(experimental_ch4_nm3, "experimental_CH4_Nm3", warnings)
    exp_biogas = _safe_float(experimental_biogas_nm3, "experimental_biogas_Nm3", warnings)
    exp_ch4_percent = _safe_float(experimental_ch4_percent, "experimental_CH4_percent", warnings)

    signed_error_ch4 = abs_error_ch4 = signed_rel_error_ch4 = rel_error_ch4 = efficiency = None
    if exp_ch4 is not None:
        signed_error_ch4 = exp_ch4 - theoretical_ch4_nm3
        abs_error_ch4 = abs(signed_error_ch4)
        signed_rel_error_ch4 = (
            signed_error_ch4 / theoretical_ch4_nm3 * 100.0
            if theoretical_ch4_nm3
            else None
        )
        rel_error_ch4 = (
            abs(signed_rel_error_ch4)
            if signed_rel_error_ch4 is not None
            else None
        )
        efficiency = exp_ch4 / theoretical_ch4_nm3 * 100.0 if theoretical_ch4_nm3 else None

    signed_error_biogas = abs_error_biogas = signed_rel_error_biogas = rel_error_biogas = None
    if exp_biogas is not None:
        signed_error_biogas = exp_biogas - theoretical_biogas_nm3
        abs_error_biogas = abs(signed_error_biogas)
        signed_rel_error_biogas = (
            signed_error_biogas / theoretical_biogas_nm3 * 100.0
            if theoretical_biogas_nm3
            else None
        )
        rel_error_biogas = (
            abs(signed_rel_error_biogas)
            if signed_rel_error_biogas is not None
            else None
        )

    theoretical_ch4_percent = theoretical_ch4_nm3 / theoretical_biogas_nm3 * 100.0 if theoretical_biogas_nm3 else None
    ch4_percent_deviation = None
    if exp_ch4_percent is not None and theoretical_ch4_percent is not None:
        ch4_percent_deviation = exp_ch4_percent - theoretical_ch4_percent

    if exp_ch4 is None and exp_biogas is None and exp_ch4_percent is None:
        warnings.append("Preencher dados experimentais para validação.")
    elif efficiency is not None and efficiency > 100.0:
        warnings.append("Eficiência acima de 100%. Verificar base experimental, unidade ou composição informada.")

    warning = " ".join(warnings)

    return {
        "absolute_error_CH4_Nm3": abs_error_ch4,
        "signed_error_CH4_Nm3": signed_error_ch4,
        "relative_error_CH4_percent": rel_error_ch4,
        "signed_relative_error_CH4_percent": signed_rel_error_ch4,
        "conversion_efficiency_percent": efficiency,
        "absolute_error_biogas_Nm3": abs_error_biogas,
        "signed_error_biogas_Nm3": signed_error_biogas,
        "relative_error_biogas_percent": rel_error_biogas,
        "signed_relative_error_biogas_percent": signed_rel_error_biogas,
        "CH4_percent_deviation": ch4_percent_deviation,
        "validation_status": classify_conversion_efficiency(efficiency),
        "warning": warning,
        "validation_basis_note": (
            "conversion_efficiency_percent is calculated as experimental CH4_Nm3 "
            "divided by theoretical CH4_Nm3. Error fields are signed deviations "
            "computed as experimental minus theoretical values."
        ),
    }
