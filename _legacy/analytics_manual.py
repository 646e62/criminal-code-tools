# Step-by-step construction of an analytical report for the sentencing data we have

from pathlib import Path
import pandas as pd

from utils import parse_quantum, convert_quantum_to_days

# Create a new dataframe that contains the data from all the CSV files in the sentencing-data folder
sentencing_data = pd.concat([
    pd.read_csv(f) for f in Path("data/sentencing-data").glob("*.csv")
], ignore_index=True)

# Check the offence column to see which offences are most common
offence_counts = sentencing_data["offence"].value_counts()

def parse_jail_string(jail_str, uid=None):
    jail_str = jail_str.strip()
    if "&" in jail_str:
        parts = jail_str.split("&")
        return sum(parse_jail_string(part, uid=uid) for part in parts)

    try:
        # Set indeterminate sentences to -1 until we have a better way to handle them
        if "indeterminate" in jail_str:
            return -1
        elif "d" in jail_str:
            return int(jail_str.replace("d", "").strip())
        elif "y" in jail_str:
            # Set life sentences to -1 until we have a better way to handle them
            if "255y" in jail_str:
                return -1
            return int(jail_str.replace("y", "").strip()) * 365
        elif "m" in jail_str:
            return int(jail_str.replace("m", "").strip()) * 30
        # Check to see if the sentence quantum is "indeterminate"

        else:
            # If there's no recognized format, we decide how to handle it
            return 0
    except ValueError as e:
        msg = f"Error parsing jail string {jail_str!r} for uid={uid}. " \
              f"Original error: {str(e)}"
        raise ValueError(msg) from e

def calculate_sentence(row):
    jail = row["jail"]
    uid = row["uid"]  # or whatever the name of the UID column is
    if isinstance(jail, str):
        return parse_jail_string(jail, uid=uid)
    else:
        return 0

# Apply the calculate_sentence function to the jail column and create a new column called sentence in days
sentencing_data["parsed_jail_sentence"] = sentencing_data.apply(calculate_sentence, axis=1)

# Print the resulting dataframe if the parsed_jail_sentence column contains a value greater than 0
#print(sentencing_data[sentencing_data["parsed_jail_sentence"] > 0])

# Sort the jail sentences in descending order
sorted_sentencing_data = sentencing_data.sort_values("parsed_jail_sentence", ascending=False)

# Print the sorted dataframe
#print(sorted_sentencing_data)

# Print sentences for offences containing 271
print(sorted_sentencing_data[sorted_sentencing_data["offence"].str.contains("271")])