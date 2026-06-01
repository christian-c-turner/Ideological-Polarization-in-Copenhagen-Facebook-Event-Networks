
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd 
import numpy as np
import ast
import seaborn as sns
from collections import Counter

# Function to update attendees in events dataset and calculate counts based on users dataset
def update_and_count_attendees(events_df, users_df):
    # Convert hashed_id and political columns to dictionaries for fast lookups
    valid_users = set(users_df['hashed_id'].values)
    political_users = set(users_df.loc[users_df['political'] == True, 'hashed_id'].values)

    # Define a function to process each event
    def process_event(attending):
        attendees = set(ast.literal_eval(attending))  # Convert string to set
        filtered_attendees = attendees.intersection(valid_users)  # Keep only valid users
        n_attending = len(filtered_attendees)  # Total attendees
        n_political = len(filtered_attendees.intersection(political_users))  # Political attendees
        # Create set of political attendees
        political_attendees = filtered_attendees.intersection(political_users)
        return str(filtered_attendees), n_attending, n_political, political_attendees

    # Apply the processing function to the 'attending' column
    results = events_df['attending'].apply(process_event)

    # Unpack the results into separate columns
    events_df['attending'] = results.apply(lambda x: x[0])  # Updated attendees
    events_df['n_attending'] = results.apply(lambda x: x[1])  # Number of total attendees
    events_df['n_political_attending'] = results.apply(lambda x: x[2])  # Number of political attendees
    events_df['political_attendees'] = results.apply(lambda x: x[3])  # Political attendees
    # Calculate the percentage of political attendees
    events_df['percent_political'] = events_df['n_political_attending'] / events_df['n_attending']

    return events_df

# Function to update user number of events attended based on events dataset
def update_user_events_attended(events_df, users_df):
    # Count the number of events each user has attended
    valid_user_ids = set(users_df['hashed_id'])  # Get the set of valid user IDs from users_df
    user_counts = Counter(
        user_id for user_list in events_df['attending'] 
        for user_id in ast.literal_eval(user_list) 
        if user_id in valid_user_ids  # Only count users that are already in users_df
    )

    # Update the 'events_attended' column in the users DataFrame
    users_df['events_attended'] = users_df['hashed_id'].map(user_counts).fillna(0).astype(int)

    return users_df

# Function to iteratively drop events with less than 2 attendees, update the users dataset, then drop users that attend less than 2 events, update the events dataset, etc.
def drop_and_update(events_df, users_df):

    # Drop users who attend less than 2 events
    users_df = users_df[users_df['events_attended'] >= 2].copy()

    # Update the number of events attended for each user
    events_df = update_and_count_attendees(events_df, users_df)
    users_df = update_user_events_attended(events_df, users_df)
    
    # Drop events with less than 2 political attendees
    events_df = events_df[events_df['n_political_attending'] >= 2].copy()

    # Update attendees and counts
    events_df = update_and_count_attendees(events_df, users_df)
    users_df = update_user_events_attended(events_df, users_df)

    return events_df, users_df

# Function to loop through the drop_and_update function as many times as needed, and return the final datasets, number of users and events dropped, and number of iterations
def drop_and_update_loop(events_df, users_df, max_iterations=10):
    # Initialize counters
    num_iterations = 0
    num_users_dropped = 0
    num_events_dropped = 0

    # Print total number of events and users before dropping
    original_user_count = users_df.shape[0]
    original_event_count = events_df.shape[0]
    print("Total number of users before dropping:", original_user_count)
    print("Total number of events before dropping:", original_event_count)

    # Loop until the maximum number of iterations is reached
    while num_iterations < max_iterations:
        prev_users = users_df.shape[0]
        prev_events = events_df.shape[0]

        # Drop and update the datasets
        events_df, users_df = drop_and_update(events_df, users_df)

        # Count the number of users and events dropped in this iteration
        num_users_dropped_iter = prev_users - users_df.shape[0]
        num_events_dropped_iter = prev_events - events_df.shape[0]

        # Update the total number of users and events dropped
        num_users_dropped += num_users_dropped_iter
        num_events_dropped += num_events_dropped_iter

        # Update the number of iterations
        num_iterations += 1

        # Break the loop if no users or events were dropped in this iteration
        if num_users_dropped_iter == 0 and num_events_dropped_iter == 0:
            break
        print(f"Iteration {num_iterations}: {num_users_dropped_iter} users dropped, {num_events_dropped_iter} events dropped")

    print("Final number of iterations:", num_iterations)
    print("Total number of users dropped:", num_users_dropped)
    print("Total number of events dropped:", num_events_dropped)
    print("Total number of users after dropping:", users_df.shape[0])
    print("Total number of events after dropping:", events_df.shape[0])
    return events_df, users_df

