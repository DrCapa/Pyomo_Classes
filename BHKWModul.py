from pyomo.environ import *


class BHKWModel:
    def __init__(self, m, df_BHKW):
        self.m = m
        self.df_BHKW = df_BHKW
        self.define_variables()
        self.define_constraints()

    def define_variables(self):
        self.m.BHKW_Bin = Var(self.m.t,
                              within=Binary,
                              doc='Online')
        self.m.BHKW_Gas = Var(self.m.t,
                              domain=NonNegativeReals,
                              doc='Fuel Consumption')
        self.m.BHKW_Power = Var(self.m.t,
                                domain=NonNegativeReals,
                                doc='Power Production')
        self.m.BHKW_Heat = Var(self.m.t,
                               domain=NonNegativeReals,
                               doc='Heat Production')

    def define_constraints(self):
        self.m.PowerMaxConstraint = Constraint(self.m.t,
                                               rule=self.power_max_constraint_rule)
        self.m.PowerMinConstraint = Constraint(self.m.t,
                                               rule=self.power_min_constraint_rule)
        self.m.GasConstraint = Constraint(self.m.t,
                                          rule=self.gas_constraint_rule)
        self.m.HeatConstraint = Constraint(self.m.t,
                                           rule=self.heat_constraint_rule)

    def power_max_constraint_rule(self, m, t):
        return m.BHKW_Power[t] <= self.df_BHKW.loc['Max', 'Power'] * m.BHKW_Bin[t]

    def power_min_constraint_rule(self, m, t):
        return self.df_BHKW.loc['Min', 'Power'] * m.BHKW_Bin[t] <= m.BHKW_Power[t]

    def gas_constraint_rule(self, m, t):
        # Gas = a*Power+b*Bin
        a = (self.df_BHKW.loc['Max', 'Gas'] -
             self.df_BHKW.loc['Min', 'Gas']) / (self.df_BHKW.loc['Max', 'Power'] -
                                                self.df_BHKW.loc['Min', 'Power'])
        b = self.df_BHKW.loc['Max', 'Gas'] - a * self.df_BHKW.loc['Max', 'Power']
        return m.BHKW_Gas[t] == a * m.BHKW_Power[t] + b * m.BHKW_Bin[t]

    def heat_constraint_rule(self, m, t):
        # Heat = a*Power+b*Bin
        a = (self.df_BHKW.loc['Max', 'Heat'] -
             self.df_BHKW.loc['Min', 'Heat']) / (self.df_BHKW.loc['Max', 'Power'] -
                                                 self.df_BHKW.loc['Min', 'Power'])
        b = self.df_BHKW.loc['Max', 'Heat'] - a * self.df_BHKW.loc['Max', 'Power']
        return m.BHKW_Heat[t] == a * m.BHKW_Power[t] + b * m.BHKW_Bin[t]
