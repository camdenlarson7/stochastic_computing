import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os

output_dir = 'single_run_graphs'
os.makedirs(output_dir, exist_ok=True)

def make_html_table(headers, rows, table_id):
    table = f'<table id="{table_id}" style="position:fixed; top:30px; right:30px; background:white; border:1px solid #ccc; z-index:10; cursor:move;">'
    table += '<thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
    for row in rows:
        table += '<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>'
    table += '</tbody></table>'
    return table

drag_js = '''<script>
function makeDraggable(el) {
  el.onmousedown = function(e) {
    e.preventDefault();
    let shiftX = e.clientX - el.getBoundingClientRect().left;
    let shiftY = e.clientY - el.getBoundingClientRect().top;
    function moveAt(pageX, pageY) {
      el.style.left = pageX - shiftX + 'px';
      el.style.top = pageY - shiftY + 'px';
    }
    function onMouseMove(e) {
      moveAt(e.pageX, e.pageY);
    }
    document.addEventListener('mousemove', onMouseMove);
    el.onmouseup = function() {
      document.removeEventListener('mousemove', onMouseMove);
      el.onmouseup = null;
    };
  };
  el.ondragstart = function() { return false; };
}
window.onload = function() {
  ['table1','table2','table3'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) makeDraggable(el);
  });
};
</script>'''

def create_graphs_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    bit_sizes = df['Number of Bits']
    diffs = df['Percent Error (%)']
    abs_diffs = df['Absolute Error']
    expected_results = df['Expected Result']
    stochastic_results = df['Stochastic Result']

    # Percent Error Plot
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=bit_sizes, y=diffs, mode='lines+markers', name='Percent Error (%)'))
    fig1.update_xaxes(type='log', title='Number of Bits (log scale)')
    fig1.update_yaxes(title='Percent Error (%)')
    fig1.update_layout(title='Stochastic Multiplication Percent Error vs. Bitstream Length', template='plotly_white')
    pio.write_html(fig1, file=os.path.join(output_dir, 'percent_error_vs_bits_draggable.html'), auto_open=False)

    # Absolute Error Plot
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=bit_sizes, y=abs_diffs, mode='lines+markers', name='Absolute Error'))
    fig2.update_xaxes(type='log', title='Number of Bits (log scale)')
    fig2.update_yaxes(title='Absolute Error |Stochastic - Expected|')
    fig2.update_layout(title='Stochastic Multiplication Absolute Error vs. Bitstream Length', template='plotly_white')
    pio.write_html(fig2, file=os.path.join(output_dir, 'absolute_error_vs_bits_draggable.html'), auto_open=False)

    # Expected vs Stochastic Result Plot
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=bit_sizes, y=expected_results, mode='lines+markers', name='Expected Result', line=dict(color='green')))
    fig3.add_trace(go.Scatter(x=bit_sizes, y=stochastic_results, mode='lines+markers', name='Stochastic Result', line=dict(color='blue')))
    fig3.update_xaxes(type='log', title='Number of Bits (log scale)')
    fig3.update_yaxes(title='Result Value')
    fig3.update_layout(title='Expected vs Stochastic Result', template='plotly_white')
    pio.write_html(fig3, file=os.path.join(output_dir, 'expected_vs_stochastic_draggable.html'), auto_open=False)

    # Prepare data for tables
    percent_rows = list(zip(bit_sizes, diffs))
    abs_rows = list(zip(bit_sizes, abs_diffs))
    exp_stoch_rows = list(zip(bit_sizes, expected_results, stochastic_results))

if __name__ == "__main__":
    create_graphs_from_csv('stochastic_multiplication_results.csv')
