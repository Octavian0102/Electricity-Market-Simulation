import pandas as pd
import numpy as np
import statsmodels.api as sm
from src.config import SURVEY_DATA


ExcelImport = pd.read_excel(SURVEY_DATA, sheet_name='Redispatch 3.0')
# rename columns to unique ending Rank 1 to Rank 10
num = 1
for col in ExcelImport.columns:
    if col.endswith(f'[Rank {num}]'):
        new_col_name = f'Rank {num}'
        ExcelImport.rename(columns={col: new_col_name}, inplace=True)
        num = num + 1

ExcelImportRanks = ExcelImport.iloc[:, -10:]
# create Dataframes filtering only 1 customer group and returns only the last 10 columns (Rank Information)
Privathaushalte = ExcelImport.iloc[:, -10:][
    ExcelImport['Ich gehöre zu folgender Stakeholdergruppe:'] == 'Privathaushalt']
Industrie = ExcelImport.iloc[:, -10:][ExcelImport['Ich gehöre zu folgender Stakeholdergruppe:'] == 'Industrie']
Aggregator = ExcelImport.iloc[:, -10:][ExcelImport['Ich gehöre zu folgender Stakeholdergruppe:'] == 'Aggregator']

# create a new dataframe that contains the last 10 rows of the original dataframe ExcelImportRanks
ExcelImportRanks = ExcelImport.iloc[:, -10:]
# create a matrix that contains the scenario information
# define CO2-high as 300 mid as 200 low as 100
Scenario_Matrix = pd.DataFrame({'Preis': [0.05, 0.15, 0.3, 0.05, 0.15, 0.3, 0.3, 0.15, 0.05, 0.3],
                                'CO2-Einsparung': [100, 200, 100, 200, 100, 300, 300, 200, 100, 200],
                                'Autarkie=hoch': [1, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                                'Autarkie=mittel': [0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
                                'Autarkie=gering': [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, ],
                                'Vorlaufzeit': [5, 60, 1440, 5, 5, 5, 1440, 60, 1440, 60]})
ScenarioMatrix_privat = ScenarioMatrix_Industrie = ScenarioMatrix_Aggregator = Scenario_Matrix.copy()

# transpose the matrix ExcelImportRanks
ExcelImportRanks_transposed = ExcelImportRanks.transpose()

# This double for loop goes over all rows of ExcelImportRanks which is the amount of users in the survey
# it creates a seperate Fliprank-list for every participant as a new column
# note that this is not the smoothest way. Might use dictionary if dataset gets too big
for j in range(ExcelImportRanks.shape[0]):
    exec(f'Fliprank{j + 1} = []')
    for i in range(10):
        index = \
            np.where(ExcelImportRanks_transposed.iloc[:, j].str.startswith('Szenario ' + str((chr(ord('A') + i)))))[0][
                0] + 1
        # index gibt den Wert der Zeile an, an welcher Szenario A-G gefunden wird
        exec(f'Fliprank{j + 1}.append(11-index)')
        # Der leeren Liste Fliprank wird entsprechend der gefundenen Zeile ein Wert zugeteilt

for j in range(ExcelImportRanks.shape[0]):
    Scenario_Matrix[f'Fliprank{j + 1}'] = globals()[f'Fliprank{j + 1}']

independent_variables = Scenario_Matrix[
    ['Preis', 'CO2-Einsparung', 'Autarkie=hoch', 'Autarkie=mittel', 'Autarkie=gering', 'Vorlaufzeit']]
# Definition eines neuen pandas Dataframe welches die Werte von A für die columns Preis - ... wiedergibt
independent_variables = sm.add_constant(independent_variables)
# dem Dataframe wird eine Konstante hinzugefügt. Diese gibt den Intercept der Regression an
regression_df = pd.DataFrame()
# Erstellen eines neuen leeren pandas Dataframe mit dem Namen regression_df
for j in range(ExcelImportRanks.shape[0]):
    # über alle User hinweg wird die Liste regression df mit den Parametern gefüllt
    y = Scenario_Matrix[f'Fliprank{j + 1}']
    linearRegression = sm.OLS(y, independent_variables).fit()
    regression_df[f'User{j + 1}'] = linearRegression.params[0:9]

# Erstellen der Matrix mit Flipranks analog zu oben nur für Privathaushalte
Privathaushalte_transposed = Privathaushalte.transpose()
for col in Privathaushalte_transposed.columns:
    new_col_name = f'User{col + 1}'
    Privathaushalte_transposed.rename(columns={col: new_col_name}, inplace=True)

# Create a unique list with flipranks for "Privathaushalte"
for j in range(Privathaushalte.shape[0]):
    exec(f'FliprankH{j + 1} = []')
    for i in range(10):
        index = \
            np.where(Privathaushalte_transposed.iloc[:, j].str.startswith('Szenario ' + str((chr(ord('A') + i)))))[0][0] + 1
        exec(f'FliprankH{j + 1}.append(11-index)')

for j in range(Privathaushalte.shape[0]):
    ScenarioMatrix_privat[f'FliprankH{j + 1}'] = globals()[f'FliprankH{j + 1}']

# analog use for Haushalt
regression_df_Haushalt = pd.DataFrame()
for j in range(Privathaushalte.shape[0]):
    y = ScenarioMatrix_privat[f'FliprankH{j + 1}']
    linearRegression = sm.OLS(y, independent_variables).fit()
    regression_df_Haushalt[f'User{j + 1}'] = linearRegression.params[0:9]

Haushalt_List = []
Utility_Haushalt = pd.DataFrame(
    {'Intercept': [], 'BetaPreis': [], 'BetaCO2': [], 'BetaAutarkie=hoch': [], 'BetaAutarkie=mittel': [],
     'BetaAutarkie=gering': [], 'BetaVorlaufzeit': []})
for rows in range(regression_df_Haushalt.shape[0]):
    avg_row = regression_df_Haushalt.iloc[rows].mean()
    Haushalt_List.append(avg_row)
Utility_Haushalt.loc[len(Utility_Haushalt)] = Haushalt_List
Utility_Haushalt.rename(index={0: "Utility_Haushalt"})

# Analog zu privat Haushalt für Industrie
Industrie_transposed = Industrie.transpose()
for col in Industrie_transposed.columns:
    new_col_name = f'User{col + 1}'
    Industrie_transposed.rename(columns={col: new_col_name}, inplace=True)

for j in range(Industrie.shape[0]):
    exec(f'FliprankI{j + 1} = []')
    for i in range(10):
        index = np.where(Industrie_transposed.iloc[:, j].str.startswith('Szenario ' + str((chr(ord('A') + i)))))[0][
                    0] + 1
        exec(f'FliprankI{j + 1}.append(11-index)')

for j in range(Industrie.shape[0]):
    ScenarioMatrix_Industrie[f'FliprankI{j + 1}'] = globals()[f'FliprankI{j + 1}']

regression_df_Industrie = pd.DataFrame()
# Erstellen eines neuen leeren pandas Dataframe
for j in range(Industrie.shape[0]):
    y = ScenarioMatrix_Industrie[f'FliprankI{j + 1}']
    linearRegression = sm.OLS(y, independent_variables).fit()
    regression_df_Industrie[f'User{j + 1}'] = linearRegression.params[0:9]

Industrie_List = []
Utility_Industrie = pd.DataFrame(
    {'Intercept': [], 'BetaPreis': [], 'BetaCO2': [], 'BetaAutarkie=hoch': [], 'BetaAutarkie=mittel': [],
     'BetaAutarkie=gering': [], 'BetaVorlaufzeit': []})
for rows in range(regression_df_Industrie.shape[0]):
    avg_row = regression_df_Industrie.iloc[rows].mean()
    Industrie_List.append(avg_row)
Utility_Industrie.loc[len(Utility_Industrie)] = Industrie_List
Utility_Industrie.rename(index={0: "Utility_Industrie"})

Aggregator_transposed = Aggregator.transpose()
for col in Aggregator_transposed.columns:
    new_col_name = f'User{col + 1}'
    Aggregator_transposed.rename(columns={col: new_col_name}, inplace=True)

for j in range(Aggregator.shape[0]):
    exec(f'FliprankA{j + 1} = []')
    for i in range(10):
        index = np.where(Aggregator_transposed.iloc[:, j].str.startswith('Szenario ' + str((chr(ord('A') + i)))))[0][
                    0] + 1
        exec(f'FliprankA{j + 1}.append(11-index)')
        # Der leeren Liste Fliprank wird entsprechend der gefundenen Zeile ein Wert zugeteilt

for j in range(Aggregator.shape[0]):
    ScenarioMatrix_Aggregator[f'FliprankA{j + 1}'] = globals()[f'FliprankA{j + 1}']
    # Dem df ScenarioMatrix_privat wird an der Stelle Fliprank j+1 die befüllte Liste Fliprankj+1 hinzugefügt

# Utility calculation for Aggregator only
regression_df_Aggregator = pd.DataFrame()
# Erstellen eines neuen leeren pandas Dataframe
for j in range(Aggregator.shape[0]):
    # über alle User hinweg wird die Liste regression df mit den Parametern gefüllt
    y = ScenarioMatrix_Aggregator[f'FliprankA{j + 1}']
    linearRegression = sm.OLS(y, independent_variables).fit()
    #   print(linearRegression.summary())
    regression_df_Aggregator[f'User{j + 1}'] = linearRegression.params[0:9]

Aggregator_List = []
utility_aggregator = pd.DataFrame(
    {'Intercept': [], 'BetaPreis': [], 'BetaCO2': [], 'BetaAutarkie=hoch': [], 'BetaAutarkie=mittel': [],
     'BetaAutarkie=gering': [], 'BetaVorlaufzeit': []})
for rows in range(regression_df_Aggregator.shape[0]):
    avg_row = regression_df_Aggregator.iloc[rows].mean()
    Aggregator_List.append(avg_row)
utility_aggregator.loc[len(utility_aggregator)] = Aggregator_List
utility_aggregator.rename(index={0: "Utility_Aggregator"})

# Merge all utility functions in 1 Dataframe
utilities = pd.concat([utility_aggregator, Utility_Industrie, Utility_Haushalt],
                      keys=['Utility_Aggregator', 'Utility_Industrie', 'Utility_Haushalt'])
#print(Industrie_List)

def utility_function(independent: list, dependent: list) -> list:
    """
    The utility function performs an OLS regression for a given set of independent variables and
    a list of dependent variable as input.
    :param independent: list of independent variables currently stored in `independent_variables`
    :param dependent: Fliprank to regress on. Use `Scenario_Matrix` and 'Fliprank{user}'
    :return: betas for all the measured attributes
    """
    linear_regression = sm.OLS(dependent, independent).fit()
    return linear_regression.params[0:8]
