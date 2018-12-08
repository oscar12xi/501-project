# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 18:44:49 2018

@author: Jimny
"""

# Import required packages
import sys
import igraph as ig
import numpy as np

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

import plotly
plotly.tools.set_credentials_file(username = 'oscar12xi', 
                                  api_key = 'k3jM66OjS8b35bFZhjGR')


# Define main function
def main(sys):

    # Open cleaned file and read to a dataframe
    with open ('for_network.csv', 'r') as inp:
        df = pd.read_csv(inp , sep=',', encoding='utf-8')
    
    # Generate origin and destination list
    origin = df['origin'].tolist()
    destination = df['destination'].tolist()
    
    # Put origin and destination together 
    airport_list = []
    airport_list.extend(origin)
    airport_list.extend(destination)
    
    # Get the unique values in the airport list
    airport_list = list(set(airport_list))
    
    # Open the cleaned data set from part 2 for some more info
    with open ('cleaned_data.csv', 'r') as raw:
        df_raw = pd.read_csv(raw , sep=',', encoding='utf-8')
    
    # Keep only the attributes we need
    attr_list = ['origin', 'destination', 'arr_delay_sig','arr_delay_min',
                 'dep_delay_sig', 'dep_delay_min', 'diff_flt']
    
    df_net = df_raw.loc[:, attr_list]
    
    # Initialize empty dictionaries for node attributes
    delay_rate_dic = {}
    avg_delay_dic = {}
    flt_count_dic = {}
    
    # Using a for loop to iterate through airport list
    for i in range(len(airport_list)):
        #print(airport_list[i])
        df_ori = df_net[df_net['origin'] == airport_list[i]]
        
        # For node: get delay rate and average delay time
        dep_delay_sig = df_ori['dep_delay_sig'].tolist()
        dep_delay_min = df_ori['dep_delay_min'].tolist()
        
        # Define delay time of undelayed flights as 0
        for j in range(len(dep_delay_min)):
            if dep_delay_min[j] < 0:
                dep_delay_min[j] = 0
        
        # For some airports, we do not have enough data to calculate delay rate
        try:
            delay_rate = sum(dep_delay_sig) / len(dep_delay_sig)
        except:
            delay_rate = float('NaN')
        
        # For some airports, we do not have enough data to calculate average delay time
        try:
            avg_delay = sum(dep_delay_min) / len(dep_delay_min)
        except:
            avg_delay = float('NaN')
        
        # Using dictionary to record attributes for the nodes
        delay_rate_dic[airport_list[i]] = delay_rate
        avg_delay_dic[airport_list[i]] = avg_delay
        
        
        # Node Size determination
        dep_count = len(df_ori)
        
        df_des = df_net[df_net['destination'] == airport_list[i]]
        
        arr_count = len(df_des)
        
        flt_count_dic[airport_list[i]] = dep_count + arr_count
    
    

##################### NetworkX ############################3
    
    # Obtain a dataframe
    df_edge_list = df.loc[:, ['origin', 'destination', 'count']]
    
    # Write the dataframe to an edge list
    with open('edge_list.txt','w') as e_list:
        df_edge_list.to_csv(e_list, sep=' ',index = False, header = False)
        

    # Open and read in the prepared weighted edge list
    with open('edge_list.txt','rb') as input_1:
        g1 = nx.read_weighted_edgelist(input_1, create_using = nx.DiGraph)
    
    # Decide if to remove the nodes with low degress to make the graph nicer
    move_sig = input('Remove low degree nodes: y or n?')
    if move_sig == 'y':
        g1_remove = [n for n,d in g1.out_degree() if d <= 3]
        g1.remove_nodes_from(g1_remove)
        
    # Print out basic info and density of the network
    print(nx.info(g1))
    print('\nDensity = ', nx.density(g1))
    
    #g1 = g1.to_undirected()

    # Instore edges into a list
    edge_list = list(g1.edges)
    
    # Using a list to collect nodes' colors
    edge_color_list = []
    for edge in edge_list:
        # Retrieve corresponding info relate to the edge
        df_temp = df.loc[df['origin'] == edge[0], ['destination', 'avg_diff_flt']]
        
        # Set edge color based on time difference with the flight plan
        diff_flt = df_temp.loc[df_temp['destination'] == edge[1], 'avg_diff_flt'].item()
        edge_color_list.append(diff_flt)
        
        g1[edge[0]][edge[1]]['diffflt'] = diff_flt 
    
    # Extract the weight values of the edges
    weight_dic = nx.get_edge_attributes(g1,'weight')
    weight_l = list(weight_dic.values())
    weight_l = [w /10 for w in weight_l]
    
    # Instore all nodes into a list
    node_list = list(g1.nodes)
    
    # Initialize empty list to collect node's sizes and colors
    node_size_list = []
    node_color_list = []
    
    # Using for loop to iterate through all nodes
    for node in node_list:
        node_size_list.append((flt_count_dic[node])*1.6)
        node_color_list.append(avg_delay_dic[node])
        
        g1.node[node]['fltcount'] = flt_count_dic[node]
        g1.node[node]['avgdelay'] = avg_delay_dic[node]
    
    #node_size_list = [(flt_count_dic[x])*1.6 for x in node_list]
    #node_color_list = [avg_delay_dic[y] for y in node_list]
    
    # Set up nodes' labels into a dictionary
    labels = {}
    for node in g1.degree():
        if move_sig == 'y':
            labels[node[0]] = node[0][1:]
        else:
            if node[1] >= 20:
                labels[node[0]] = node[0]
                
                
    # Calculate network positions to plot    
    pos = nx.spring_layout(g1)
    
    # Start plotting
    plt.clf()
    plt.figure(1,figsize=(18, 12))
    
    # Plot network nodes
    c_node = nx.draw_networkx_nodes(g1, pos, node_size = node_size_list, 
                           node_color = node_color_list, 
                           cmap = plt.cm.YlOrRd, 
                           vmin = min(node_color_list), vmax = max(node_color_list),
                           edgecolors = 'salmon')
    # Plot network edges
    c_edge = nx.draw_networkx_edges(g1, pos, width = weight_l, alpha = 0.5,
                           edge_color = edge_color_list,
                           edge_cmap = plt.cm.rainbow, 
                           edge_vmin = min(edge_color_list), edge_vmax = max(edge_color_list))
    
    # Plot network nodes' labels
    nx.draw_networkx_labels(g1, pos, labels, font_size = 18,
                            font_color='dimgray')
    
    # Set up color bars
    cbn = plt.colorbar(c_node, shrink = 0.6)
    
    c_edge = mpl.collections.PatchCollection(c_edge, cmap = plt.cm.rainbow)
    c_edge.set_array(edge_color_list)
    
    cbe = plt.colorbar(c_edge, shrink = 0.6)


    cbn.set_label('Average Delay \n(min)', fontsize=16)
    cbe.set_label('Average Differece with Plan \n(min)', fontsize=16)
    
    cbn.ax.tick_params(labelsize=16)
    cbe.ax.tick_params(labelsize=16)
    
    # Show the plot
    plt.axis('off')
    plt.show()
    
    # Write 
    nx.write_gml(g1, "airport_networkx.gml")

# Let the main function run
if __name__=="__main__":
    # Execute only if run as script
    main(sys.argv)