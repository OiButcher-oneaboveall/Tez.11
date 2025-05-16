
import random
import numpy as np

cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
num_cities = len(cities)

distance_matrix = np.random.uniform(5, 30, size=(num_cities, num_cities))
risk_matrix = np.random.rand(num_cities, num_cities)
speed_matrix = np.random.uniform(30, 70, size=(12, num_cities, num_cities))

service_times = [0] + [random.randint(5, 15) for _ in range(num_cities - 1)]
time_windows = [(360, 1080)] * num_cities

def evaluate_route(route):
    total_distance = 0
    total_time = 0
    total_risk = 0
    current_time = 360
    log = []

    for i in range(len(route) - 1):
        from_idx = cities.index(route[i])
        to_idx = cities.index(route[i + 1])
        hour = int(current_time // 60) - 6
        hour = max(0, min(hour, 11))
        speed = speed_matrix[hour][from_idx][to_idx]
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
    print("GA Başlıyor...")
    population = [random.sample(cities[1:], len(cities) - 1) for _ in range(pop_size)]
    population = [["Rafineri"] + p + ["Rafineri"] for p in population]
    best_route = None
    best_fitness = float("inf")

    for gen in range(generations):
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

        if gen % 10 == 0:
            print(f"Gen {gen}: En iyi fitness = {best_fitness:.2f}")

        new_pop = [best_route]
        while len(new_pop) < pop_size:
            p1, p2 = random.choices(scores[:pop_size//2], k=2)
            cut = random.randint(1, len(cities) - 2)
            child = ["Rafineri"] + p1[1][1:cut] + [c for c in p2[1][1:] if c not in p1[1][1:cut]] + ["Rafineri"]
            if len(child) == len(cities) + 1:
                new_pop.append(child)
        population = new_pop

    print("GA Bitti.")
    return best_route, best_dist, best_time, best_risk, best_log, best_avg_speed
