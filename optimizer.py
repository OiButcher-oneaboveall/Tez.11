
import random
import numpy as np

cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
num_cities = len(cities)

# Önceden tanımlı örnek sabit matrisler (gerçek veriyle değiştirilmediği için hızlıdır)
distance_matrix = np.array([
    [0, 66.8, 105, 123, 130, 106, 109, 113],
    [66.8, 0, 40.3, 57.8, 55.4, 41.5, 47.6, 52.1],
    [105, 40.3, 0, 18.5, 23.9, 6, 11.8, 24.8],
    [123, 57.8, 18.5, 0, 8.1, 16.4, 21.9, 19.2],
    [130, 55.4, 23.9, 8.1, 0, 25.3, 28.2, 17.4],
    [106, 41.5, 6, 16.4, 25.3, 0, 9.2, 21.3],
    [109, 47.6, 11.8, 21.9, 28.2, 9.2, 0, 15.2],
    [113, 52.1, 24.8, 19.2, 17.4, 21.3, 15.2, 0]
])

risk_matrix = np.random.rand(num_cities, num_cities)
speed_matrix = np.full((12, num_cities, num_cities), 60)  # Ortalama 60 km/h sabit hız

service_times = [0] + [10] * (num_cities - 1)  # Her noktada 10 dk servis
time_windows = [(360, 1080)] * num_cities  # 06:00 - 18:00

def evaluate_route(route):
    total_distance = 0
    total_time = 0
    total_risk = 0
    current_time = 360
    log = []

    for i in range(len(route) - 1):
        from_idx = cities.index(route[i])
        to_idx = cities.index(route[i + 1])
        speed = speed_matrix[int(current_time // 60 - 6)][from_idx][to_idx]
        dist = distance_matrix[from_idx][to_idx]
        travel_time = dist / speed * 60
        arrival_time = current_time + travel_time
        earliest, latest = time_windows[to_idx]
        wait = max(0, earliest - arrival_time)
        service = service_times[to_idx]
        depart_time = arrival_time + wait + service

        log.append({
            "from": route[i],
            "to": route[i + 1],
            "departure": f"{int(current_time//60):02d}:{int(current_time%60):02d}",
            "arrival": f"{int(arrival_time//60):02d}:{int(arrival_time%60):02d}",
            "wait": int(wait),
            "service": service
        })

        total_distance += dist
        total_time += travel_time + wait + service
        total_risk += risk_matrix[from_idx][to_idx]
        current_time = depart_time

    avg_speed = total_distance / (total_time / 60)
    return total_distance, total_time, total_risk, log, avg_speed

def run_ga(pop_size, generations, max_risk, hedef):
    population = [random.sample(cities[1:], len(cities) - 1) for _ in range(pop_size)]
    population = [["Rafineri"] + p + ["Rafineri"] for p in population]
    best_route = None
    best_fitness = float("inf")

    for _ in range(generations):
        scores = []
        for route in population:
            dist, time, risk, log, avg_speed = evaluate_route(route)
            if risk > max_risk:
                fitness = float("inf")
            else:
                if hedef == "Minimum Süre":
                    fitness = time
                elif hedef == "Minimum Mesafe":
                    fitness = dist
                elif hedef == "Minimum Risk":
                    fitness = risk
                elif hedef == "Maksimum Ortalama Hız":
                    fitness = -avg_speed
                else:
                    fitness = time
            scores.append((fitness, route, dist, time, risk, log, avg_speed))

        scores.sort()
        best_fitness, best_route, best_dist, best_time, best_risk, best_log, best_avg_speed = scores[0][:7]
        new_pop = [best_route]
        while len(new_pop) < pop_size:
            p1, p2 = random.choices(scores[:pop_size//2], k=2)
            cut = random.randint(1, len(cities) - 2)
            child = ["Rafineri"] + p1[1][1:cut] + [c for c in p2[1][1:] if c not in p1[1][1:cut]] + ["Rafineri"]
            if len(child) == len(cities) + 1:
                new_pop.append(child)
        population = new_pop

    return best_route, best_dist, best_time, best_risk, best_log, best_avg_speed
