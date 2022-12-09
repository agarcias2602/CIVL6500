import osmnx as ox
import networkx as nx
import geopandas as gpd
from gyroscope import GYROSCOPE

def getEdgeWeights(df, G):
  #dictionary of edge tuples to weight
  weights = {}
  sumGraphWeights = 0 #used to get the sum of all loc indexes
  sumGraphNodes = 0
  #loop through each node
  for node in df['G_NODE']:
    #if G.nodes[node]['gyroscope_list'] !=[]:
    totalLen = 0     
    totalWeight = 0
    sumGraphNodes += 1
    for edge in nx.edges(G, node):
      totalLen += G.get_edge_data(edge[0], edge[1])[0]['length']
    for x in G.nodes[node]['gyroscope_list']:
      totalWeight += x.awv
      sumGraphWeights += x.awv
    baseWeight = totalWeight/len(G.nodes[node]['gyroscope_list'])
    for edge in nx.edges(G, node):
      weights[(edge[0], edge[1], 0)] = (totalLen/G.get_edge_data(edge[0], edge[1])[0]['length']) * baseWeight
  avgWeight = sumGraphWeights/sumGraphNodes if sumGraphNodes else 0
  for node in G.nodes:
    if G.nodes[node]['gyroscope_list'] == []:
      totalLen = 0
      totalWeight = 0
      for edge in nx.edges(G, node):
        totalLen += G.get_edge_data(edge[0], edge[1])[0]['length']
      for edge in nx.edges(G, node):
        weights[(edge[0], edge[1], 0)] = (totalLen/G.get_edge_data(edge[0], edge[1])[0]['length']) *avgWeight
  return weights

def york_data_preprocessing(G, filter_df):
  york_df = gpd.read_file("F:/York/01. Master Transportation/03. Fall 2022/CIVL 6500 - Freight Transportation/Term Project/Data/loc_yorku.geojson")
  york_df["LOC_INDEX"] = york_df["awv"]
  index_df = york_df[["ID", "LOC_INDEX"]].groupby(by="ID").sum()
  cols_to_keep = ["Latitude", "Longitude", "ID"]
  york_df = york_df[cols_to_keep]
  york_df = york_df.drop_duplicates()
  york_df.reset_index(drop=True, inplace=True)
  york_df["G_NODE"]= ox.nearest_nodes(G, york_df["Longitude"], york_df["Latitude"], return_dist=False)
  york_df.drop(["Latitude", "Longitude"], axis=1, inplace=True)
  york_df = york_df.merge(index_df, on="ID")
  york_df = york_df.infer_objects()
  york_df["GYROSCOPE"] = york_df.apply(lambda x: GYROSCOPE(x["ID"], x["LOC_INDEX"]), axis=1)
  if filter_df == "0":
    return york_df.loc[york_df.ID.isin(["0"])]
  else:
    return york_df


def create_york_graph(filter_df = "None", weighted=True):
  G = ox.graph_from_place('York University, Toronto, Canada', network_type='walk')
  york_df = york_data_preprocessing(G,filter_df)
  given_df = york_df.groupby('G_NODE')['GYROSCOPE'].apply(list).reset_index(name='GYROSCOPES')
  attr = given_df.set_index('G_NODE')['GYROSCOPES'].to_dict()
  nx.set_node_attributes(G, [], "gyroscope_list")
  nx.set_node_attributes(G, attr, "gyroscope_list")
  if weighted:
    weights = getEdgeWeights(given_df, G)
    nx.set_edge_attributes(G, 0, 'w')
    nx.set_edge_attributes(G, weights, 'w')
  G = ox.add_edge_speeds(G)
  G = ox.add_edge_travel_times(G)
  return G
