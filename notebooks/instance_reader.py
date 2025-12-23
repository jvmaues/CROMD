import math
from haversine import haversine, Unit


def euclidean_distance(x1, y1, x2, y2):
    """
    Calcula a distância euclidiana entre dois pontos.

    Args:
        x1, y1: Coordenadas do primeiro ponto
        x2, y2: Coordenadas do segundo ponto

    Returns:
        Distância euclidiana
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def manhattan_distance(x1, y1, x2, y2):
    """
    Calcula a distância de Manhattan entre dois pontos.

    Args:
        x1, y1: Coordenadas do primeiro ponto
        x2, y2: Coordenadas do segundo ponto

    Returns:
        Distância de Manhattan
    """
    return abs(x2 - x1) + abs(y2 - y1)


def read_instance(file_path, distance_type='euclidean'):
    """
    Lê uma instância do problema de cobertura de sensores com drones.

    Args:
        file_path: Caminho para o arquivo de instância
        distance_type: Tipo de cálculo de distância ('euclidean', 'haversine', 'manhattan')
                      - 'euclidean': Para coordenadas planas (padrão)
                      - 'haversine': Para coordenadas GPS (lat/lon), retorna distância em km
                      - 'manhattan': Distância em grade (menos comum para drones)

    Returns:
        dict contendo:
            - V: lista de sensores (índices) incluindo a base (sensor 0)
            - A: lista de tuplas (i,j) representando todos os arcos do grafo completo
            - d: dicionário com tuplas (i,j) como chave e distância como valor
            - C: capacidade dos drones (2 × distância do sensor mais distante da base)
            - K: número máximo de drones (metade do número de sensores)
            - Viz: lista de listas com a vizinhança de cobertura de cada sensor
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Primeira linha: número de sensores
    n = int(lines[0].strip())

    # Ler coordenadas e raios de todos os sensores
    sensors = []
    for i in range(1, n + 1):
        parts = lines[i].strip().split()
        x, y, r = float(parts[0]), float(parts[1]), float(parts[2])
        sensors.append((x, y, r))

    # V: lista de sensores (índices de 0 a n-1)
    V = list(range(n))

    # Selecionar função de distância baseada no tipo
    if distance_type == 'haversine':
        def calc_distance(i, j):
            lat1, lon1, _ = sensors[i]
            lat2, lon2, _ = sensors[j]
            return haversine((lat1, lon1), (lat2, lon2), unit=Unit.METERS)
    elif distance_type == 'manhattan':
        def calc_distance(i, j):
            x1, y1, _ = sensors[i]
            x2, y2, _ = sensors[j]
            return manhattan_distance(x1, y1, x2, y2)
    elif distance_type == 'euclidean':
        def calc_distance(i, j):
            x1, y1, _ = sensors[i]
            x2, y2, _ = sensors[j]
            return euclidean_distance(x1, y1, x2, y2)
    else:
        raise ValueError(f"Tipo de distância inválido: {distance_type}. Use 'euclidean', 'haversine' ou 'manhattan'.")

    # A: lista de tuplas (i,j) de todos os arcos do grafo completo
    A = []
    for i in V:
        for j in V:
            if i != j:
                A.append((i, j))

    # d: dicionário com as distâncias
    d = {}
    for (i, j) in A:
        d[(i, j)] = calc_distance(i, j)

    # C: capacidade dos drones = 2 × distância do sensor mais distante da base
    max_distance_from_base = 0.0
    for i in range(1, n):
        dist = calc_distance(0, i)
        if dist > max_distance_from_base:
            max_distance_from_base = dist
    C = 2 * max_distance_from_base

    # K: número de drones = metade do número de sensores
    K = n // 2

    # Viz: vizinhança de cobertura
    # Para cada sensor i, Viz[i] contém os sensores j que estão a uma distância
    # menor que o raio de cobertura de i
    Viz = []
    for i in V:
        neighbors = []
        _, _, radius = sensors[i]
        # if i != 0:
        #     radius = 202.0  # Raio fixo para sensores diferentes da base
        # print( f"Sensor {i}: raio de cobertura = {radius:.4f}" )
        
        for j in V:
            if i != j:
                dist = calc_distance(i, j)
                if dist <= radius:
                    neighbors.append(j)
        Viz.append(neighbors)

    return {
        'V': V,
        'A': A,
        'd': d,
        'C': C,
        'K': K,
        'Viz': Viz,
        'sensors': sensors
    }


if __name__ == '__main__':
    # # Exemplo de uso
    # import sys

    # if len(sys.argv) < 2:
    #     print("Uso: python instance_reader.py <caminho_arquivo_instancia>")
    #     sys.exit(1)

    # instance_file = sys.argv[1]

    path = "data/instances/instancia1Tijuca.csv"
    data = read_instance(path)

    print("=== Dados da Instância ===")
    print(f"V (sensores): {data['V']}")
    print(f"\nNúmero de arcos: {len(data['A'])}")
    print(f"Primeiros 10 arcos: {data['A'][:10]}")
    print(f"\nC (capacidade dos drones): {data['C']:.4f}")
    print(f"K (número de drones): {data['K']}")
    print(f"\nViz (vizinhança de cobertura):")
    for i, neighbors in enumerate(data['Viz']):
        print(f"  Sensor {i}: {neighbors}")
    print(f"\nExemplos de distâncias:")
    for arc in data['A'][:5]:
        print(f"  d{arc} = {data['d'][arc]:.4f}")
