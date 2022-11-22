import networkx as nx
import pandas as pd
import osmnx as ox
import itertools

def pagerank_top_n(G, n):
  pr = nx.pagerank_scipy(G, weight='w')
  pr = pd.DataFrame.from_dict(pr, orient='index').sort_values(by=0, ascending=False).rename(columns={0:"PageRank Score"})
  return pr.iloc[:n]


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


def plot_route(G, route_list, color):
  return ox.plot_graph_route(G, bgcolor='white', node_size=1.0, node_color='gray', edge_color='gray',route=route_list, route_color = color, dpi=300, figsize=(15,15))


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


def girvan_newman_upto_k(G, k):
  comp = nx.algorithms.community.centrality.girvan_newman(G, most_central_edge)
  limited = itertools.takewhile(lambda c: len(c) <= k, comp)
  k_community = None
  for communities in limited:
    k_community = communities
  community_tuple = tuple(c for c in k_community)
  return community_tuple

def plot_top_4_communities(G, communities):
  cc1 = communities[0]
  cc2 = communities[1]
  cc3 = communities[2]
  cc4 = communities[3]
  ec = []
  for edge in G.edges():
    if (edge[0] in cc1) or (edge[1] in cc1):
      ec.append('red')
    elif (edge[0] in cc2) or (edge[1] in cc2):
      ec.append('blue')
    elif (edge[0] in cc3) or (edge[1] in cc3):
      ec.append('green')
    elif (edge[0] in cc4) or (edge[1] in cc4):
      ec.append('orange')
    else:
      ec.append("gray")
  return ox.plot_graph(G, bgcolor='white', node_size=1.0, node_color='gray', edge_color=ec, edge_linewidth=1.0, edge_alpha=1, dpi=300, figsize=(15,15))


def average_LOC_index(G, community):
  total_idx = 0
  for node in community:
    for gyroscope in G.nodes()[node]['gyroscope_list']:
      total_idx = total_idx + gyroscope.aw_tot
  return total_idx/len(community)


def average_gyroscope_weight(G, community):
  total_weight = 0
  edge_count = 0
  for edge in list(G.edges.data()):
    if (edge[0] in community) or (edge[1] in community):
      total_weight = total_weight + edge[2]['w']
      edge_count = edge_count + 1
  return total_weight/edge_count