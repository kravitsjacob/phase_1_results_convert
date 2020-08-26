
# Import Modules
import os
import pandas as pd
import numpy as np

# Global Vars
pathto_data = '/app_io'
pathto_parambounds = os.path.join(pathto_data, 'phase_1_optimization', 'input', 'param_bounds.csv')
pathto_input = os.path.join(pathto_data, 'phase_1_optimization', 'output')
pathto_output = os.path.join(pathto_data, 'phase_1_results_convert', 'output')
parameter_names = ['N_length', 'N_width', 'n_estimators', 'min_samples_split', 'min_samples_leaf', 'min_weight_fraction_leaf', 'max_depth', 'max_features', 'max_leaf_nodes']
objective_names = ['accuracy', 'FPR', 'TPR', 'AUROCC']


def discretizer(cont_var, disc_min, disc_max, step_size):
    """
    Round the continuous parameters from Borg (defined [0, 1]) to the rounded parameters of the simulation
    :param cont_var: float
                       Continuous variables
    :param disc_min: numeric
                       Minimum of the discretized parameter
    :param disc_max: numeric
                       Maximum of the discretized parameter
    :param step_size: numeric
                       Interval between discretizations
    :return: numeric
                       Discretized values
       """
    # Range Difference
    diff = disc_max - disc_min
    # Proportion of Continious Variable in Range
    dis = diff * cont_var
    # Round to Multiple of Step Size
    if step_size.is_integer():
        # Round to Multiple of Step Size
        disc_var = int(disc_min + step_size * round(dis / step_size))
    else:
        # Round to Multiple of Step Size
        disc_var = disc_min + step_size * round(dis / step_size)
    # Export
    return disc_var


def parameter_converter(params):
    """
    Wrapper function to Round all the continuous parameters from Borg (defined [0, 1]) to the rounded parameters
    of the simulation
    :param params: tuple
                    All the current Borg parameters
    :return: series
                    All the corresponding discretized simulation parameters
    """
    # Convert to Dictionary
    param_dict = dict(zip(parameter_names, params))
    # Import Parameter Bounds
    pb = pd.read_csv(pathto_parambounds, index_col=0)
    # Parameter To Be Converted
    convert_params = list(pb.index[pb['stepsize'].notnull()])
    # Convert Parameters
    for i in convert_params:
        param_dict[i] = discretizer(param_dict[i], *tuple(pb.loc[i][['min', 'max', 'stepsize']]))
    # Export
    return pd.Series(param_dict, dtype=str)


def processor(df, outname, neg_convert):
    """
    Convert a dataframe of continuous Borg parameters to discretized parameters
    :param df: DataFrame
                Continuous Borg parameters
    :param outname: str
                Name of converted file
    :param neg_convert: bool
                Convert negative objectives, helpful when objectives were maximized during the optimization
    :return: int
                Exit status
    """
    # Split Results
    df_objs = df[objective_names]
    df_params = df[parameter_names]
    # Convert Objectives
    if neg_convert == True:
        df_objs = df_objs[df_objs.columns[df_objs.dtypes != np.object]].abs()
    # Convert Parameters
    df_params = df_params.apply(parameter_converter, axis=1)
    # Merge
    df = pd.concat([df_params, df_objs], axis=1)
    # Export
    df.to_csv(os.path.join(pathto_output, outname), sep=',', header=True, index=False)
    return 0


def main():
    # Import Data
    df = pd.read_table(os.path.join(pathto_input, 'results_raw.txt'), sep=' ', names=parameter_names + objective_names)
    # Convert Data
    processor(df, 'results.csv', neg_convert=True)
    return 0


if __name__ == '__main__':
    main()
