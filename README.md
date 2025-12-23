# CROMD - Cobertura de Sensores com Drones

Leitor de instâncias para o problema de cobertura de sensores utilizando drones com múltiplas métricas de distância.

## Uso Básico

```python
from instance_reader import read_instance

# Distância Euclidiana (padrão - coordenadas planas)
data = read_instance('caminho/arquivo.txt')

# Distância Haversine (coordenadas GPS: latitude/longitude)
data = read_instance('caminho/arquivo.txt', distance_type='haversine')

# Distância Manhattan (grade)
data = read_instance('caminho/arquivo.txt', distance_type='manhattan')
```

## Tipos de Distância

### 1. Euclidiana (padrão)
- **Uso**: Coordenadas em um plano cartesiano (metros, km, unidades arbitrárias)
- **Fórmula**: √((x₂-x₁)² + (y₂-y₁)²)
- **Quando usar**: Coordenadas planas, mapas em pequena escala

### 2. Haversine
- **Uso**: Coordenadas GPS (latitude/longitude)
- **Fórmula**: Considera a curvatura da Terra
- **Retorno**: Distância em quilômetros
- **Quando usar**: Coordenadas geográficas reais (GPS), mapas de grande escala
- **Exemplo**: latitude = -22.9068, longitude = -43.1729 (Rio de Janeiro)

### 3. Manhattan
- **Uso**: Movimento em grade (apenas horizontal/vertical)
- **Fórmula**: |x₂-x₁| + |y₂-y₁|
- **Quando usar**: Menos comum para drones, útil para cenários em grade

## Formato do Arquivo de Instância

```
12
0 0 0
1 0 1
2 0 1
...
```

- **Linha 1**: Número total de sensores (incluindo a base)
- **Linha 2**: Base com coordenadas (x, y) e raio de cobertura
- **Linhas seguintes**: Cada sensor com coordenadas (x, y) e raio de cobertura

## Estrutura de Dados Retornada

```python
{
    'V': [0, 1, 2, ...],              # Lista de índices dos sensores
    'A': [(0,1), (0,2), ...],         # Arcos do grafo completo
    'd': {(0,1): 1.0, ...},           # Dicionário de distâncias
    'C': 7.2111,                       # Capacidade dos drones
    'K': 6,                            # Número de drones
    'Viz': [[], [0,2,5], ...]         # Vizinhança de cobertura
}
```

### Detalhes:
- **V**: Lista de sensores incluindo a base (sensor 0)
- **A**: Todas as tuplas (i,j) do grafo completo
- **d**: Distância entre cada par de sensores
- **C**: 2 × distância do sensor mais distante da base
- **K**: ⌊n/2⌋ onde n é o número de sensores
- **Viz**: Para cada sensor i, lista de sensores j cobertos pelo raio de i

## Exemplos

Execute o script de teste para ver as diferentes métricas em ação:

```bash
python3 test_distances.py
```

## Requisitos

- Python 3.9+
- Biblioteca padrão (math)
