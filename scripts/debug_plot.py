import pandas as pd
from benchmarks.scripts.figure_styles import FRAMEWORK_ORDER

pdf = pd.read_csv('benchmarks/metrics/structural_metrics.csv')
pdf_fixed = pdf[pdf['n_qubits'] == pdf.groupby('algorithm')['n_qubits'].transform('min')]

x_values = pdf_fixed['algorithm'].unique()
print('n_x', len(x_values))

for fw in FRAMEWORK_ORDER:
    subset = pdf_fixed[pdf_fixed['framework'] == fw].set_index('algorithm')
    heights = [subset['total_gates'].get(x, 0) for x in x_values]
    bad = [h for h in heights if hasattr(h, '__len__') and not isinstance(h, (str, bytes))]
    print(fw, 'len', len(heights), 'bad', len(bad), 'sample_bad', bad[:5])
    print('heights type', type(heights[0]), 'example', heights[:5])
