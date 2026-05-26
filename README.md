# Risk-Aware UAV Mission Planner

This is a small project I started after working on basic drone route optimization and battery checks.  
Here I wanted to make the mission planning problem a little more realistic by adding simple risk zones.

The project is not a complete UAV planning system. It is a learning project where I try to connect route planning, battery feasibility, mission priority, and operational risk in one simple Python example.

## Project idea

A UAV starts from a base, visits several mission points, and returns to the base.  
While planning the route, the code considers:

- total travel distance
- simple risk zones
- task priority
- task time at each point
- estimated battery usage
- safety reserve

The route is selected with a simple risk-aware nearest neighbor logic.  
It is not an advanced optimization algorithm, but it is easy to understand and gives me a good base to improve later.

## Files

- `mission_points.csv` includes the base and mission points.
- `risk_zones.csv` includes simple circular risk zones.
- `uav_parameters.csv` includes battery and speed assumptions.
- `uav_mission_planner.py` runs the mission planning logic.
- `mission_summary.csv` is created after running the code.
- `uav_mission_route.png` is created after running the code.

## Why I made this

I am interested in defense industry, UAV systems, optimization, and mission planning from an Industrial Engineering point of view.  
This project helped me think about how different constraints affect a route. A route can be short, but it may not be the safest or most feasible one.

For now, I kept the project simple and understandable. My aim is to improve it step by step instead of making it too complicated at the beginning.

## How to run

```bash
python uav_mission_planner.py
```

## What I want to improve later

Some ideas I want to try next:

- compare low-risk and shortest-distance routes
- add no-fly zones as strict constraints
- add multiple UAVs
- add time windows for mission points
- include wind or weather effect
- create a basic dashboard
- test different risk penalty values
- use a stronger optimization method
