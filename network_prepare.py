# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 16:55:21 2018

@author: Jimny
"""

# Import required packages
import sys
import numpy as np
import pandas as pd


# Define main function here
def main(argv):
    
    # Open cleaned file and read to a dataframe
    with open ('cleaned_data.csv', 'r') as raw:
        df = pd.read_csv(raw , sep=',', encoding='utf-8')
    
    # Initialize the attribute list 
    attr_list = ['origin', 'destination', 'arr_delay_sig','arr_delay_min',
                 'dep_delay_sig', 'dep_delay_min', 'diff_flt']
    
    # Extract the attributes we need for the network
    df_net = df.loc[:, attr_list]
    
    # Defines the origin and destination as nodes
    df_pair = df_net.groupby(['origin','destination']).size().reset_index().rename(columns={0:'count'})
    
    # Generate origin and destination list
    origin_list = df_pair['origin'].tolist()
    destination_list = df_pair['destination'].tolist()
    
    # This for loop iterate through the origin list
    for i in range(len(origin_list)):
        df_ori = df_net[df_net['origin'] == origin_list[i]]
        
        # Generate nodes' attributes correspondingly
        dep_delay_sig = df_ori['dep_delay_sig'].tolist()
        dep_delay_min = df_ori['dep_delay_min'].tolist()
        
        # Define delay time of undelayed flights as 0
        for j in range(len(dep_delay_min)):
            if dep_delay_min[j] < 0:
                dep_delay_min[j] = 0
        
        # Calculate delay rate and average delay time for nodes
        delay_rate = sum(dep_delay_sig) / len(dep_delay_sig)
        avg_delay = sum(dep_delay_min) / len(dep_delay_min)
        
        # Write these two attributes to dataframe of nodes info
        df_pair.loc[i, 'delay_rate'] = delay_rate
        df_pair.loc[i, 'avg_delay'] = avg_delay
        
        # For edge
        df_ori_des = df_ori[df_ori['destination'] == destination_list[i]]
        
        # Generate average time difference with flight time for edges
        diff_flt = df_ori_des['diff_flt'].tolist()
        avg_diff_flt = sum(diff_flt) / len(diff_flt)
        
        df_pair.loc[i, 'avg_diff_flt'] = avg_diff_flt
        
        # Node Size: determines by flight counts
        dep_count = len(df_ori)
        
        df_des = df_net[df_net['destination'] == origin_list[i]]
        
        arr_count = len(df_des)
        
        df_pair.loc[i, 'dep_arr_count'] = dep_count + arr_count
        
    # Clean up NA values and delete nodes with extra low flight counts
    df_pair = df_pair[df_pair['avg_diff_flt'].isna() == False]
    df_pair = df_pair[df_pair['count'] >= 5].reset_index(drop = True)
    
    # Write the concantenated dataframe
    with open('for_network.csv','w') as prepared:
        df_pair.to_csv(prepared, sep=',',index = True)
    
# Let the main function run
if __name__=="__main__":
    # Execute only if run as script
    main(sys.argv)