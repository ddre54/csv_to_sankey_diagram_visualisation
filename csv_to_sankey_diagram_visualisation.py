# Idea:
# - Create a Sankey diagram in Python from CSV file defining a flow from left to right.
# Approach:
# - Convert multi column CSV file into two columns CSV file (source, target)
# - - The left most column is always the source to the right column
# - - Tools allow to skip columns when loading the CSV file, thus implementing
# - - a sliding windoow approach should be doable to efficiently do this step
# - Use the two columns (source, target) CSV file to generate the Sankey diagram
# -- as seen here:  https://python-graph-gallery.com/basic-sankey-diagram-with-pysankey/
# Resources:
# - https://medium.com/@sssspppp/sankey-diagram-in-python-10c377f1099f
# - https://medium.com/kenlok/how-to-create-sankey-diagrams-from-dataframes-in-python-e221c1b4d6b0
# - https://www.fabi.ai/blog/how-to-create-a-sankey-diagram-in-30-seconds-with-python
# - https://python-graph-gallery.com/basic-sankey-diagram-with-pysankey/

import pandas as pd
import plotly.graph_objects as go
import csv
import argparse


def convert_to_pairs(input_file, output_file, options):
  print("convert_to_paris: {}, {}, {}".format(input_file, output_file, options))
  with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    headers = ''
    for _ in range(options.skip_rows + 1):
      headers = next(reader)  # Read the header row

    # headers = next(reader)  # Read the header row
    print("headers: {}".format(headers))

    sankey_csv_headers = ["source", "target", "value"]
    writer.writerow(sankey_csv_headers)
    for row in reader:
      counter = 0
      for i in range(1, len(headers)):
        if counter == 0:
          print("Window: headers[i-1]: {}, headers[i]: {}".format(headers[i-1], headers[i]))
        # writer.writerow([header[0], header[i], row[0], row[i]])
        print("i-1: {}, i: {}".format(i-1, i))
        print("row[i-1]: {}, row[i]: {}".format(row[i-1], row[i]))
        row1 = row[i-1]
        row2 = row[i]
        if options.header_key:
          row1 = "{}-{}".format(headers[i-1], row[i-1])
          row2 = "{}-{}".format(headers[i], row[i])
        writer.writerow([row1, row2, 1])
        counter += 1


def generate_sankey_diagram(input_file, args):
  # TODO:
  # - Improve CSV file parsing.
  # - Currently it has issues with supporting files that are not strictly clean up and without spaces between columns
  # df = pd.read_csv(file_path, sep=',\s*', skipinitialspace=True, quoting=csv.QUOTE_ALL, engine='python')
  # df = pd.read_csv(file_path, sep=',\s*', skipinitialspace=True, quotechar='"', engine='python')
  # df = pd.read_csv(file_path, sep=',\s*', quotechar='"')
  df = pd.read_csv(input_file, encoding='iso-8859-1', engine='python', sep=',', quotechar='"', quoting=0, doublequote=True)

  print("data frame columns: {}".format(df.columns))

  # Check if the necessary columns exists
  required_columns = {"source", "target", "value"}
  if not required_columns.issubset(df.columns):
    raise ValueError(f"The file must contain the following columns: {required_columns}")

  # Prepare data for Sankey diagram
  # Create a list of unique labesl from 'column1' and 'column2'
  labels = list(pd.concat([df['source'], df['target']]).unique())

  # Map labels to indices
  label_to_index = {label: idx for idx, label in enumerate(labels)}

  # Create source and target lists based on the DataFrame
  sources = df["source"].map(label_to_index).tolist()
  targets = df["target"].map(label_to_index).tolist()
  values = df["value"].tolist()

  # Create Sankey diagram
  fig = go.Figure(go.Sankey(
    node=dict(
      pad=15, # Space between nodes
      thickness=20, # Node thickness
      line=dict(color="black", width=0.5),
      label=labels # Node labels
    ),
    link=dict(
      source=sources, # Source indices
      target=targets, # Target indices
      value=values # Values (amounts)
    )
  ))

  # fig.update_layout(title_text="Sankey Diagram", font_size=10)
  fig.update_layout(title_text=args.input_file, font_size=10)
  fig.show()


def main(input_file, output_file, args):
  print("Input file: {}, Output file: {}".format(input_file, output_file))
  convert_to_pairs(input_file, output_file, args)
  generate_sankey_diagram(output_file, args)


if __name__=="__main__":
  parser = argparse.ArgumentParser(description="Convert multi-column CSV file describing flows into Sankey diagram.")
  # Positional argument
  parser.add_argument("input_file", help="Input CSV file with the multi-column flow data.")

  # Optional argument with default value
  parser.add_argument('-o', "--output-file", help="Output CSV file containing intermediate Sankey diagram flow data format. (default: output.csv)", default='output.csv')
  parser.add_argument('-sr', "--skip-rows", help="How many rows to skip. (default: 0)", default=0, type=int)
  # parser.add_argument('-v', "--verbose", help="Enable verbose output.", default=False)
  parser.add_argument('-hk', "--header-key", help="Flag to include the column's header name as part of the node's key. E.g. <header-value>. Without this flag, the node's key is only <value>. If multiple columns have the save value this could help reduce loops.", action="store_true")

  args = parser.parse_args()
  main(args.input_file, args.output_file, args)

