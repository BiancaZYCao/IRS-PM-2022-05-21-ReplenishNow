# %%
import time
import numpy as np
import pandas as pd
import argparse
from pycaret.datasets import get_data
from pycaret.time_series import *

parser = argparse.ArgumentParser(description="Train a model")
parser.add_argument("-i", "--index", type=int, help="Path to the output file")
args = parser.parse_args()

# %%
y = pd.read_csv('sales_order.csv')
itemID = y.itemID.unique()[args.index]
y = y[y.itemID==itemID]
y.date = pd.to_datetime(y.date)
y = y.set_index('date')

# Sum the sales data for each day
y = y.groupby('date')['quantity'].agg('sum')

# Resample the data by week and sum the sales data for each week
y = y.resample('D').sum()

# %%
# We want to forecast the next 12 months of data and we will use 3 fold cross-validation to test the models.
fh = 12 # or alternately fh = np.arange(1,13)
fold = 3

# init setup
exp = TSForecastingExperiment()
exp.setup(data=y, target='quantity', fh=fh, fold=fold,session_id = 123)

# %%
# compare baseline models
best_baseline_models = exp.compare_models(n_select = 3, turbo=False)
best_baseline_models

# %%
# We will save the metrics to be used in a later step.
compare_metrics = exp.pull()
# compare_metrics

# %%
best_tuned_models = [exp.tune_model(model) for model in best_baseline_models]
best_tuned_models

# %%
# Get model weights to use
top_model_metrics = compare_metrics.iloc[0:3]['MASE']
top_model_metrics
top_model_weights = 1 - top_model_metrics/top_model_metrics.sum()
top_model_weights
# %%
# blend top 3 models
blender = exp.blend_models(best_tuned_models, choose_better = True, weights=top_model_weights.values.tolist())

# %%
y_predict = exp.predict_model(blender)
print(y_predict)


# %%
final_model = exp.finalize_model(blender)
print(exp.predict_model(final_model))

# %%
_ = exp.save_model(final_model, str(itemID))