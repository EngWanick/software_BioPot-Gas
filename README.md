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

## Escopo e hipóteses operacionais atuais

A versão v0.6.1 mantém o modelo numérico da v0.6 e adiciona estabilizações de pipeline, testes automatizados, validações defensivas e metadados de interpretação dos resultados.

O parâmetro `molar_flow` define a base molar usada no cálculo. As grandezas molares mantêm a mesma base da entrada. Quando `molar_flow` é informado em kmol, as saídas de massa podem ser interpretadas em kg e as saídas volumétricas em Nm³.

O parâmetro `carbon_conversion` representa a fração do carbono orgânico degradável destinada à geração de gases. A fração complementar do carbono orgânico degradável é tratada como associada ao crescimento biológico celular.

A planilha Excel é tratada como template controlado. A leitura atual espera que os parâmetros globais, cabeçalhos e abas sigam a estrutura do arquivo `BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx`.

A aba `06_VALIDATION_BENCHMARKS` é preservada na geração da planilha calculada. Seu conteúdo de benchmark não é recalculado pelo pipeline Python nesta versão.

Limitações conhecidas:
- O consumo ou produção líquida de água no balanço de Buswell ainda não é calculado nem reportado explicitamente.
- A conversão automática de unidades declaradas na planilha ainda não está implementada.
- A separação entre `excel_reader.py` e `excel_writer.py` ainda contém sobreposição legada e será consolidada em refatoração futura.

## Benchmarks incluídos

- Controle estequiométrico e volumétrico com celulose, comparado ao valor teórico de 415 mL CH4/g VS.
- Biodegradabilidade experimental de FW, DIW, BW e CBW com dados de Llanos-Lizcano et al. 2024.
- Notas metodológicas baseadas em Nielfa et al. 2015, Angelidaki et al. 2009 e Zhang et al. 2021.
