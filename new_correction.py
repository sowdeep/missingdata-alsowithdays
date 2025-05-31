import os
import re
import csv
from collections import defaultdict

def analyze_climate_data_final_v3(main_folder_path):
    """
    Analyzes files in subfolders for alphabetical sequences and
    horizontal numerical data present on the *same lines* as alphabetical data.
    Generates a single CSV report with a hierarchical structure.
    Displays subfolders with 0 alphabetical counts at the top.
    Excludes files with 0 alphabetical counts.
    Sorts files within subfolders by filename.
    Includes a 'Following day' column for numerical data associated with alphabetical lines.

    Args:
        main_folder_path (str): The path to the main folder containing climate data.
    """
    subfolder_data = defaultdict(list)  # Stores files and their counts per subfolder
    subfolder_totals = defaultdict(int)  # Stores total counts per subfolder

    for root, dirs, files in os.walk(main_folder_path):
        # Determine the relative path of the current directory from the main folder
        relative_path = os.path.relpath(root, main_folder_path)

        # Skip the main folder itself if it's the root of the walk
        if relative_path == '.':
            continue

        # Get the immediate subfolder name
        current_subfolder_name = os.path.basename(root)

        # Ensure every visited subfolder is initialized in subfolder_totals,
        # even if it ends up having 0 alphabets.
        if current_subfolder_name not in subfolder_totals:
             subfolder_totals[current_subfolder_name] = 0

        for file in files:
            file_path = os.path.join(root, file)
            alphabetical_units_count_file = 0
            numerical_data_from_alpha_lines = [] # Collects numbers from relevant lines

            try:
                # Attempt to read the file line by line, ignoring decoding errors.
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Check if the line contains any alphabetical characters
                        if re.search(r'[a-zA-Z]', line):
                            # If it does, find all numerical sequences on THIS line
                            numerical_sequences_on_line = re.findall(r'\b\d+\.?\d*\b', line)
                            if numerical_sequences_on_line:
                                numerical_data_from_alpha_lines.extend(numerical_sequences_on_line)
                            
                            # Count alphabetical units on THIS line
                            alphabetical_units = re.findall(r'[a-zA-Z]+', line)
                            alphabetical_units_count_file += len(alphabetical_units)

                # Join collected numerical data for the 'Following day' column
                following_day_data = "; ".join(numerical_data_from_alpha_lines) if numerical_data_from_alpha_lines else ""

                # Only add files if their total alphabetical count is not 0
                if alphabetical_units_count_file > 0:
                    subfolder_data[current_subfolder_name].append({
                        'File': file,
                        'Alphabetical Units Count': alphabetical_units_count_file,
                        'Following day': following_day_data
                    })
                    subfolder_totals[current_subfolder_name] += alphabetical_units_count_file

            except Exception as e:
                # print(f"Could not process file (might be binary or corrupted) {file_path}: {e}")
                pass # Silently skip files that cause errors or are unreadable text

    # Prepare the final structured data for CSV
    final_report_data = []

    # Separate subfolders into those with 0 count and those with non-zero counts
    zero_count_subfolders = []
    non_zero_count_subfolders = []

    for subfolder_name, total_alpha_count in subfolder_totals.items():
        if total_alpha_count == 0:
            zero_count_subfolders.append((subfolder_name, total_alpha_count))
        else:
            non_zero_count_subfolders.append((subfolder_name, total_alpha_count))

    # Sort non-zero count subfolders by their total alphabetical count in ascending order
    non_zero_count_subfolders.sort(key=lambda item: item[1])

    # Combine them: zero-count subfolders first, then sorted non-zero count subfolders
    sorted_subfolders = zero_count_subfolders + non_zero_count_subfolders

    for subfolder_name, total_alpha_count in sorted_subfolders:
        # Add the subfolder row
        final_report_data.append({
            'Subfolder Name': subfolder_name,
            'Subfolder Total Alphabetical Count': total_alpha_count,
            'File Name': '',
            'File Alphabetical Count': '',
            'Following day': ''
        })

        # Get and sort files within this subfolder by their filename (alphabetical + numerical)
        files_in_subfolder = subfolder_data.get(subfolder_name, [])
        files_in_subfolder.sort(key=lambda x: x['File']) # Sort by 'File' name

        # Add file rows under the subfolder
        for file_info in files_in_subfolder:
            final_report_data.append({
                'Subfolder Name': '',
                'Subfolder Total Alphabetical Count': '',
                'File Name': file_info['File'],
                'File Alphabetical Count': file_info['Alphabetical Units Count'],
                'Following day': file_info['Following day']
            })

    output_csv_path = os.path.join(main_folder_path, "climate_data_analysis.csv")

    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Subfolder Name',
                'Subfolder Total Alphabetical Count',
                'File Name',
                'File Alphabetical Count',
                'Following day' # New column header
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in final_report_data:
                writer.writerow(row)
        print(f"Successfully created climate_data_analysis.csv at: {output_csv_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

# --- How to use this script ---
if __name__ == "__main__":
    # Ensure this path is correct for your system
    main_folder_location = r"C:\Users\aaa\Desktop\climate data"
    analyze_climate_data_final_v3(main_folder_location)