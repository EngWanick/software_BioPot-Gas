from __future__ import annotations

from pathlib import Path

from .excel_reader import read_biopotgas_excel
from .excel_utils import to_bool
from .report import result_to_dict
from .core import calculate_biogas_from_components
from .constants import MOLECULAR_WEIGHTS_KG_PER_KMOL, CH4_LHV_MJ_PER_NM3, KWH_PER_MJ
from .input_units import (
    basis_time_mode,
    convert_component_flows_to_internal_molar_basis,
    convert_water_to_internal_molar_basis,
    internal_molar_basis_label,
)


def calculate_from_excel(path: str | Path, sheet_name: str = "01_INPUTS") -> dict:
    data = read_biopotgas_excel(path, sheet_name=sheet_name)
    warnings: list[str] = []

    def get_global_parameter(name: str, default):
        if name not in data.global_parameters:
            warnings.append(
                f"Global parameter {name!r} not found; using default {default!r}."
            )
            return default

        return data.global_parameters[name]

    input_basis_type = str(get_global_parameter("input_basis_type", "molar")).strip().lower()
    input_unit = str(get_global_parameter("input_unit", "kmol")).strip()
    carbon_conversion = float(get_global_parameter("carbon_conversion", 0.95))
    normal_temperature_C = float(get_global_parameter("normal_temperature_C", 0.0))
    normal_pressure_kPa = float(get_global_parameter("normal_pressure_kPa", 101.325))
    ch4_lhv_mj_per_Nm3 = CH4_LHV_MJ_PER_NM3
    kwh_per_mj = KWH_PER_MJ

    components = convert_component_flows_to_internal_molar_basis(
        data.components,
        input_basis_type=input_basis_type,
        input_unit=input_unit,
    )

    water_available_mol = convert_water_to_internal_molar_basis(
        data.water_available_mol,
        input_basis_type=input_basis_type,
        input_unit=input_unit,
)

    result = calculate_biogas_from_components(
        components,
        carbon_conversion=carbon_conversion,
    )

    output = result_to_dict(
        result,
        normal_temperature_C=normal_temperature_C,
        normal_pressure_kPa=normal_pressure_kPa,
        ch4_lhv_mj_per_Nm3=ch4_lhv_mj_per_Nm3,
        kwh_per_mj=kwh_per_mj,
    )

    net_water_balance_mol = water_available_mol - output["H2O_mol"]

    time_mode = basis_time_mode(input_unit)
    internal_basis = internal_molar_basis_label(input_unit)

    output["input_basis_type"] = input_basis_type
    output["input_unit"] = input_unit
    output["internal_molar_basis"] = internal_molar_basis_label(input_unit)
    output["basis_time_mode"] = basis_time_mode(input_unit)
    output["water_available_mol"] = water_available_mol
    output["net_water_balance_mol"] = net_water_balance_mol
    output["net_water_balance_mass"] = (
        net_water_balance_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["H2O"]
    )
    output["net_water_balance_note"] = (
        "net_water_balance_mol is calculated as water_available_mol minus H2O_mol. "
        "Positive values indicate water surplus. Negative values indicate water deficit."
    )

    output["number_of_components_read"] = len(data.components)
    output["carbon_conversion"] = carbon_conversion
    output["normal_temperature_C"] = normal_temperature_C
    output["normal_pressure_kPa"] = normal_pressure_kPa
    output["CH4_LHV_MJ_per_Nm3"] = ch4_lhv_mj_per_Nm3
    output["kWh_per_MJ"] = kwh_per_mj
    output["molar_basis_note"] = (
        "Molar quantities use the same basis as the input molar_flow. "
        "Use kmol as input basis to interpret mass outputs as kg and volume outputs as Nm3."
    )
    output["carbon_conversion_note"] = (
        "carbon_conversion represents the fraction of degradable organic carbon "
        "allocated to gas generation. The remaining degradable organic carbon is "
        "treated as associated with biological cell growth."
    )
    output["output_molar_unit"] = internal_basis
    output["output_mass_unit"] = "kg/h" if time_mode == "rate" else "kg"
    output["output_volume_unit"] = "Nm³/h" if time_mode == "rate" else "Nm³"
    output["output_energy_MJ_unit"] = "MJ/h" if time_mode == "rate" else "MJ"
    output["output_energy_kWh_unit"] = "kW" if time_mode == "rate" else "kWh"
    output["calculation_status"] = "Calculated successfully"
    output["warnings"] = "; ".join(warnings)

    return output