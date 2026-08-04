# BioPot-Gas v0.6

Software independente para estimativa, análise energética, validação experimental e validação técnico-científica do potencial teórico de biogás e biometano a partir de substratos orgânicos.

## Novidade da versão v0.6

A versão v0.6 preserva o núcleo computacional da v0.5 e adiciona a aba `06_VALIDATION_BENCHMARKS`, com evidências de validação matemática, volumétrica, experimental e metodológica.

## Arquivo principal

Use a planilha:

`BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx`

## Execução

```bash
pip install -r requirements.txt
python run_from_excel.py
```

O programa gera uma nova planilha com o sufixo `_calculated.xlsx`.

## Abas da planilha

- `00_INFORMATIVO`
- `01_INPUTS`
- `02_OUTPUTS`
- `03_COMPONENT_DATABASE`
- `04_EXPERIMENTAL_VALIDATION`
- `05_METHOD_NOTES`
- `06_VALIDATION_BENCHMARKS`

## Benchmarks incluídos

- Controle estequiométrico e volumétrico com celulose, comparado ao valor teórico de 415 mL CH4/g VS.
- Biodegradabilidade experimental de FW, DIW, BW e CBW com dados de Llanos-Lizcano et al. 2024.
- Notas metodológicas baseadas em Nielfa et al. 2015, Angelidaki et al. 2009 e Zhang et al. 2021.
