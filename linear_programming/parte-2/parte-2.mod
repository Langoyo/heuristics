# SETS
# ------------------------------------------------------------------------------------------------------------------------------------------
# PART 1
# Set which contains the planes in the first problem and the second problem
set PLANES;
# Set which contains the tickets in the first problem
set TICKETS;

# ------------------------------------------------------------------------------------------------------------------------------------------
# PART 2
# Set which contains the planes in the second problem
# Set that contains the four runways in the second problem
set RUNWAYS;
# Set which contains the six slots that can be in a runway
set SLOTS;

/*
To state the sixth restriction in which two contiguous slots cannot be assigned
at the same time, we make a set (CONSECUTIVE) containing the sets of the different
pairs of slots: e.g.(slot0,slot1), (slot1,slot2). 
To index each tuple in the CONSECUTIVE set we use another set: 
GROUPS, which ranges from one to five.  
*/
set GROUPS;
set CONSECUTIVE {GROUPS} within SLOTS;

# PARAMS
# ------------------------------------------------------------------------------------------------------------------------------------------
# PART 1
# Indicates the price of each ticket
param TICKET_PRICE{t in TICKETS};

# Indicates the weight each type of tickets adds to the plane
param TICKET_BAGGAGE{t in TICKETS};

# Indicates the maximum number of seats in each plane
param PLANE_SEATS{p in PLANES};

# Indicates the maximum amount of kilograms of each plane
param PLANE_CAPACITY{p in PLANES};
# ------------------------------------------------------------------------------------------------------------------------------------------
# PART 2
# Indicates the starting time of a slot
param SLOT_TIME{s in SLOTS};
# Indicates the landing time of a plane
param ARRIVAL_TIME{p in PLANES};
# Indicates the number of €/min that the delay of each plane causes
param PRICE_PENALTY{p in PLANES};
# Indicates the time a plane runs out of fuel
param MAX_TIME{p in PLANES};
# Indicates which slots can be assigned to our airline
param SLOT_AVAILABLE{r in RUNWAYS, s in SLOTS};


# DECISION VARIABLES
# ------------------------------------------------------------------------------------------------------------------------------------------
# We use a decision variable that stores the amount of tickets of each type for each plane.
var quantity{p in PLANES, t in TICKETS} integer;
# We use a binary variable for each combination of runway, slot and plane.
# If the assignment is made we have 1, otherwise 0
var assignment{r in RUNWAYS, p in PLANES,  s in SLOTS} binary;

# OPTIMIZATION FUNCTION
# ------------------------------------------------------------------------------------------------------------------------------------------
# To combine both models, merge both objective functions. The objective is to obtain as much profit as possible. To do so we subtract to the money
# obtained by the ticktes in part 1 the money lost because of delays in part 2.
maximize PROFIT:
 sum{p in PLANES, t in TICKETS} quantity[p,t]*TICKET_PRICE[t] -
 sum{r in RUNWAYS, p in PLANES,  s in SLOTS} assignment[r,p,s] * ((SLOT_TIME[s]-ARRIVAL_TIME[p]) * PRICE_PENALTY[p]);

# CONSTRAINTS
# ------------------------------------------------------------------------------------------------------------------------------------------
# PART 1

#CONSTRAINT #1:It is not allowed to sell more tickets for an airline than its number of available seats.
s.t. airline_seats: sum{p in PLANES, t in TICKETS} quantity[p,t] <= sum{p in PLANES} PLANE_SEATS[p];

#CONSTRAINT #2:It is strictly forbidden to exceed the maximum capacity of each airplane.

s.t. plane_capacity {p in PLANES}:
 sum{t in TICKETS} quantity[p,t]*TICKET_BAGGAGE[t] <= PLANE_CAPACITY[p];

#CONSTRAINT #3: At least, 20 leisure plus airplane tickets should be offered for each airplane, and at least 10 business plus
#airline tickets for each airplane as well.

s.t. leisure_tickets {p in PLANES}:
 quantity[p,'leisure'] >= 20;

s.t. business_tickets {p in PLANES}:
 quantity[p,'business'] >= 10;

#CONSTRAINT #4: Because this is a low-cost company, the number of standard air tickets should be at least the 60 % of the
#overall number of airline tickets offered.
s.t. tickets_proportion:
 sum{p in PLANES} quantity[p,'standard'] >= 0.6*sum{p in PLANES, t in TICKETS} quantity[p,t];

#CONSTRAINT EXTRA: Each plane cannot sell more tickets than seats are available
s.t. plane_max_tickets {p in PLANES}:
 sum{t in TICKETS} quantity[p,t] <= PLANE_SEATS[p];

#PART 2
# ------------------------------------------------------------------------------------------------------------------------------------------
#CONSTRAINT 1:In all the variables that can be assigned to one plane, only one can be true.
s.t. one_plane_per_slot {p in PLANES} :
 sum{r in RUNWAYS, s in SLOTS} assignment[r,p,s]=1;

#CONSTRAINT 2: No slot can have more than one plane so for each slot all the possible planes have to add up to one if the slot is
# finally assigned or to 0 if the slot is not assigned
s.t. one_slot_per_plane {r in RUNWAYS, s in SLOTS} :
sum{p in PLANES} assignment[r,p,s]<=1;

#CONSTRAINT 3: The available slots can be either 1 or 0 but the unavailable slots must always be 0
s.t. forbidden_slots {r in RUNWAYS, s in SLOTS}:
sum{p in PLANES} assignment[r,p,s] <= SLOT_AVAILABLE[r,s];

#CONSTRAINT 4: The arrival time of a plane must be earlier than the slot starting time. Then arrival time < slot time
# We multiply by the decision variable to perform it if that combination is assigned.
s.t. after_starting_time {p in PLANES, s in SLOTS}:
 sum{r in RUNWAYS} (ARRIVAL_TIME[p]-SLOT_TIME[s])*assignment[r,p,s]<=0;

#CONSTRAINT 5: One plane has to be assigned a slot that starts before it runs out of fuel.
s.t. before_max_time { p in PLANES, s in SLOTS}:
 sum{r in RUNWAYS} (SLOT_TIME[s]-MAX_TIME[p])*assignment[r,p,s]<=0;

#CONSTRAINT 6: Two consecutive slots cannot be assigned for security.
# Here we first go through every possible runway and pairs of sets grouped in GROUPS. We make sure that in each pair
# of slots we cannot obtain more than one plane.

# The data for this part is:

#set GROUPS := one two three four five;
#set SLOTS := slot0 slot1 slot2 slot3 slot4 slot5;
#set CONSECUTIVE [one] := slot0 slot1;
#set CONSECUTIVE [two] := slot1 slot2;
#set CONSECUTIVE [three] := slot2 slot3;
#set CONSECUTIVE [four] := slot3 slot4;
#set CONSECUTIVE [five] := slot4 slot5;

s.t. not_contiguous {r in RUNWAYS, g in GROUPS}: 
sum{s in CONSECUTIVE[g], p in PLANES} assignment[r,p,s] <= 1;
