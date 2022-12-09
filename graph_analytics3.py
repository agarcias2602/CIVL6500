import networkx as nx
import pandas as pd
import osmnx as ox
import itertools

def print_route_time_distance(G, route):
  route_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))/1000
  route_time = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'travel_time')))/60
  route_weight = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'w')))
  print('Route is', format(route_length, '.2f'), 'kms and takes', format(route_time, '.2f'), 'minutes. This route has a LOC of: ', route_weight)


def get_route_by_comfort(G, origin, destination):
  return nx.shortest_path(G, source=origin, target = destination, weight = 'w', method='dijkstra')


def get_route_by_length(G, origin, destination):
  return nx.shortest_path(G, source=origin, target = destination, weight = 'length', method='dijkstra')


def get_route_by_time(G, origin, destination):
  return nx.shortest_path(G, source=origin, target = destination, weight = 'travel_time', method='dijkstra')


def plot_all_routes(G, origin, destination):
  routes = [get_route_by_length(G, origin, destination), get_route_by_time(G, origin, destination), get_route_by_comfort(G, origin, destination)]
  rc = ['r', 'b', 'g']
  return ox.plot_graph_routes(G, bgcolor='white', node_size=1.0, node_color='gray', edge_color='gray',routes=routes, route_colors = rc, dpi=300, figsize=(15,15))


def plot_graph(G, filter_node_list = None):
  if filter_node_list:
    ec = ['r' if node in filter_node_list else (0,0,0,0) for node in G.nodes]
    return ox.plot_graph(G, bgcolor='white', node_size=20, node_color=ec, edge_linewidth=0.4, edge_alpha=1, dpi=300, figsize=(15,15))
  else:
    return ox.plot_graph(G, bgcolor='white', node_size=0.3, node_color="red", edge_linewidth=0.4, edge_alpha=1, dpi=300, figsize=(15,15))


def most_central_edge(net):
    centrality = nx.edge_betweenness_centrality(net, k = 25)
    return max(centrality, key=centrality.get)