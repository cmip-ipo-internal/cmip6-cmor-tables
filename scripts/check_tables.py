import json
from jsonschema import validate
from collections import defaultdict, Counter
import glob
import argparse

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Mip-Table Validation")
# parser.add_argument("--validate-schema", action="store_true", help="Validate tables against schema")
parser.add_argument("--check-dimensions", action="store_true", help="Check dimensions")
parser.add_argument("--check-units", action="store_true", help="Check units")
parser.add_argument("--report-statistics", action="store_true", help="Print the number of variables per table")
parser.add_argument("--multitable", action="store_true", help="Check if a variable exists in multiple tables. ")

parser.add_argument("--duplicates", action="store_true", help="Check conformity of individual variable entries")

args = parser.parse_args()


# Schema for validation
schema = {
  "type": "object",
  "required": ["Header", "variable_entry"],
  "properties": {
    "Header": {
      "type": "object",
      "required": ["table_id", "product", "table_date", "missing_value", 
                    "generic_levels", "mip_era", 
                   "Conventions"],
      "properties": {
        "table_id": {"type": "string"},
        "product": {"type": "string"},
        "table_date": {"type": "string"}, 
        "missing_value": {"type": "string"},
        "int_missing_value": {"type": "string"},
        "mip_era": {"type": "string"},
        "Conventions": {"type": "string"}  
      }
    },
    "variable_entry": {"type": "object"}
  }
}
# "int_missing_value", - required




variable_schema = {
        "type": "object",
        "required": ["frequency", "modeling_realm", "standard_name", "units", "cell_methods", "cell_measures", "long_name", "dimensions", "out_name", "type", "positive", "valid_min", "valid_max", "ok_min_mean_abs", "ok_max_mean_abs"],
        "properties": {
            "frequency": {"type": "string"},
            "modeling_realm": {"type": "string"},
            "standard_name": {"type": "string"},
            "units": {"type": "string"},
            "cell_methods": {"type": "string"},
            "cell_measures": {"type": "string"},
            "long_name": {"type": "string"},
            "dimensions": {"type": "string"},
            "out_name": {"type": "string"},
            "type": {"type": "string"},
            "positive": {"type": "string"},
            "valid_min": {"type": "string"},
            "valid_max": {"type": "string"},
            "ok_min_mean_abs": {"type": "string"},
            "ok_max_mean_abs": {"type": "string"}
        }
    }

# Load and validate CMIP6 tables against schema
tables = {}
for filename in glob.glob('../Tables/*.json'):
  with open(filename) as f:
    table = json.load(f)
    validate(table, schema)
    tables[table['Header']['table_id']] = table

print(f"Loaded and validated {len(tables)} tables")

# Check units and dimensions
variables = defaultdict(lambda: {"units": set(), "dimensions": set(), "origin": set()})

for table_id, table in tables.items():
  for var_name, attrs in table['variable_entry'].items():
    
    # Validate the variable entry against the schema
    validate(attrs, variable_schema)

    variables[var_name]["units"].add(attrs.get("units"))
    variables[var_name]["dimensions"].add(tuple(attrs.get("dimensions").split()))
    variables[var_name]["origin"].add(table_id)


if args.check_units:
    
    for var, attrs in variables.items():
        if len(attrs["units"]) > 1:
            print(f"Inconsistent units for {var}: {attrs['units']}")

if args.check_dimensions:
    for var, attrs in variables.items():
        if len(attrs["dimensions"]) > 1:  
            print(f"Inconsistent dimensions for {var}: {attrs['dimensions']}")


if args.multitable:
    for var, tables in variables.items():
    #    print(var)
        if len(tables['origin']) >1 :
            print(var,len(tables['origin']), tables['origin'])






if args.report_statistics:
    # Report statistics
    print(f"Variables per table:")
    for table_id, table in tables.items():
        num_vars = len(table['variable_entry'])
        print(f"{table_id}: {num_vars}")

    print(f"Total variables: {len(variables)}")
