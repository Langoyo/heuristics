from collections import deque
import copy

#Definition of the object class
class Object:
    #Constructor of an object 
    def __init__(self, band, hour):
        #The band where the object is placed
        self.band = band
        #The hour in which the object is measurable
        self.hour = hour
        #The state of the object either measured or not measured
        self.measured = False
    
    #Method to change the state of an object
    def measure(self):
        self.measured = True

#Definition of the object class
class Satellite:
     #Constructor of an object 
    def __init__(self, bands, battery_recharge, downlink_cost, measurement_cost, turn_cost, max_battery, hour):
        #Storing the initial battery that will be changing over time, we assume this battery is the maximum at the beginning
        self.battery = max_battery
        #Storing the first band the satellite can measure in. for computation purposes we will always take self.bands and self.bands+1
        self.bands = bands
        #Storing the units of energy recharged by using the operator recharge
        self.battery_recharge = battery_recharge
        #Storing the units of energy used by using the operator downlink
        self.downlink_cost = downlink_cost
        #Storing the units of energy used by using the operator measure
        self.measurement_cost = measurement_cost
        #Storing the units of energy used by using the operator turn
        self.turn_cost = turn_cost
        #Storing the maximum battery the satellite can have
        self.max_battery = max_battery
        #Storing the hour in which the satellite is at the moment
        self.hour = hour
        #Storing the objects the satellite has measured for downlink purposes
        self.measurements_stack = []
        #Storing the initial band in which the satellite is placed, for h2 heuristic purposes
        self.original_bands = bands
    
    #Method to check if we are able of doing a certain operation in terms of battery
    def check_battery(self, cost):
        return self.battery >= cost
    
    #Method to check if an object can be measured from a satellite
    def check_measurement_object(self, band, hour):
        return((self.bands - band == 0 or self.bands - band == -1) and self.hour % 12 == hour)   
    
    #Method to use the downlink operator
    def downlink(self):
        to_return = self.measurements_stack.pop()
        #Decreasing battery of the satellite 
        self.battery -= self.downlink_cost
        return to_return
    
    #Method for checking if an object can be downlinked
    def can_downlink(self):
        return (self.check_battery(self.downlink_cost) and len(self.measurements_stack) > 0)
    
    #Method for checking the maximum battery
    def is_battery_full(self):
        return self.battery == self.max_battery
    
    #Method to charge the battery of a satellite
    def recharge(self):
        #Checking the max battery is not exceeded
        if self.battery < self.max_battery:
            if (self.battery + self.battery_recharge) > self.max_battery:
                self.battery = self.max_battery
            else:
                self.battery = self.battery + self.battery_recharge
                return True
        return False
    
    
    def measure(self, object_index):
        """
        Stores the object and decreases the battery
        """
        self.battery -= self.measurement_cost
        self.measurements_stack.append(object_index)
    
    
    def can_measure_battery(self):
        """
        Checking if we can perform the measure operation in terms of battery
        """
        self.check_battery(self.measurement_cost)
    
    #Method for the turn operations
    def turn(self, band):
        """
        True for forward and False for backwards
        """
        self.battery -= self.turn_cost
        if band:
            self.bands = self.bands + 1
        else:
            self.bands = self.bands -1
    
    def next_hour(self):
        """
        Method to update the hour
        """
        self.hour = self.hour + 1
    
    def can_move_bands(self, num_bands):
        """
        Method to check to how many bands a satellite can turn
        """
        if(self.can_move_battery()):
            if self.bands == 0 or self.bands == num_bands:
                return 1
            else:
                return 2
        return -1
    
    def can_move_battery(self):
        """
        Method to check if a satellite can turn in terms of battery   
        """
        return self.check_battery(self.turn_cost)

    def get_hour(self):
        """
        Method to get the current hour of a satellite
        """
        return self.hour % 12
#Definition of the state class
class State_t:
    def __init__(self, satellites, objects, parent = None, cost = 0, downlinked_objects_counter=0, heuristic = "h1"):
        #Storing the list of satellites
        self.satellites = copy.deepcopy(satellites)
        #Storing the list of objects
        self.objects = copy.deepcopy(objects)
        #Storing the parent from which this node was generated for backtracking purposes
        self.parent = parent
        #Storing the accumulated cost of energy by the actions of all satellites
        self.cost = cost
        #Storing the number of downliked objects
        self.downlinked_objects_counter = downlinked_objects_counter
        #Storing the operation taken by this state with respect to the parent
        self.action_taken = ""
        #Storing the heuristic being implemented
        self.heuristic = heuristic
    #Method to calculate the cost of expanding a node as f=g(cost in energy)+h(heuristic cost)
    def f(self):
        """
        Calculates the addition of the cost function and the heuristic funciton for the current state
        Chooses one heuristic or the other depending of the initial argument given.
        """
        if self.heuristic == "h1":
            return self.get_cost() + self.h1()
        return self.get_cost() + self.h2()
    #Method to get the accumulated cost of energy
    def get_cost(self):
        """
        Returns the cost of the curren state
        """
        return self.cost
    #Method that implements the first heuristic
    def h1(self):
        """
        This corresponds to the h1 heuristic defined in the report
        It is based on the differnce in bands of all the satellites with all the objects to know if the
        objects should move. Then, it is divided by the number of satellites to avoid overcounting.
        """
        result = 0
        for sat in self.satellites:
            for obj in self.objects:

                # Only add if the object is yet to be measured
                if(not obj.measured):
                    # If the object is above the satellite we take into account that the satellite can see one band further
                    if(sat.bands + 1 < obj.band):
                        result += obj.band - 1 - sat.bands
                        
                        
                    # If the object is in an inferior band we calculate the distance normally
                    elif(obj.band  < sat.bands):
                        result += sat.bands - obj.band
        # Doing an average of the cost for all the satellites to get an estimation
        result /= len(self.satellites)
        result += len(self.objects) - self.downlinked_objects_counter

        return result
    
    def h2(self):
        """
        This heuristic corresponds to h2 in the report.
        It attempts to benefit those states in which there are more measured and donwlinked objects.
        Also, it penalizes the turning operation of satellites as, in our inital configuration the satellites cover all the bands.
        We assumed we could do it this way beacuse in the problem is not specified and also the example is given in this way.
        As the objective is to minimize the energy cost, we choose the IDLE operation over the turns. 
        """
        result = 0
        result += len(self.objects) - self.downlinked_objects_counter
        #Penalising the turns as they use up energy
        for object in self.objects:
            if(not object.measured):
                result+=1
        for satellite in self.satellites:
            result +=  abs(satellite.bands - satellite.original_bands)
        return result
        

    def is_goal(self):
        """
        Checks if a node represents a goal state
        """
        
        # If all the satellites have the same hour and all the objects have been downloaded
        # As we delayed the satellites, it may happen that with just the first satellite's operation the problem finishes
        # and the other satellites remain delayed. But for printing porpueses and in order to avoid this implementation decision to be
        # reflected on the result, we enforce that all the satellites are synchronized
        first_satellite_hour = self.satellites[0].hour
        last_satellite_hour = self.satellites[len(self.satellites)-1].hour
        return self.downlinked_objects_counter == len(self.objects) and (first_satellite_hour == last_satellite_hour)

    def increase_cost(self, cost):
        self.cost = self.cost + cost



    def get_steps(self):
        """
        Returns the number of steps taken by the less delayed satellite which is always satellite 0
        """
        return self.satellites[0].hour

    def save_action(self, action):
        """
        Saves a string with the action into a the state
        """
        self.action_taken = action
          


    def children(self):
        # Vector of children states to be returned
        children = []

        #Getting new satellite index to be expanded
        next_index = self.get_next_satellite_index()

        #-----------IDLE operation---------------------------------
        
        if self.satellites[next_index].battery == self.satellites[next_index].max_battery:
            # Copying current state
            idle_child = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)
                
            # Moving satellite to next hour
            idle_child.satellites[next_index].next_hour()

            # Save action
            idle_child.action_taken = "SAT" + str(next_index+1) + ": IDLE"

            children.append(idle_child)

        #----------- CHARGE battery--------------------------------
        
        if(not self.satellites[next_index].is_battery_full()):
            recharge_child = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)
            
            # We recharge in the child
            recharge_child.satellites[next_index].recharge()

            #Moving the satellite to the next hour
            recharge_child.satellites[next_index].next_hour()

            # Save action
            recharge_child.action_taken= "SAT"+ str(next_index+1) + ": Charge"

            # Adding to the return vector the new state
            children.append(recharge_child)

        # -------------MEASUREMENTS operation------------
                
        # Getting an object that can be measured
        object_to_measure = self.check_ability_measurement(next_index)

        if(object_to_measure > -1):
            
            #Creating a child
            measure_child = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)
            
            # Measure the object
            measure_child.objects[object_to_measure].measure()

            # Store the object in the satellite stack
            measure_child.satellites[next_index].measure(object_to_measure)

            # Increase time
            measure_child.satellites[next_index].next_hour()

            # Increase cost
            measure_child.increase_cost(self.satellites[next_index].measurement_cost)
            
            # Save action
            measure_child.action_taken = "SAT"+ str(next_index+1) + ": Measure O" + str(object_to_measure+1)
            
            # Appending the new child
            children.append(measure_child)

        # -----------DOWNLINK operation-------------
        
        # Checking that the current satellite can downlink
        if self.satellites[next_index].can_downlink():
            downlink_child = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)
            
            # Creating new node
            object_index = downlink_child.satellites[next_index].downlink()
            
            # Increase counter of downlinked objects
            downlink_child.downlinked_objects_counter += 1

            # Increase time
            downlink_child.satellites[next_index].next_hour()

            # Increase cost
            downlink_child.increase_cost(self.satellites[next_index].downlink_cost)
            
            # Save action
            downlink_child.action_taken = "SAT"+ str(next_index+1) + ": Downlink O" + str(object_index+1)

            # Push object
            children.append(downlink_child)
            
        # -------------TURN operation---------------

        # Get number of turn operations that can be made
        movements = self.satellites[next_index].can_move_bands(len(self.satellites))
        
        #  In case only one can be made, it is beacuse it is at the first visibility band or the last
        if(movements == 1):
            moving_child = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)

            # If the element is at the beginning, we move it to the next visibility band
            if self.satellites[next_index].bands == 0:
                moving_child.satellites[next_index].turn(True)

            # If it is at the end, to the previous visibility band
            else:
                moving_child.satellites[next_index].turn(False)
            
            # Increase the time of the satellite
            moving_child.satellites[next_index].next_hour()

            # Increasing the cosst of the node with the operation move
            moving_child.increase_cost(self.satellites[next_index].turn_cost)
            
            # Storing the action tanken by the satellite
            moving_child.action_taken = "SAT" + str(next_index+1) + ": Turn"

            # Appending the child
            children.append(moving_child)
        
        # Case where the satellite can make two moves
        elif (movements == 2):
            # Creating one child to move down and another to move up
            moving_child1 = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)
            moving_child2 = State_t(self.satellites, self.objects, self, self.cost, self.downlinked_objects_counter,self.heuristic)

            # In one child, one satellite moves up and the other down
            moving_child1.satellites[next_index].turn(True)
            moving_child2.satellites[next_index].turn(False)

            # Increasing their time
            moving_child1.satellites[next_index].next_hour()
            moving_child2.satellites[next_index].next_hour()

            # Incresing their cost
            moving_child1.increase_cost(self.satellites[next_index].turn_cost)
            moving_child2.increase_cost(self.satellites[next_index].turn_cost)
            
            # Storing their acction
            moving_child1.action_taken = "SAT" + str(next_index+1) + ": Turn"
            moving_child2.action_taken = "SAT" + str(next_index+1) + ": Turn"
            
            # Appending the childs
            children.append(moving_child1)
            children.append(moving_child2)
        
        return children              
    

    def check_ability_measurement(self, next_index):
        """
        Checks if a satellite can measure any object

        * Returns:
        - -1 if it cannot measure
        - the index of the object in the list if it can
        """
        # If the satellite has energy to measure
        energy = self.satellites[next_index].battery >= self.satellites[next_index].measurement_cost

        if not energy:
            return -1

        for object_index in range(len(self.objects)):
            # If the object and satellite are in the same position
            measurable = self.satellites[next_index].check_measurement_object(self.objects[object_index].band, self.objects[object_index].hour)
            # If the current object has not been measured
            not_measured = not(self.objects[object_index].measured)
            
            if measurable and not_measured:
                return object_index
        return -1

    def get_next_satellite_index(self):
        """
        Returns the index of the vector of satellites which corresponds with the most delayed satellite
        """
        
        # Stores the index of the satellite most delayed
        first_satellite_hour = self.satellites[0].hour
        
        # Searching for a more delayed one
        for index_satellite in range(len(self.satellites)):
            if(first_satellite_hour > self.satellites[index_satellite].hour):
                return index_satellite
        return 0

 
        
        
    def __lt__(self, other):
        """ 
        Overriding less that method for the built in priority queue based on the cost and the heuristic function of a state
        """
        return self.f() < other.f()

    def __hash__(self):
        """
        Function that calculates a hash with the most relevant information of a state so that the
        built in set container can compare different state.
        The members that uniquely identify a state are:
        - The measured state of the objects
        - The Battery, hour mod 12 and the band of the satellite
        - The number of objects that have been downlinked
        """
        to_hash = ""
        # Storing the state of each object
        for object in self.objects:
            to_hash += str(object.measured)

        # Storing the state of each satellite
        for satellite in self.satellites:
            to_hash += str(satellite.battery) + str(satellite.bands) + str(satellite.hour%12)
        
        # Adding the downlinked object counter
        to_hash+= str(self.downlinked_objects_counter)
        return hash(to_hash)

    def __eq__(self, other):
        """
        Overrides the object equal member function in case the hash function fails in the hash fails in the set
        """
        # Storing the state of each object
        if(self.downlinked_objects_counter != other.downlinked_objects_counter):
            return False

        # Storing the state of each satellite
        for object_index in range(len(self.objects)):
            if (self.objects[object_index].measured != other.objects[object_index].measured):
                return False
        
        # Adding the downlinked object counter
        for satellite_index in range(len(self.satellites)):
            if(self.satellites[satellite_index].battery != other.satellites[satellite_index].battery
            or self.satellites[satellite_index].bands != other.satellites[satellite_index].bands
            or self.satellites[satellite_index].hour%12 != other.satellites[satellite_index].hour%12):
                return False
        return True
    

    

    """
    OTHER HEURISTICS ATTEMPTED
     def h4(self):
        # Heuristic function that measures the distance between satellites and remaining objects to be measured
        # This heuristic tries to benefit the closenenss of satellites with all the objects of the problem in terms of bands and hours
        # However, we believe it overestimates the cost to reach the goal because it takes into account the difference in hours, representing
        # the IDLE operation. This operation has zero cost so we did not use it
        
        result = 0
        for sat in self.satellites:
            for obj in self.objects:

                # Only add if the object is yet to be measured
                if(not obj.measured):
                    # If the object is above the satellite we take into account that the satellite can see one band further
                    if(sat.bands + 1 < obj.band):
                        result += obj.band - 1 - sat.bands
                    # If the object is in an inferior band we calculate the distance normally
                    elif(obj.band  < sat.bands):
                        result += sat.bands - obj.band
                    if sat.hour%12 <= obj.hour:
                        result += obj.hour - sat.hour%12
                    else:
                        result += obj.hour - sat.hour%12
        result /= len(self.satellites)
        result += len(self.objects) - self.downlinked_objects_counter

        return result

    def h3(self):

        # This heuristic behaves the same way as before but taking out the bands differnce. Again, it overestimates the cost and,
        # in addition, it is less informed than the precious one.
        

        result = 0
        for sat in self.satellites:
            for obj in self.objects:

                # Only add if the object is yet to be measured
                if(not obj.measured):
                    if sat.hour%12 <= obj.hour:
                        result += obj.hour - sat.hour%12
                    else:
                        result += obj.hour - sat.hour%12
        result += len(self.objects) - self.downlinked_objects_counter
        return result
    """