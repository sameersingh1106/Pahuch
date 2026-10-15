import osmnx as ox


ox.settings.timeout = 180


center_point = (25.5788, 91.8933)

graph = ox.graph_from_point(center_point, dist=5000, network_type="drive")


nodes, edges = ox.graph_to_gdfs(graph)
print(f"Total road segments (edges): {len(edges)}")


edges.to_csv("ner_road_segments.csv")
print("Saved road segments to ner_road_segments.csv successfully!")