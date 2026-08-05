from __future__ import annotations

from .core import BiogasResult


MOLECULAR_WEIGHTS_KG_PER_KMOL = {
    "CH4": 16.043,
    "CO2": 44.010,
    "NH3": 17.031,
    "H2S": 34.081,
    "C": 12.011,
    "H2O": 18.015,
}


def molar_volume_m3_per_kmol(
    temperature_C: float = 0.0,
    pressure_kPa: float = 101.325,
) -> float:
    """Calculate molar volume in m3 per kmol using the ideal gas equation."""

    if pressure_kPa <= 0:
        raise ValueError("pressure_kPa must be positive.")

    R_kPa_m3_per_kmol_K = 8.314462618
    temperature_K = temperature_C + 273.15

    if temperature_K <= 0:
        raise ValueError("temperature_C must be above absolute zero.")

    return R_kPa_m3_per_kmol_K * temperature_K / pressure_kPa


def result_to_dict(
    result: BiogasResult,
    normal_temperature_C: float = 0.0,
    normal_pressure_kPa: float = 101.325,
    ch4_lhv_mj_per_Nm3: float = 35.8,
    kwh_per_mj: float = 0.277778,
) -> dict:
    """Convert result to molar, mass, volumetric and energy outputs."""

    vm = molar_volume_m3_per_kmol(normal_temperature_C, normal_pressure_kPa)

    ch4_nm3 = result.ch4_mol * vm
    co2_nm3 = result.co2_mol * vm
    nh3_nm3 = result.nh3_mol * vm
    h2s_nm3 = result.h2s_mol * vm
    total_nm3 = ch4_nm3 + co2_nm3 + nh3_nm3 + h2s_nm3

    ch4_energy_mj = ch4_nm3 * ch4_lhv_mj_per_Nm3
    ch4_energy_kwh = ch4_energy_mj * kwh_per_mj

    ch4_to_co2 = result.ch4_mol / result.co2_mol if result.co2_mol > 0 else None

    return {
        "CH4_mol": result.ch4_mol,
        "CO2_mol": result.co2_mol,
        "NH3_mol": result.nh3_mol,
        "H2S_mol": result.h2s_mol,
        "H2O_mol": result.h2o_mol,
        "total_gas_mol": result.total_gas_mol,
        "CH4_mol_fraction": result.methane_fraction_mol,
        "H2O_balance_note": (
            "Positive H2O_mol indicates net water consumption. "
            "Negative H2O_mol indicates net water production."
        ),
        "inert_carbon_mol": result.inert_carbon_mol,
        "CH4_mass": result.ch4_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["CH4"],
        "CO2_mass": result.co2_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["CO2"],
        "NH3_mass": result.nh3_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["NH3"],
        "H2S_mass": result.h2s_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["H2S"],
        "H2O_mass": result.h2o_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["H2O"],
        "inert_carbon_mass": result.inert_carbon_mol * MOLECULAR_WEIGHTS_KG_PER_KMOL["C"],
        "molar_volume_Nm3_per_kmol": vm,
        "CH4_Nm3": ch4_nm3,
        "CO2_Nm3": co2_nm3,
        "NH3_Nm3": nh3_nm3,
        "H2S_Nm3": h2s_nm3,
        "total_biogas_Nm3": total_nm3,
        "CH4_vol_percent": (ch4_nm3 / total_nm3 * 100.0) if total_nm3 > 0 else 0.0,
        "CH4_energy_LHV_MJ": ch4_energy_mj,
        "CH4_energy_LHV_kWh": ch4_energy_kwh,
        "CH4_to_CO2_molar_ratio": ch4_to_co2,
    }


def print_result(result: BiogasResult) -> None:
    """Print a readable summary for a raw BiogasResult.

    This is a manual/reporting utility and is not used by the Excel pipeline.
    Use result_to_dict() when structured output is required.
    """
    data = result_to_dict(result)
    for key, value in data.items():
        if value is None:
            print(f"{key}: None")
        elif isinstance(value, (int, float)):
            print(f"{key}: {value:.6g}")
        else:
            print(f"{key}: {value}")
