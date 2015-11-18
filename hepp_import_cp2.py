import sys

from import_cp2 import import_cp2_csv_results, output_cp2_results

data = import_cp2_csv_results(sys.argv[1], sys.argv[2], sys.argv[3], [sys.argv[4]])

output_cp2_results(data, sys.argv[5], sys.argv[6])
