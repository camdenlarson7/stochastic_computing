import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


output_dir = 'combinational_analysis_graphs'
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv('all_stochastic_results.csv')


# 1. Mean percent error vs. bit length (across all runs)
mean_error = df.groupby('Number of Bits')['Percent Error (%)'].mean().reset_index()
fig1 = px.line(mean_error, x='Number of Bits', y='Percent Error (%)', log_x=True, title='Mean Percent Error vs. Bitstream Length')
fig1.write_html(os.path.join(output_dir, 'mean_percent_error_vs_bits.html'))

#2. Mean absolute error vs. bit length (across all runs)
mean_abs_error = df.groupby('Number of Bits')['Absolute Error'].mean().reset_index()
fig2 = px.line(mean_abs_error, x='Number of Bits', y='Absolute Error', log_x=True, title='Mean Absolute Error vs. Bitstream Length')
fig2.write_html(os.path.join(output_dir, 'mean_absolute_error_vs_bits.html'))