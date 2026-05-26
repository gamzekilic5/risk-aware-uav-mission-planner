import math
import pandas as pd
import matplotlib.pyplot as plt


def euclidean_distance(a, b):
    return math.sqrt((a["x_km"] - b["x_km"]) ** 2 + (a["y_km"] - b["y_km"]) ** 2)


def point_to_segment_distance(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay

    if dx == 0 and dy == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)

    t = ((px - ax) * dx + (py - ay) * dy) / (dx ** 2 + dy ** 2)
    t = max(0, min(1, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)


def leg_risk(start, end, risk_zones):
    score = 0

    for _, zone in risk_zones.iterrows():
        distance_to_leg = point_to_segment_distance(
            zone["center_x_km"], zone["center_y_km"],
            start["x_km"], start["y_km"],
            end["x_km"], end["y_km"]
        )

        if distance_to_leg <= zone["radius_km"]:
            score += zone["risk_score"]

    return score


def route_distance(route, points):
    total = 0
    for i in range(len(route) - 1):
        total += euclidean_distance(points[route[i]], points[route[i + 1]])
    return total


def route_risk(route, points, risk_zones):
    total = 0
    for i in range(len(route) - 1):
        total += leg_risk(points[route[i]], points[route[i + 1]], risk_zones)
    return total


def route_energy(route, points, params):
    speed = params["average_speed_kmh"]
    cruise_power = params["cruise_power_w"]
    hover_power = params["hover_power_w"]

    cruise_energy = 0
    hover_energy = 0

    for i in range(len(route) - 1):
        start = points[route[i]]
        end_name = route[i + 1]
        end = points[end_name]

        distance = euclidean_distance(start, end)
        flight_time_min = (distance / speed) * 60
        cruise_energy += cruise_power * (flight_time_min / 60)

        if end_name != "Base":
            hover_energy += hover_power * (end["task_time_min"] / 60)

    return cruise_energy + hover_energy


def build_risk_aware_route(points, risk_zones, params, start="Base"):
    unvisited = set(points.keys())
    unvisited.remove(start)

    route = [start]
    current = start

    while unvisited:
        best_candidate = None
        best_score = float("inf")

        for candidate in unvisited:
            distance = euclidean_distance(points[current], points[candidate])
            risk = leg_risk(points[current], points[candidate], risk_zones)
            priority = points[candidate]["priority"]

            # Lower score is better.
            # Priority slightly reduces the score so important points are not pushed too far back.
            score = distance + (params["risk_penalty_weight"] * risk) - (0.15 * priority)

            if score < best_score:
                best_score = score
                best_candidate = candidate

        route.append(best_candidate)
        unvisited.remove(best_candidate)
        current = best_candidate

    route.append(start)
    return route


def plot_mission(route, points, risk_zones, filename="uav_mission_route.png"):
    xs = [points[p]["x_km"] for p in route]
    ys = [points[p]["y_km"] for p in route]

    plt.figure()
    plt.plot(xs, ys, marker="o")

    for name, p in points.items():
        plt.text(p["x_km"], p["y_km"], name)

    for _, zone in risk_zones.iterrows():
        circle = plt.Circle(
            (zone["center_x_km"], zone["center_y_km"]),
            zone["radius_km"],
            fill=False
        )
        plt.gca().add_patch(circle)
        plt.text(zone["center_x_km"], zone["center_y_km"], zone["zone"], fontsize=8)

    plt.title("Risk-Aware UAV Mission Route")
    plt.xlabel("X Coordinate (km)")
    plt.ylabel("Y Coordinate (km)")
    plt.axis("equal")
    plt.grid(True)
    plt.savefig(filename, dpi=200, bbox_inches="tight")


def main():
    point_df = pd.read_csv("mission_points.csv")
    risk_zones = pd.read_csv("risk_zones.csv")
    param_df = pd.read_csv("uav_parameters.csv")

    points = {
        row["point"]: {
            "x_km": row["x_km"],
            "y_km": row["y_km"],
            "priority": row["priority"],
            "task_time_min": row["task_time_min"]
        }
        for _, row in point_df.iterrows()
    }

    params = dict(zip(param_df["parameter"], param_df["value"]))

    route = build_risk_aware_route(points, risk_zones, params)

    distance = route_distance(route, points)
    risk = route_risk(route, points, risk_zones)
    energy = route_energy(route, points, params)

    battery_capacity = params["battery_capacity_wh"]
    reserve = params["safety_reserve_percent"]
    usable_battery = battery_capacity * (1 - reserve / 100)

    mission_feasible = energy <= usable_battery

    summary = pd.DataFrame([{
        "route": " -> ".join(route),
        "total_distance_km": round(distance, 2),
        "total_risk_score": round(risk, 2),
        "estimated_energy_wh": round(energy, 2),
        "usable_battery_wh": round(usable_battery, 2),
        "mission_feasible": mission_feasible
    }])

    summary.to_csv("mission_summary.csv", index=False)

    print("Risk-Aware UAV Mission Planner")
    print("------------------------------")
    print("Route:", " -> ".join(route))
    print("Total distance:", round(distance, 2), "km")
    print("Total risk score:", round(risk, 2))
    print("Estimated energy:", round(energy, 2), "Wh")
    print("Usable battery:", round(usable_battery, 2), "Wh")
    print("Mission feasible:", "Yes" if mission_feasible else "No")

    plot_mission(route, points, risk_zones)


if __name__ == "__main__":
    main()
