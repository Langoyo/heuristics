import constraint
import sys
import json

def same_antenna(*x):
    """
    Checks that all the variables have the same value.
    """
    return all(elem == x[0] for elem in x)
    



def diff_antenna(sat1,sat2):
    """
    Checks that two satellites don't have the same antenna
    """
    return sat1 != sat2


def separate_frames(data):
    """
    Receives the data dictionary extracted from the input JSON
    Separates all the variables into two sets:
    - before noon
    - after noon 
    """
    before_noon = []
    after_noon = []
    # data items is a dictionary in which the keys are the satellites and the elements are keys
    for satellite, slots in data.items():
        for slot in slots.keys():
            # Getting the starting time of the slot (they are represented as <start>-<end>)
            start_time = int(slot.split("-")[0])
            #  Dividing variables before and after noon
            if start_time < 12:
                before_noon.append(satellite + " " + slot)
            else:
                after_noon.append(satellite + " " + slot)
    return before_noon, after_noon

if __name__ == '__main__':

    file = sys.argv[1]

    # Reading the input file that contains the data in json format
    with open(file) as json_file:
        file = json.load(json_file)
        """
        The JSON file has two main parts:
        data: which specifies the combination of satellites and slots and their domain
        constraints: which specifies the values for each constraint 
        """
        data = file["data"]
        constraints = file["constraints"]
        constraint_2 = constraints["constraint_2"]
        constraint_3 = constraints["constraint_3"]
        constraint_4 = constraints["constraint_4"]
        constraint_5 = constraints["constraint_5"]
        


    # Instantiating a CSP problem
    problem = constraint.Problem()

    # Getting the variables from the input JSON and introducing them into the problem.
    # The variables are of the form SAT12 - 16-18:
    # The domains are lists of antennas.
    for satellite, slots in data.items():
        for slot, antennas in slots.items():
            problem.addVariable(satellite + ' ' + slot, antennas)

    # Second constraint to have satellites use the same antenna
    # The list same_antennas store all the variables that must have the same antenna value.
    same_anetennas = []
    # Iterating over every satellite specified in the constraint
    for satellite in constraint_2:
        # We need to get every slot of each satellite
        for slot in data[satellite].keys():
            same_anetennas.append(satellite + " " + slot)
    problem.addConstraint(same_antenna,same_anetennas)
        
    
    # Third constraint to have satellites use different antennas
    # different is a list that contains lists with all the slots of each satellite
    # The idea is to ensure that elements from each list are different from elements in any other list
    different = []
    # Going through every satellite specified in the constraint
    for satellite in constraint_3:
        # Store in partial results all the variables that are realted to one satellite
        partial_result = []
        for slot in data[satellite].keys():
            partial_result.append(satellite + " " + slot)
        different.append(partial_result)
        
    #Iterating over the first satellite
    for satellite_i in range(len(different)-1):
        #Iterating over the satellite's timeslots
        for time_slot_i in range(len(different[satellite_i])):
            #Iterating over the next satellites
            for satellite_j in range(satellite_i + 1,len(different)):
                #Iterating over the next satellite's timeslot
                for time_slot_j in range(len(different[satellite_j])):
                    problem.addConstraint(diff_antenna, (different[satellite_i][time_slot_i], different[satellite_j][time_slot_j]))
    
    
    #Fourth constraint to avoid wrong satellite configurations
    # wrong_config is a list that contains lists with all the possible combinations for each satellite
    # The idea is to ensure that elements from each list are different from elements in any other list
    wrong_config = []
    # We get every variable that is specified in the constraint
    for pair in constraint_4:
        partial_result = []
        # The constraint specifies the pair: [satellite, antenna]
        satellite = pair[0]
        # Getting all the variables of one satellite
        for slot in data[satellite].keys():
            partial_result.append(satellite + " " + slot)
        wrong_config.append(partial_result)

    #Iterating over the first satellite
    for satellite_i in range(len(wrong_config)-1):
        #Iterating over the satellite's timeslots
        for time_slot_i in range(len(wrong_config[satellite_i])):
        #Iterating over the next satellites
            for satellite_j in range(satellite_i + 1,len(wrong_config)):
                #Iterating over the next satellite's timeslot
                for time_slot_j in range(len(wrong_config[satellite_j])):
                    # We get the forbidden atennas for each variable
                    antenna1 = constraint_4[satellite_i][1]
                    antenna2 = constraint_4[satellite_j][1]                    
                    problem.addConstraint(lambda sat1,sat2:
                                            not(sat1==antenna1 and sat2==antenna2), 
                                            (wrong_config[satellite_i][time_slot_i],wrong_config[satellite_j][time_slot_j]))
    
    # Fifth constraint to use satellites in the correct timeslot
    # We separate all the variables into two sets, the assigned satellites before noon and after noon
    before_noon, after_noon = separate_frames(data)
    #problem.addConstraint(same_time_sat,(before_noon,after_noon))

    # For every pait of satellites, we check that they are not assigned to the same slot.
    for before_satellite in before_noon:
        for after_satellite in after_noon:

            for antenna_i in range(len(constraint_5)-1):
                for antenna_j in range(antenna_i + 1, len(constraint_5)):
                    print("Satellites to be compared"+before_satellite +" "+after_satellite)
                    print("Constraint satellites"+constraint_5[antenna_i]+" "+constraint_5[antenna_j])
                    problem.addConstraint(lambda before_satellite, after_satellite:
                                not(            
                                    (before_satellite == constraint_5[antenna_i] and after_satellite == constraint_5[antenna_j]) 
                                    or 
                                    (before_satellite == constraint_5[antenna_j] and after_satellite == constraint_5[antenna_i])
                                    ),(before_satellite,after_satellite))
    # We print the problem solution
    solutions = problem.getSolutions() 
    print("There were found {}".format(len(solutions)))
    
    if len(solutions)>0:
        print("An example of solution is:")
        solution = solutions[0]
        for variable,value in solution.items():
            print("{} is assigned to {}".format(variable,value))
        