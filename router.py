import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

print("1. Rebuilding road network graph and training prediction model...")
ox.settings.timeout = 180
center_point = (25.5788, 91.8933)
graph = ox.graph_from_point(center_point, dist=5000, network_type="drive")

# Quick feature simulation and model training to get probabilities
nodes, edges = ox.graph_to_gdfs(graph)
np.random.seed(42)
edges['rainfall_mm'] = np.random.exponential(scale=50, size=len(edges))
edges['slope_degrees'] = np.random.uniform(low=2.0, high=40.0, size=len(edges))
edges['historical_incidents'] = np.random.poisson(lam=1.0, size=len(edges))

risk_score = (
    (edges['rainfall_mm'] > 100).astype(int) * 2 +
    (edges['slope_degrees'] > 25).astype(int) * 2 +
    (edges['historical_incidents'] >= 2).astype(int) * 1.5
)
y = (risk_score > 3.0).astype(int)
X = edges[['rainfall_mm', 'slope_degrees', 'historical_incidents']]

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

# Predict disruption probabilities for all road edges
edges['disruption_prob'] = model.predict_proba(X)[:, 1]

# 2. Assign dynamic risk-adjusted weights to graph edges
for u, v, k, data in graph.edges(keys=True, data=True):
    # Fetch base length (default to 1 if missing)
    base_length = data.get('length', 1.0)
    
    # Get disruption probability from our dataframe edges
    try:
        prob = edges.loc[(u, v, k), 'disruption_prob']
    except KeyError:
        prob = 0.05  # Default low risk if edge not found
        
    # Penalty multiplier: if probability is high, weight increases exponentially
    data['risk_weight'] = base_length * (1.0 + (prob * 20.0))

print("2. Graph weighted successfully with disaster risk penalties.")

# 3. Compute Shortest Path from a start node to an end node
# Pick first two nodes in the graph as a sample source and target
node_list = list(graph.nodes())
source_node = node_list[0]
target_node = node_list[len(node_list) // 2]

try:
    # Compute standard shortest path (by distance) vs Risk-Aware path
    standard_path = nx.shortest_path(graph, source=source_node, target=target_node, weight='length')
    safe_path = nx.shortest_path(graph, source=source_node, target=target_node, weight='risk_weight')
    
    print("\n--- Routing Results ---")
    print(f"Source Node: {source_node}")
    print(f"Target Node: {target_node}")
    print(f"Standard Path Node Count: {len(standard_path)}")
    print(f"Risk-Aware Safe Path Node Count: {len(safe_path)}")
    print("Routing optimization complete! Safe alternate route successfully computed.")

except nx.NetworkXNoPath:
    print("No path found between selected nodes in this sub-graph.")