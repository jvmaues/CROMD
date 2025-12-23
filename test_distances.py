"""
Script para demonstrar o uso de diferentes métricas de distância.
"""
from notebooks.instance_reader import read_instance


def test_euclidean():
    """Testa com distância euclidiana (coordenadas planas)."""
    print("=" * 60)
    print("DISTÂNCIA EUCLIDIANA (Coordenadas Planas)")
    print("=" * 60)

    data = read_instance('example_instance.txt', distance_type='euclidean')

    print(f"Número de sensores: {len(data['V'])}")
    print(f"Capacidade dos drones (C): {data['C']:.4f}")
    print(f"Número de drones (K): {data['K']}")
    print(f"\nExemplos de distâncias:")
    for arc in [(0, 1), (0, 4), (1, 5), (5, 9)]:
        print(f"  d{arc} = {data['d'][arc]:.4f}")
    print()


def test_haversine():
    """Testa com distância de Haversine (coordenadas GPS)."""
    print("=" * 60)
    print("DISTÂNCIA HAVERSINE (Coordenadas GPS - lat/lon)")
    print("=" * 60)
    print("Usando coordenadas próximas ao Rio de Janeiro\n")

    data = read_instance('example_gps.txt', distance_type='haversine')

    print(f"Número de sensores: {len(data['V'])}")
    print(f"Capacidade dos drones (C): {data['C']:.4f} km")
    print(f"Número de drones (K): {data['K']}")
    print(f"\nExemplos de distâncias (em km):")
    for arc in data['A'][:5]:
        print(f"  d{arc} = {data['d'][arc]:.6f} km")
    print(f"\nVizinhança de cobertura:")
    for i, neighbors in enumerate(data['Viz']):
        print(f"  Sensor {i}: {neighbors}")
    print()


def test_manhattan():
    """Testa com distância de Manhattan."""
    print("=" * 60)
    print("DISTÂNCIA MANHATTAN (Grade)")
    print("=" * 60)

    data = read_instance('example_instance.txt', distance_type='manhattan')

    print(f"Número de sensores: {len(data['V'])}")
    print(f"Capacidade dos drones (C): {data['C']:.4f}")
    print(f"Número de drones (K): {data['K']}")
    print(f"\nExemplos de distâncias:")
    for arc in [(0, 1), (0, 4), (1, 5), (5, 9)]:
        print(f"  d{arc} = {data['d'][arc]:.4f}")
    print()


def compare_distances():
    """Compara as três métricas lado a lado."""
    print("=" * 60)
    print("COMPARAÇÃO ENTRE MÉTRICAS")
    print("=" * 60)

    euclidean_data = read_instance('example_instance.txt', distance_type='euclidean')
    manhattan_data = read_instance('example_instance.txt', distance_type='manhattan')

    print("\nComparação de distâncias para alguns arcos:")
    print(f"{'Arco':<10} {'Euclidiana':<15} {'Manhattan':<15}")
    print("-" * 40)

    test_arcs = [(0, 1), (0, 5), (1, 6), (2, 9)]
    for arc in test_arcs:
        euc = euclidean_data['d'][arc]
        man = manhattan_data['d'][arc]
        print(f"{str(arc):<10} {euc:<15.4f} {man:<15.4f}")

    print(f"\nCapacidade dos drones (C):")
    print(f"  Euclidiana: {euclidean_data['C']:.4f}")
    print(f"  Manhattan:  {manhattan_data['C']:.4f}")
    print()


if __name__ == '__main__':
    test_euclidean()
    test_manhattan()

    # Só testa Haversine se o arquivo GPS existir
    try:
        test_haversine()
    except FileNotFoundError:
        print("Arquivo example_gps.txt não encontrado, pulando teste Haversine\n")

    compare_distances()
