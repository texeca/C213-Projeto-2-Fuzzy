import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def criar_controlador_fuzzy():
    erro = ctrl.Antecedent(np.arange(0, 31, 0.5), 'erro')
    delta_erro = ctrl.Antecedent(np.arange(-10, 10, 0.5), 'delta_erro')
    potencia_motor = ctrl.Consequent(np.arange(0, 101, 1), 'potencia_motor')

    erro['MP'] = fuzz.trimf(erro.universe, [0, 0, 0.5])
    erro['P'] = fuzz.trimf(erro.universe, [0.2, 0.5, 1.5])
    erro['M']  = fuzz.trimf(erro.universe, [1.0, 3.0, 8.0])
    erro['G'] = fuzz.trimf(erro.universe, [5, 20, 31])
    

    delta_erro['NG'] = fuzz.trimf(delta_erro.universe, [-10, -2, -0.5])
    delta_erro['NP'] = fuzz.trimf(delta_erro.universe, [-1, -0.2, -0.05])
    delta_erro['Z'] = fuzz.trimf(delta_erro.universe, [-0.3, 0, 0.3])
    delta_erro['PP'] = fuzz.trimf(delta_erro.universe, [0.05, 0.2, 1])
    delta_erro['PG'] = fuzz.trimf(delta_erro.universe, [0.5, 2, 10])

    potencia_motor['MB'] = fuzz.trimf(potencia_motor.universe, [0, 2, 8])
    potencia_motor['B'] = fuzz.trimf(potencia_motor.universe, [5, 20, 40])
    potencia_motor['M'] = fuzz.trimf(potencia_motor.universe, [35, 55, 75])
    potencia_motor['A'] = fuzz.trimf(potencia_motor.universe, [65, 78, 88])
    potencia_motor['MA'] = fuzz.trimf(potencia_motor.universe, [75, 85, 90])

    regras = [
        ctrl.Rule(erro['MP'] & delta_erro['PG'], potencia_motor['B']),
        ctrl.Rule(erro['MP'] & delta_erro['PP'], potencia_motor['MB']),
        ctrl.Rule(erro['MP'] & delta_erro['Z'], potencia_motor['MB']),
        ctrl.Rule(erro['MP'] & delta_erro['NP'], potencia_motor['MB']),
        ctrl.Rule(erro['MP'] & delta_erro['NG'], potencia_motor['MB']),

        ctrl.Rule(erro['P'] & delta_erro['PG'], potencia_motor['M']),
        ctrl.Rule(erro['P'] & delta_erro['PP'], potencia_motor['B']),
        ctrl.Rule(erro['P'] & delta_erro['Z'], potencia_motor['B']),
        ctrl.Rule(erro['P'] & delta_erro['NP'], potencia_motor['MB']),
        ctrl.Rule(erro['P'] & delta_erro['NG'], potencia_motor['MB']),
        
        ctrl.Rule(erro['M'] & delta_erro['PG'], potencia_motor['A']),
        ctrl.Rule(erro['M'] & delta_erro['PP'], potencia_motor['M']),
        ctrl.Rule(erro['M'] & delta_erro['Z'], potencia_motor['M']),
        ctrl.Rule(erro['M'] & delta_erro['NP'], potencia_motor['B']),
        ctrl.Rule(erro['M'] & delta_erro['NG'], potencia_motor['B']),
        
        ctrl.Rule(erro['G'] & delta_erro['PG'], potencia_motor['MA']),
        ctrl.Rule(erro['G'] & delta_erro['PP'], potencia_motor['MA']),
        ctrl.Rule(erro['G'] & delta_erro['Z'], potencia_motor['MA']),
        ctrl.Rule(erro['G'] & delta_erro['NP'], potencia_motor['M']),
        ctrl.Rule(erro['G'] & delta_erro['NG'], potencia_motor['M']),
    ]

    sistema = ctrl.ControlSystem(regras)
    sim = ctrl.ControlSystemSimulation(sistema)
    return sim
