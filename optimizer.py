
import random
import numpy as np

cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
distance_matrix = np.array([
    [0, 66.8, 105, 123, 130, 106, 109, 113],
    [66.8, 0, 40.3, 57.8, 55.4, 41.5, 47.6, 52.1],
    [105, 40.3, 0, 18.5, 23.9, 6, 11.8, 24.8],
    [123, 57.8, 18.5, 0, 13.9, 17.8, 18.3, 19.1],
    [130, 55.4, 23.9, 13.9, 0, 18.5, 30.4, 23.2],
    [106, 41.5, 6, 17.8, 18.5, 0, 8, 21.7],
    [109, 47.6, 11.8, 18.3, 30.4, 8, 0, 14.4],
    [113, 52.1, 24.8, 19.1, 23.2, 21.7, 14.4, 0]
])
risk_matrix = np.array([
    [0, 0.2, 0.4, 0.8, 0.9, 0.5, 0.5, 1.0],
    [0, 0, 0.1, 0.5, 0.4, 0.1, 0.1, 0.5],
    [0, 0.1, 0, 0.2, 0.2, 0.1, 0.1, 0.3],
    [0, 0.5, 0.2, 0, 0.1, 0.2, 0.2, 0.4],
    [0, 0.4, 0.1, 0.1, 0, 0.3, 0.3, 0.5],
    [0, 0.1, 0.1, 0.2, 0.3, 0, 0.1, 0.2],
    [0, 0.1, 0.1, 0.2, 0.3, 0.1, 0, 0.2],
    [0, 0.5, 0.2, 0.4, 0.5, 0.2, 0.2, 0]
])
speed_hourly_matrix = np.array([
    [90, 80, 70, 90, 80, 70, 90, 90, 80, 90, 70, 80],
    [80, 70, 80, 80, 70, 90, 80, 70, 70, 70, 90, 90],
    [70, 60, 90, 70, 90, 90, 70, 90, 90, 90, 90, 70],
    [60, 90, 60, 60, 60, 80, 60, 80, 90, 80, 80, 60],
    [90, 90, 90, 90, 90, 80, 90, 90, 90, 90, 90, 90],
    [80, 90, 80, 90, 70, 70, 80, 90, 70, 80, 80, 70],
    [90, 80, 90, 90, 80, 90, 90, 90, 90, 90, 90, 90],
    [70, 70, 90, 80, 90, 80, 70, 90, 90, 90, 90, 90]
])
service_times = {1: 30, 5: 33, 3: 32, 4: 31, 2: 40, 6: 29, 7: 20}
MAX_TOTAL_RISK = 10
START_HOUR = 6
time_windows = {
    1: (6, 18), 2: (6, 18), 3: (12, 18), 4: (6, 18),
    5: (6, 12), 6: (12, 18), 7: (6, 12)
}

def get_speed(city_idx, hour_idx):
    window_idx = hour_idx - START_HOUR
    return speed_hourly_matrix[city_idx, window_idx] if 0 <= window_idx < 12 else 90

def compute_piecewise_travel_time(from_city, to_city, start_hour, start_minute, distance):
    remaining_distance = distance
    hour, minute = int(start_hour), int(start_minute)
    total_minutes = 0
    while remaining_distance > 0:
        current_speed = min(get_speed(from_city, hour), get_speed(to_city, hour))
        remaining_time_in_hour = 60 - minute
        max_distance_this_hour = current_speed * (remaining_time_in_hour / 60)
        if remaining_distance <= max_distance_this_hour:
            travel_time = (remaining_distance / current_speed) * 60
            total_minutes += travel_time
            minute += travel_time
            hour += int(minute) // 60
            minute = int(minute) % 60
            break
        else:
            total_minutes += remaining_time_in_hour
            remaining_distance -= max_distance_this_hour
            hour += 1
            minute = 0
    return total_minutes, hour, minute

def route_metrics_with_log(route):
    total_distance, total_time, total_risk = 0, 0, 0
    hour, minute = START_HOUR, 0
    log = []
    for i in range(len(route) - 1):
        from_city, to_city = route[i], route[i + 1]
        departure = f"{int(hour):02d}:{int(minute):02d}"
        distance = distance_matrix[from_city][to_city]
        wait_time = 0
        next_speed = min(get_speed(from_city, hour + 1), get_speed(to_city, hour + 1))
        current_speed = min(get_speed(from_city, hour), get_speed(to_city, hour))
        travel_minutes_now = (distance / current_speed) * 60
        travel_minutes_waited = (distance / next_speed) * 60
        if travel_minutes_waited + 60 < travel_minutes_now:
            wait_time = 60 - minute
        minute += wait_time
        hour += minute // 60
        minute %= 60
        if to_city != 0:
            earliest, latest = time_windows[to_city]
            arrival_total_minutes = hour * 60 + minute
            if arrival_total_minutes < earliest * 60:
                additional_wait = (earliest * 60) - arrival_total_minutes
                wait_time += additional_wait
                minute += additional_wait
                hour += minute // 60
                minute %= 60
            elif arrival_total_minutes > latest * 60:
                return float('inf'), float('inf'), float('inf'), []
        travel_minutes, hour, minute = compute_piecewise_travel_time(from_city, to_city, hour, minute, distance)
        total_distance += distance
        total_time += travel_minutes + wait_time
        total_risk += risk_matrix[from_city][to_city]
        arrival = f"{int(hour):02d}:{int(minute):02d}"
        service = service_times.get(to_city, 0)
        total_time += service
        minute += service
        hour += minute // 60
        minute %= 60
        departure_after_service = f"{int(hour):02d}:{int(minute):02d}"
        log.append({
            "from": cities[from_city],
            "to": cities[to_city],
            "departure": departure,
            "arrival": arrival,
            "service": service,
            "wait": wait_time,
            "departure_after_service": departure_after_service
        })
        if hour >= 18:
            return float('inf'), float('inf'), float('inf'), []
    return total_distance, total_time, total_risk, log

def initialize_population(size, num_cities):
    return [[0] + random.sample(range(1, num_cities), num_cities - 1) + [0] for _ in range(size)]

def fitness(route):
    d, t, r, _ = route_metrics_with_log(route)
    return float('inf') if r > MAX_TOTAL_RISK or d == float('inf') else t

def selection(pop):
    return min(random.sample(pop, 5), key=fitness)

def crossover(p1, p2):
    start, end = sorted(random.sample(range(1, len(p1) - 1), 2))
    child = [None] * len(p1)
    child[start:end] = p1[start:end]
    pointer = 1
    for gene in p2[1:-1]:
        if gene not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = gene
    child[0] = child[-1] = 0
    return child

def mutate(route, rate=0.02):
    for i in range(1, len(route) - 2):
        if random.random() < rate:
            j = random.randint(1, len(route) - 2)
            route[i], route[j] = route[j], route[i]

def run_ga(pop_size=300, generations=1000, max_risk=10, hedef="Minimum Süre"):
    global MAX_TOTAL_RISK
    MAX_TOTAL_RISK = max_risk
    population = initialize_population(pop_size, len(cities))
    for _ in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = selection(population)
            p2 = selection(population)
            c = crossover(p1, p2)
            mutate(c)
            new_pop.append(c)
        population = new_pop
    valid_population = [route for route in population if fitness(route) != float('inf')]
    if not valid_population:
        return [], float('inf'), float('inf'), float('inf'), []
    best_route = min(valid_population, key=fitness)
    d, t, r, log = route_metrics_with_log(best_route)
    return [cities[i] for i in best_route], round(d, 2), round(t, 2), round(r, 2), log
