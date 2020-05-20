import xlrd
import collections
import json
import time
import subprocess
import sys
import os
import traceback

try:
    import pyexcel

    print(f"LOG INFO: {pyexcel.__name__} sucessfully imported")
except:
    print(f"LOG WARN: Need to install pyexcel")
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", 'pyexcel'])
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", 'pyexcel-xlsx'])


def add_to_records(single_record, list_of_details):
    """Append record of a single order to list of records """
    print(f"LOG INFO: Adding single dict object to list ")
    try:
        list_of_details.append(single_record)
        print("\nLOG INFO: Current record added")
        print(json.dumps(single_record, indent=2))
        print("\n")
        print(list_of_details)
    except:
        print("LOG ERROR: record not added")
    return list_of_details


def convert_excel_to_list_of_dict(fname):
    result_list = []

    xl_workbook = xlrd.open_workbook(filename=fname)
    xl_sheet = xl_workbook.sheet_by_index(0)

    # Build a list of headers from row at index 0
    headers_list = []
    for idx_col in range(0, xl_sheet.ncols):
        header = str(xl_sheet.cell(rowx=0, colx=idx_col).value)
        headers_list.append(header)

    for idx_row in range(1, xl_sheet.nrows):
        values_list = []

        # Build a list of values for single record/ row
        for col in range(0, xl_sheet.ncols):
            col_value = str(xl_sheet.cell(rowx=idx_row, colx=col).value)
            values_list.append(col_value)

        # Build a dict object for the current record/row
        current_record = collections.OrderedDict()
        for i, item in enumerate(headers_list):
            current_record[headers_list[i]] = (values_list[i]).strip()

        # Add dict object ot list of dict objects
        add_to_records(current_record, result_list)

    print(f"LOG INFO: Total number of records added {len(result_list)}")
    return result_list


def list_of_json_to_excel(jsonList, subdirectory_name, fullDestfilename):
    print("LOG INFO: Saving results")
    time_run = time.strftime("%Y%b%d_%H%M%S", time.localtime())
    dest_file_name = f"C:/saveToFile/{subdirectory_name}/{fullDestfilename}_{time_run}.xlsx"

    try:
        pyexcel.save_as(records=jsonList, dest_file_name=dest_file_name)
        print(f"LOG INFO: Results saved at: {dest_file_name}")
    except:
        print("LOG ERROR: Save directory not present. Making directory")
        os.makedirs(f'C:/saveToFile/{subdirectory_name}')
        try:
            pyexcel.save_as(records=jsonList, dest_file_name=dest_file_name)
            print(f"LOG INFO: Results saved at: {dest_file_name}")
            print("\n")
        except:
            traceback.print_exc()
            print("LOG ERROR:Final Save failed")
