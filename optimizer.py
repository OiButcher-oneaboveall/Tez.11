
import random

def run_ga(pop_size, generations, max_risk, hedef):
    cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
    route = random.sample(cities[1:], len(cities) - 1)
    route.insert(0, "Rafineri")
    dist = round(random.uniform(100, 300), 2)
    time = round(random.uniform(60, 180), 2)
    risk = round(random.uniform(5, max_risk), 2)
    log = [{"from": route[i], "to": route[i+1], "arrival": f"08:{str(i*10).zfill(2)}", "departure": f"08:{str((i+1)*10).zfill(2)}"} for i in range(len(route)-1)]
    return route, dist, time, risk, log
