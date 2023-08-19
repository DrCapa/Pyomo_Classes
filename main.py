import pandas as pd

from pyomo.opt import SolverFactory
from pyomo.environ import *
from BHKWModul import BHKWModel


# Path
path_in = '01_Input/'
path_out = '02_Output/'

# Select Solver
opt = SolverFactory('cbc')

# Create DataPortal
data = DataPortal()

# Read Time Series
data.load(filename=path_in+'Gas_Price.csv',
          index='t',
          param='Gas_Price')
data.load(filename=path_in+'Power_Price.csv',
          index='t',
          param='Power_Price')

# Read BHKW Performance Data
df_BHKW = pd.read_csv(path_in+'BHKW_Data.csv', index_col=0)

# Define abstracte model
m = AbstractModel()

# Define sets
m.t = Set(ordered=True)

# Define parameters
m.Gas_Price = Param(m.t)
m.Power_Price = Param(m.t)


# Create instance of BHKWModel
bhkw_instance = BHKWModel(m, df_BHKW)

# Define Objective Function
def obj_expression(m):
    """ Objective Function """
    return (sum(m.BHKW_Gas[t]*m.Gas_Price[t] for t in m.t) -
            sum(m.BHKW_Power[t]*m.Power_Price[t] for t in m.t))
m.obj = Objective(rule=obj_expression, sense=minimize)

# Create instanz
instance = m.create_instance(data)

# Solve the optimization problem
results = opt.solve(instance,
                    logfile=path_out+'Logfile_Output.log',
                    symbolic_solver_labels=True,
                    tee=True,
                    load_solutions=True)

# Write Results
results.write()

""" Write Output Time Series """
df_output = pd.DataFrame()
df_parameters = pd.DataFrame()
df_variables = pd.DataFrame()

for t in instance.t.data():
    # Write Parameter
    for parameter in instance.component_objects(Param, active=True):
        name = parameter.name
        df_parameters[name] = [value(parameter[t]) for t in instance.t]
    # Write Variables
    for variable in m.component_objects(Var, active=True):
        name = variable.name
        df_variables.loc[t, name] = abs(instance.__getattribute__(name)[t].value)
df_output = pd.concat([df_parameters, df_variables], axis=1)

df_output.to_csv(path_out+'Timeseries_Output.csv')
