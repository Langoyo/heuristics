from queue import PriorityQueue
from dataclasses import dataclass, field
from typing import Any
import time
from state import Satellite, Object, State_t
import argparse
import sys, io
import re


def BFS(initial_state):
    """
    Implementation of Breath first search algorithm
    """
    open = []
    closed = set()
    if(initial_state.is_goal()):
        return initial_state
    open.append(initial_state)
    while(len(open)>0):
        node = open.pop(0)
        children = node.children()
        closed.add(node)
        
        for child in children:
            if child.is_goal():
                return child
            if child not in closed:
                open.append(child)
            
    
def A_star(intitial_state):
    """
    Implementation of A_star algorithm
    
    *Parameters:
    - Initial state of the problem
    
    *Returns:
    - Final state of the problem
    - Number of nodes expanded to reach the solution

    """

    # Priority queue with the ordered nodes to expand
    open = PriorityQueue()

    # Set that stores expanded nodes
    closed = set()

    # Counter for the number of expansions
    expansions = 0

    # Introducing the initial state of the problem with the funcion of the node
    open.put((initial_state.f(),initial_state))
    while(not open.empty()):

        # We get the node with the lowest value of f()
        node = open.get()[1]
        
        #If the node to be expanded is a goal, we return it
        if node.is_goal():
            return node,expansions
        
        # Obtaining a list of counters
        children = node.children()

        # Update the expandion counter
        expansions+=1
        
        # Adding the node to closed
        closed.add(node)
        
        # Adding the children to open if they are not already expanded (in closed)
        for child in children:
            if child not in closed:
                open.put((child.f(),child))


def extract_data(string, pattern):
    """
    Extracts a list containing the capturing groups of a string given a regular expression
    *Parmeters:
    - string to be analyzed
    - pattern to be compared against

    *Returns:
    - list of ints with the values to be captured
    """
    # The imported module prints a warning to the standard error. We redirect the warning no to print it
    stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    # We search the capturable values in the string
    search_res=re.search(pattern,string)
    list = []
    # If possible, the values are converted to int an added to alist to be returned
    if search_res is None:
        return None
    else:
        i=1
        while (i<=search_res.lastindex):
            list.append(int(search_res.group(i)))
            i=i+1
    
    # Restoring standard error
    sys.stderr = stderr

    return list

    
    
if __name__ == '__main__':

    # Help command
    parser=argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''This program is used to search the best solution in a satellite scenario
        The initial problem configuration must the following format:
        
        "OBS: (0,1);(0,3);(1,3)"
        "SAT1: 1;1;1;1;1"
        "SAT2: 1;1;1;1;8"
        ''',
        epilog="""An example "./cosmos.sh problema.prob h2" """
    )
    parser.add_argument('directory_name', nargs='*', default=[1, 2, 3], help='Insert the file location with the intial problem configuration')
    parser.add_argument('heuristic', help='For the second argument two heuristics can be chose "h1" or "h2"')
    
    # Parsing the arguments of the problem
    args=parser.parse_args()
    
    # Opening the file and splitting it in lines
    file=open(sys.argv[1],'r')
    lines=file.readlines()

    objects = []
    satellites = []

    # Regular expressions for satellites and objects
    sat_pattern = r"(?:SAT[\d]+:\s([\d]+);([\d]+);([\d]+);([\d]+);([\d]+))"
    obj_pattern = r"\(([\d]+),([[0-9]|(?:1[0-1]))\)"
    
    # Extracting the object tuples substring
    lines_rem=lines[0].split(" ")
    
    # Getting the tuples alone
    final_objects=lines_rem[1].split(";")

    # Extracting the data of the objects and instantiating them in the list
    for i in range (0, len(final_objects)):
        obje_data = extract_data(final_objects[i],obj_pattern)
        objects.append(Object(obje_data[0],obje_data[1]))
        

    # Extracting the data of each satellite and instantiating them in their container
    # We assume that the satellites initially cover all the possible bands. They start at 0 and the following ones add +1
    # To fit all the bands the last one is two bands appart from the provious one
    # As it is not specified, we chose this configuration so that all the bands are initially covered
    bands = 0
    for i in range(1,len(lines)):
        sat_data = extract_data(lines[i],sat_pattern)
        satellites.append(Satellite(bands,sat_data[3],sat_data[1],sat_data[0],sat_data[2],sat_data[4],0))
        bands+=1
        if i != len(lines)-2:
            bands+=1
    
    
    file.close()
    
    # Creation of the initial state of the problem
    initial_state = State_t(satellites, objects, None, 0, 0, sys.argv[2])

    # Calculating the solution with A* and measuring the time
    start = time.time()
    final_state,expansions = A_star(initial_state)
    end = time.time()
    
    # Printing the statistics of the problem solution
    sys.stdout = open('problem.prob.statistics', 'w')
    print("Overall time: {:.2f}\nOverall cost: {}\n# Steps: {}\n# Expansions: {}\n".format(end-start, final_state.get_cost(), final_state.get_steps(), expansions))
    sys.stdout = sys.__stdout__
    print("Overall time: {:.2f}\nOverall cost: {}\n# Steps: {}\n# Expansions: {}\n".format(end-start, final_state.get_cost(), final_state.get_steps(), expansions))
    # Getting into a list the actions taken by each of the nodes
    number_of_satellites = len(final_state.satellites)
    actions = []
    while(final_state.parent is not None):
        actions.insert(0,final_state.action_taken)
        final_state = final_state.parent
    
    # Printing the actions taken by each node
    time_step = 0
    string_to_print = ""

    # For every action of the satellies
    for action_index in range(0,len(actions)):
        # Introducing new line and time step
        if(action_index % number_of_satellites == 0):
            time_step+=1
            # If the action is the first, we dont add a new line at the beginning
            if action_index == 0:
                string_to_print += "{}. ".format(time_step)    
            else:    
                string_to_print += "\n{}. ".format(time_step)
            # Loop to get all the satellite actions in this line
            for satellite_index in range(0,number_of_satellites):
                if action_index + satellite_index < len(actions):
                    # Printing a final comma or not depeding if it is the last satellite
                    if satellite_index == number_of_satellites-1:
                        string_to_print += "{} ".format(actions[action_index + satellite_index])
                    else:   
                        string_to_print += "{}, ".format(actions[action_index + satellite_index])

    # Printing solution    
    stdout_ = sys.stdout
    sys.stdout = open('problema.prob.output', 'w')
    print(string_to_print)
    sys.stdout = sys.__stdout__
    print(string_to_print)