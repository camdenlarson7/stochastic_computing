import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt



output_dir = 'combinational_analysis_graphs'
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv('all_stochastic_results.csv')


# Mean Percent Error vs. Bitstream Length
df['Percent Error (%)'] = pd.to_numeric(df['Percent Error (%)'], errors='coerce')
mean_error = df.groupby('Number of Bits', as_index=False)['Percent Error (%)'].mean()
fig1 = px.line(mean_error, x='Number of Bits', y='Percent Error (%)', log_x=True,
             title='Mean Percent Error vs. Bitstream Length', markers=True)
fig1.write_html(os.path.join(output_dir, 'mean_percent_error_vs_bits.html'))



# Mean Absolute Error vs. Bitstream Length
df['Absolute Error'] = pd.to_numeric(df['Absolute Error'], errors='coerce')
mean_abs_error = df.groupby('Number of Bits', as_index=False)['Absolute Error'].mean()
fig2 = px.line(mean_abs_error, x='Number of Bits', y='Absolute Error',
               log_x=True,
               title='Mean Absolute Error vs. Bitstream Length',
               markers=True)

fig2.write_html(os.path.join(output_dir, 'mean_absolute_error_vs_bits.html'))