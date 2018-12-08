# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 17:50:20 2018

@author: Xi
"""

# Import required packages
import sys
import igraph as ig
import numpy as np

import plotly
plotly.tools.set_credentials_file(username = 'oscar12xi', 
                                  api_key = 'k3jM66OjS8b35bFZhjGR')

import plotly.plotly as py
import plotly.graph_objs as go


import pandas as pd

# Define main function
def main(sys):
    # Open the csv file that containes airport names and ICAO codes
    with open ('airport-codes.csv', 'r', encoding='utf-8') as data:
        df_airport = pd.read_csv(data , sep=',')
    
    # Only use two columns ('ident' 'name')
    df_airport = df_airport.loc[:, ['ident', 'name']]
    
    # Construct 'airport ICAO code: name' dictionary
    airport_dict = dict()
    for index, row in df_airport.iterrows():
        airport_dict[row['ident']] = row['name']
    
    # Read in the gml format network that has been constructed by networkx
    with open('airport_networkx.gml','r') as input_3:
        g3 = ig.Graph.Read_GML(input_3)
    
    # Print out the density and the number of nodes and edges
    print('\nDensity = ', g3.density())
    print('Nodes/Vertices: ', len(ig.VertexSeq(g3)))
    print('Edges: ', len(ig.EdgeSeq(g3)))
    
    # Set the weight of edges
    #g3.es['weight'] = g3.es['value']
    
    # Setup the layout (position)
    layt = g3.layout('kk', dim=3) 
    
    # Count total number of vertices
    N = len(ig.VertexSeq(g3))
    
    # Setup 3d nodes position
    Xn=[layt[k][0] for k in range(N)]# x-coordinates of nodes
    Yn=[layt[k][1] for k in range(N)]# y-coordinates
    Zn=[layt[k][2] for k in range(N)]# z-coordinates
    
    # Initialize list to collect edges position
    Xe=[]
    Ye=[]
    Ze=[]
    
    # Initialize edge width and color lists
    edge_width = []
    edge_color = []
    
    # Iterate through all edges to set positions, widths, and colors
    for edge in g3.es:
        start = edge.source
        end = edge.target
        
        Xe+=[layt[ start ][0],layt[ end ][0], None]# x-coordinates of edge ends
        Ye+=[layt[ start ][1],layt[ end ][1], None]  
        Ze+=[layt[ start ][2],layt[ end ][2], None]  
        
        edge_width.append(edge['weight'])
        edge_color.append(edge['diffflt'])
    
    
    node_label = []
    node_size = []
    node_color = []
    
    # Iterate through all edges to set positions, widths, and colors
    for node in g3.vs:
        color = node['avgdelay']
        
        # Some small airports are not in ICAO: name dictionary
        try:
            airport = airport_dict[node['label']]
        except:
            airport = ''
        
        # Set labels to display interactively
        label = ''.join([node['label'], '<br>',airport,
                         '<br>Average Departure Dalay: ', 
                         str(round(color,3)), ' (min)'])
        
        size = node['fltcount']
        
        # Append label, size, and color to corresponding lists
        node_label.append(label)
        node_size.append(size/20)
        node_color.append(color)
    
    # Set trace of edges
    trace1=go.Scatter3d(x=Xe,
                        y=Ye,
                        z=Ze,
                        mode='lines',
                        line=dict(color=edge_color,
                                  cmin = min(edge_color),
                                  cmax = max(edge_color),
                                  colorscale='RdBu', 
                                  width=1),
                        hoverinfo='none'
                        )
    
    # Set trace of nodes
    trace2=go.Scatter3d(x=Xn,
                        y=Yn,
                        z=Zn,
                        mode='markers',
                        name='actors',
                        marker=dict(symbol='circle',
                                    size=node_size,
                                    color=node_color,
                                    cmin = min(node_color),
                                    cmax = 60,
                                    colorscale='Reds',
                                    line=dict(color='rgb(50,50,50)', width=0.5)
                                    ),
                        text=node_label,
                        hoverinfo='text'
                        )
                        
    # Setup axis dictionary (mute the axes)
    axis=dict(showbackground=False,
              showline=False,
              zeroline=False,
              showgrid=False,
              showticklabels=False,
              title=''
              )

    # Setup the layout
    layout = go.Layout(
            title="Network of Airports Delay Relationship (3D visualization)",
            width=1000,
            height=1000,
            showlegend=False,
            scene=dict(
                    xaxis=dict(axis),
                    yaxis=dict(axis),
                    zaxis=dict(axis),
                    ),
                    margin=dict(
                            t=100
                            ),
                    hovermode='closest',
                    )
    
    # Final combination of data to plot
    data=[trace1, trace2]
    fig=go.Figure(data=data, layout=layout)

    #py.iplot(fig, filename='Airport Network')
    
    # 3D network plotting
    plotly.offline.plot(fig, validate=False, filename='3d_network.html')
    
    
    
    '''
    # Plotting using igraph directly
    # Set up the parameters for visualization
    vs_3 = {}
    vs_3['layout'] = 'kk'
    vs_3["vertex_size"] = 20
    
    # Set edge widths based on weights
    vs_3["edge_width"] = [w/5 for w in g3.es['weight']]
    
    # Using the determine_col function to determine the vertex color
    #vs_3['vertex_color'] = [determine_col(item) for item in g3.degree()]
    
    vs_3["vertex_label_dist"] = 2
    vs_3["vertex_label_size"] = 25
    vs_3["vertex_label_angle"] = 90
    vs_3["vertex_label_color"] = 'darkslategrey'
    vs_3["bbox"] = (1500,1500)
    vs_3["margin"] = 50
    
    # Plot the network
    plot3 = ig.plot(g3, **vs_3)
    plot3.show()
    '''
    
# Let the main function run
if __name__=="__main__":
    # Execute only if run as script
    main(sys.argv)