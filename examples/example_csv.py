from pathlib import Path

from biopotgas import (
    calculate_biogas_from_components,
    read_components_csv,
    result_to_dict,
)


def main() -> None:
    csv_path = Path(__file__).with_name("example_components.csv")

    components = read_components_csv(csv_path)
    result = calculate_biogas_from_components(components)
    output = result_to_dict(result)

    print("BioPot-Gas CSV example")
    print(f"CH4_Nm3: {output['CH4_Nm3']:.6f}")
    print(f"total_biogas_Nm3: {output['total_biogas_Nm3']:.6f}")


if __name__ == "__main__":
    main()