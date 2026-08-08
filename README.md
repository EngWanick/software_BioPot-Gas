# BioPot-Gas v0.6

Software independente para estimativa, análise energética, validação experimental e validação técnico-científica do potencial teórico de biogás e biometano a partir de substratos orgânicos.

## Novidade da versão v0.6.1

A versão v0.6.0 preserva o núcleo computacional da v0.5 e adiciona a aba `06_VALIDATION_BENCHMARKS`, com evidências de validação matemática, volumétrica, experimental e metodológica.

A versão v0.6.1 consolida a estrutura de entrada e saída do BioPot-Gas dentro
da série v0.6. Ela mantém a camada de validação técnico-científica introduzida
na v0.6 e adiciona suporte ao balanço de água, bases globais de entrada no Excel,
conversão de entradas mássicas, padronização de unidades de saída e suporte CSV
para linhas de água livre.

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

A classificação da eficiência de conversão experimental usa limites internos do BioPot-Gas: abaixo de 50% indica baixa conversão experimental; de 50% a abaixo de 80% indica conversão intermediária; de 80% a 100% indica conversão elevada; acima de 100% indica necessidade de verificar base experimental, unidade ou composição de entrada. Esses limites são critérios internos de triagem e não representam norma regulatória ou padrão universal.

O parâmetro `carbon_conversion` representa a fração do carbono orgânico degradável destinada à geração de gases. A fração complementar do carbono orgânico degradável é tratada como associada ao crescimento biológico celular.

A planilha Excel é tratada como template controlado. A leitura atual espera que os parâmetros globais, cabeçalhos e abas sigam a estrutura do arquivo `BioPot-Gas_Input_Template_v6_validation_benchmarks.xlsx`.

A aba `06_VALIDATION_BENCHMARKS` é preservada na geração da planilha calculada. Seu conteúdo de benchmark não é recalculado pelo pipeline Python nesta versão.

Limitações conhecidas:
- A expansão da aba `03_COMPONENT_DATABASE` está fora do escopo desta versão e
  será revisada separadamente.

## Base de entrada no Excel

O template Excel usa uma base de entrada global para a tabela de componentes.

Os campos `input_basis_type` e `input_unit` definem como todos os valores em
`input_quantity` são interpretados. As bases atualmente suportadas são:

- `molar`: `kmol`, `mol`, `kmol/h`, `mol/h`
- `mass`: `kg`, `g`, `ton`, `kg/h`, `g/h`, `ton/h`

O valor de `input_quantity` pode representar uma quantidade total ou uma vazão,
e pode estar expresso em base molar ou mássica. Unidades contendo `/h` são
interpretadas como vazões; unidades sem `/h` são interpretadas como quantidades
totais. A base e a unidade selecionadas são aplicadas globalmente a todas as
linhas ativas da tabela de componentes.

O modelo converte todas as entradas do Excel para uma base molar interna antes
de executar o cálculo estequiométrico de Buswell:

- entradas em quantidade são convertidas para `kmol`
- entradas em vazão são convertidas para `kmol/h`

Para entradas em base mássica, a massa molar de cada componente é calculada a
partir de sua composição elementar (`C`, `H`, `O`, `N`, `S`). O template Excel
não permite misturar unidades de entrada diferentes entre linhas da tabela de
componentes.

## Balanço de água

O BioPot-Gas calcula o termo estequiométrico de água associado à equação de
Buswell e reporta os campos `H2O_mol`, `H2O_mass` e `H2O_balance_note`.

A convenção adotada é:

- `H2O_mol > 0`: demanda líquida de água;
- `H2O_mol < 0`: produção líquida de água.

O template Excel também permite informar água livre disponível por meio de uma
linha especial na tabela de componentes. Linhas com `component_name` igual a
`WATER`, `H2O`, `ÁGUA` ou `AGUA`, ou com `input_mode = WATER`, são interpretadas
como água disponível no sistema. Essas linhas não entram no cálculo de Buswell
como componentes degradáveis; sua quantidade é usada apenas no balanço de água.

O pipeline reporta `water_available_mol`, `net_water_balance_mol`,
`net_water_balance_mass` e `net_water_balance_note`.

## Unidades de saída

As unidades de saída são padronizadas por dimensão física e escritas na coluna
de unidade da aba `02_OUTPUTS`.

Para entradas em quantidade, os resultados são reportados em `kmol`, `kg`,
`Nm³`, `MJ` e `kWh`. Para entradas em vazão, os resultados são reportados em
`kmol/h`, `kg/h`, `Nm³/h`, `MJ/h` e `kW`.

As unidades de saída não preservam necessariamente a unidade específica de
entrada. Por exemplo, uma entrada em `g` é convertida internamente e as massas
de saída são reportadas em `kg`.

## Carbono inerte reportado

O campo `inert_carbon_mol` representa apenas a fração não convertida do carbono
degradável controlada por `carbon_conversion`.

Componentes marcados como não degradáveis são excluídos do cálculo de Buswell e
não contribuem para `inert_carbon_mol`. Portanto, esse campo não deve ser
interpretado como todo o carbono fisicamente inerte presente na alimentação.

## API CSV para uso sem o template Excel

Além do template Excel, o BioPot-Gas pode ser usado por uma API CSV simples.
Esse caminho é destinado a uso programático ou automação externa, mantendo o
núcleo computacional independente do arquivo `.xlsx`.

O leitor CSV aceita o contrato atual de entrada por meio de `component_name`,
`input_quantity`, `input_basis_type` e `input_unit`, com a mesma lógica de
conversão usada no Excel. Também mantém compatibilidade com arquivos antigos
baseados em `name` e `molar_flow`.

As bases suportadas são:

- `molar`: `kmol`, `mol`, `kmol/h`, `mol/h`
- `mass`: `kg`, `g`, `ton`, `kg/h`, `g/h`, `ton/h`

Linhas com `component_name` ou `name` igual a `WATER`, `H2O`, `ÁGUA` ou `AGUA`,
ou com `input_mode = WATER`, são interpretadas como água livre disponível. Essas
linhas são separadas dos componentes enviados ao cálculo de Buswell.

Arquivos de exemplo:

- `examples/example_components.csv`
- `examples/example_csv.py`

## Aba `06_VALIDATION_BENCHMARKS`

A aba `06_VALIDATION_BENCHMARKS` é mantida no template Excel como camada de
documentação técnico-científica e comparação com benchmarks. No pipeline Python
atual, essa aba não é recalculada nem reescrita diretamente; seu conteúdo é
preservado ao gerar o arquivo `_calculated.xlsx`.

Os valores nela registrados devem ser interpretados como benchmarks documentais
do modelo.

## Benchmarks incluídos

- Controle estequiométrico e volumétrico com celulose, comparado ao valor teórico de 415 mL CH4/g VS.
- Biodegradabilidade experimental de FW, DIW, BW e CBW com dados de Llanos-Lizcano et al. 2024.
- Notas metodológicas baseadas em Nielfa et al. 2015, Angelidaki et al. 2009 e Zhang et al. 2021.
- Fórmulas genéricas como `PROTEIN_GENERIC`, `LIGNIN_GENERIC`,
  `BIOMASS_GENERIC` e `ENZYME_GENERIC` tratadas como composições
  representativas para estimativas preliminares, não como análises elementares
  específicas de uma amostra. Referência: Wooley and Putsche (1996), NREL.