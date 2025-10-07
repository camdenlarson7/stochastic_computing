import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt



output_dir = 'combinational_analysis_graphs'
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv('all_stochastic_results.csv')


#1 Mean Percent Error vs. Bitstream Length
df['Percent Error (%)'] = pd.to_numeric(df['Percent Error (%)'], errors='coerce')
mean_error = df.groupby('Number of Bits', as_index=False)['Percent Error (%)'].mean()
fig1 = px.line(mean_error, x='Number of Bits', y='Percent Error (%)', log_x=True,
             title='Mean Percent Error vs. Bitstream Length', markers=True)
fig1.write_html(os.path.join(output_dir, 'mean_percent_error_vs_bits.html'))



#2 Mean Absolute Error vs. Bitstream Length
df['Absolute Error'] = pd.to_numeric(df['Absolute Error'], errors='coerce')
mean_abs_error = df.groupby('Number of Bits', as_index=False)['Absolute Error'].mean()
fig2 = px.line(mean_abs_error, x='Number of Bits', y='Absolute Error',
               log_x=True,
               title='Mean Absolute Error vs. Bitstream Length',
               markers=True)

fig2.write_html(os.path.join(output_dir, 'mean_absolute_error_vs_bits.html'))



# 3. Scatter plot: percent error vs. product of a and b (all bit lengths)
df['a*b'] = df['a'] * df['b']
fig3 = px.scatter(df, x='a*b', y='Percent Error (%)', color='Number of Bits',
                  title='Percent Error vs. Product a*b (Colored by Bitstream Length)',
                  color_continuous_scale='Viridis', log_x=False)
fig3.write_html(os.path.join(output_dir, 'percent_error_vs_product.html'))


#4 . Heatmap: mean percent error as a function of a and b (for a fixed bit length, e.g., 1024)
bit_length = 8192
subset = df[df['Number of Bits'] == bit_length]
fig4 = px.density_heatmap(subset, x='a', y='b', z='Percent Error (%)', histfunc='avg', nbinsx=30, nbinsy=30,
                          title=f'Percent Error Heatmap for a vs. b (Bitstream Length = {bit_length})')
fig4.write_html(os.path.join(output_dir, 'percent_error_heatmap_a_b.html'))