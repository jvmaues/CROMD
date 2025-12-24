import math
from haversine import haversine, Unit
import matplotlib.pyplot as plt


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

    # N: conjunto de sensores sem a base (vértice 0)
    N = [v for v in V if v != 0]

    # Viz: vizinhança de cobertura
    # Para cada sensor i, Viz[i] contém os sensores j que estão a uma distância
    # menor que o raio de cobertura de i
    # IMPORTANTE: A base (vértice 0) não pode pertencer a nenhuma vizinhança
    Viz = []
    for i in V:
        neighbors = []
        _, _, radius = sensors[i]
        # if i != 0:
        #     radius = 202.0  # Raio fixo para sensores diferentes da base
        # print( f"Sensor {i}: raio de cobertura = {radius:.4f}" )

        # Iterar apenas sobre sensores em N (excluindo a base)
        for j in N:
            if i != j:
                dist = calc_distance(i, j)
                if dist <= radius:
                    neighbors.append(j)
        Viz.append(neighbors)

    return {
        'V': V,
        'N': N,
        'A': A,
        'd': d,
        'C': C,
        'K': K,
        'Viz': Viz,
        'sensors': sensors
    }


def plot_instance_routes(data, result, show_coverage=False, figsize=(8, 6), title=None):
    sensors = data.get("sensors")
    if sensors is None:
        raise ValueError("Instance data must include 'sensors' for plotting.")

    coords = [(x, y) for x, y, _ in sensors]
    V_list = data.get("V", list(range(len(coords))))
    N_list = data.get("N", [v for v in V_list if v != 0])

    fig, ax = plt.subplots(figsize=figsize)

    xs = [coords[i][0] for i in N_list]
    ys = [coords[i][1] for i in N_list]
    ax.scatter(xs, ys, s=30, c="#1f77b4", label="Sensors")

    if 0 in V_list:
        ax.scatter([coords[0][0]], [coords[0][1]], s=60, c="#d62728", marker="s", label="Base")

    for i in V_list:
        ax.text(coords[i][0], coords[i][1], str(i), fontsize=8, ha="left", va="bottom")

    if show_coverage:
        for i in N_list:
            _, _, radius = sensors[i]
            circ = plt.Circle((coords[i][0], coords[i][1]), radius, color="#1f77b4", alpha=0.08, fill=True)
            ax.add_patch(circ)

    routes = result.get("routes", []) if result else []
    colors = ["#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    for idx, route in enumerate(routes):
        if not route or len(route) < 2:
            continue
        color = colors[idx % len(colors)]
        for a, b in zip(route[:-1], route[1:]):
            xa, ya = coords[a]
            xb, yb = coords[b]
            ax.plot([xa, xb], [ya, yb], color=color, linewidth=2, alpha=0.9)

    ax.set_aspect("equal", adjustable="datalim")
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.5)
    plt.show()


def plot_instance(data, show_coverage=False, figsize=(8, 6), title=None):
    sensors = data.get("sensors")
    if sensors is None:
        raise ValueError("Instance data must include 'sensors' for plotting.")

    coords = [(x, y) for x, y, _ in sensors]
    V_list = data.get("V", list(range(len(coords))))
    N_list = data.get("N", [v for v in V_list if v != 0])

    fig, ax = plt.subplots(figsize=figsize)

    xs = [coords[i][0] for i in N_list]
    ys = [coords[i][1] for i in N_list]
    ax.scatter(xs, ys, s=30, c="#1f77b4", label="Sensors")

    if 0 in V_list:
        ax.scatter([coords[0][0]], [coords[0][1]], s=60, c="#d62728", marker="s", label="Base")

    for i in V_list:
        ax.text(coords[i][0], coords[i][1], str(i), fontsize=8, ha="left", va="bottom")

    if show_coverage:
        for i in N_list:
            _, _, radius = sensors[i]
            circ = plt.Circle((coords[i][0], coords[i][1]), radius, color="#1f77b4", alpha=0.08, fill=True)
            ax.add_patch(circ)

    ax.set_aspect("equal", adjustable="datalim")
    if title:
        ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.5)
    plt.show()



def compute_route_distance(route, d):
    dist = 0.0
    for a, b in zip(route[:-1], route[1:]):
        if (a, b) not in d:
            raise KeyError(f"Arc ({a},{b}) not in distance map")
        dist += d[(a, b)]
    return dist


def print_instance(DATA):
    print("=== Dados da Instância ===")
    print(f"V (sensores): {DATA['V']}")
    print(f"\nNúmero de arcos: {len(DATA['A'])}")
    print(f"Primeiros 10 arcos: {DATA['A'][:10]}")
    print(f"\nC (capacidade dos drones): {DATA['C']:.4f}")
    print(f"K (número de drones): {DATA['K']}")
    print(f"\nViz (vizinhança de cobertura):")
    
    for i, neighbors in enumerate(DATA['Viz']):
        print(f"  Sensor {i}: {neighbors}")
    
    print(f"\nExemplos de distâncias:")
    for arc in DATA['A']:
        print(f"  d{arc} = {DATA['d'][arc]:.4f}")


def print_solution(DATA, result):

    d = DATA['d']
    C = DATA['C']

    print("======== Instância ========")
    print(f"Número de sensores (|V|): {len(DATA['V'])}")
    print(f"Número de drones (K): {DATA['K']}")
    print(f"Capacidade dos drones (C): {C:.4f}")
    print("\n")
    print("==== Resultado da Solucao ====")
    print(f"Status: {result['status_string']}")
    if result["objective_T"] is not None:
        print(f"Makespan (T): {result['objective_T']:.4f}")
        print(f"Drones usados: {len(result['used_drones'])}")
        used = result.get("used_drones", [])
        routes = result.get("routes", [])
        for i, route in enumerate(routes):
            drone_id = used[i] if i < len(used) else i
            dist = compute_route_distance(route, d)
            print(f"  Rota drone {drone_id}: {route} (dist={dist:.4f})")
    print(f"Tempo de execucao (s): {result['runtime_sec']:.2f}")



if __name__ == '__main__':
    # Exemplo de uso
    path = "../data/toy_instances/toy_large.csv"
    data = read_instance(path, distance_type='euclidean')
    # print_instance(data)
