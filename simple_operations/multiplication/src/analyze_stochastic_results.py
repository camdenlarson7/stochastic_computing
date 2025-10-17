import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure output directory exists
output_dir = '../graphs'
os.makedirs(output_dir, exist_ok=True)

# Load the cumulative results
df = pd.read_csv('../data/all_sobol_results.csv')

# 1. Mean percent error vs. bit length (across all runs)
mean_error = df.groupby('Number of Bits')['Percent Error (%)'].mean().reset_index()
fig1 = px.line(mean_error, x='Number of Bits', y='Percent Error (%)', log_x=True, title='Mean Percent Error vs. Bitstream Length')
fig1.write_html(os.path.join(output_dir, 'mean_percent_error_vs_bits.html'))

# 2. Boxplot of percent error vs. bit length (shows outliers)
fig2 = px.box(df, x='Number of Bits', y='Percent Error (%)', points='all', log_x=True, title='Percent Error Distribution vs. Bitstream Length')
fig2.write_html(os.path.join(output_dir, 'percent_error_boxplot_vs_bits.html'))

# 3. Heatmap: mean percent error as a function of a and b (for a fixed bit length, e.g., 1024)
bit_length = 1024
subset = df[df['Number of Bits'] == bit_length]
fig3 = px.density_heatmap(subset, x='a', y='b', z='Percent Error (%)', histfunc='avg', nbinsx=30, nbinsy=30,
                          title=f'Percent Error Heatmap for a vs. b (Bitstream Length = {bit_length})')
fig3.write_html(os.path.join(output_dir, 'percent_error_heatmap_a_b.html'))

# 4. Scatter plot: percent error vs. product of a and b (all bit lengths)
df['a*b'] = df['a'] * df['b']
fig4 = px.scatter(df, x='a*b', y='Percent Error (%)', color='Number of Bits',
                  title='Percent Error vs. Product a*b (Colored by Bitstream Length)',
                  color_continuous_scale='Viridis', log_x=False)
fig4.write_html(os.path.join(output_dir, 'percent_error_vs_product.html'))

# 5. Highlight outliers: show runs with highest percent error for each bit length
outliers = df.loc[df.groupby('Number of Bits')['Percent Error (%)'].idxmax()]
fig5 = px.scatter(outliers, x='a*b', y='Percent Error (%)', color='Number of Bits',
                  hover_data=['a', 'b', 'Run ID'],
                  title='Outlier Runs: Highest Percent Error per Bitstream Length')
fig5.write_html(os.path.join(output_dir, 'percent_error_outliers.html'))

# 6. Mean absolute error vs. bit length (across all runs)
if 'Absolute Error' not in df.columns:
    # Try to compute it if columns exist
    if 'True Value' in df.columns and 'Result' in df.columns:
        df['Absolute Error'] = abs(df['True Value'] - df['Result'])
    else:
        print('No Absolute Error column and cannot compute it. Skipping absolute error plot.')
else:
    mean_abs_error = df.groupby('Number of Bits')['Absolute Error'].mean().reset_index()
    fig6 = px.line(mean_abs_error, x='Number of Bits', y='Absolute Error', log_x=True, title='Mean Absolute Error vs. Bitstream Length')
    fig6.write_html(os.path.join(output_dir, 'mean_absolute_error_vs_bits.html'))
    print('mean_absolute_error_vs_bits.html')

print('Graphs generated in graphs/:')
print('mean_percent_error_vs_bits.html')
print('percent_error_boxplot_vs_bits.html')
print('percent_error_heatmap_a_b.html')
print('percent_error_vs_product.html')
print('percent_error_outliers.html')
