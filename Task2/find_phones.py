"""This module find hones:
find in the text the numbers that correspond to the providers
that were specified as command line arguments
and create an output CSV file phones.csv"""

import csv
import re
import argparse


parser = argparse.ArgumentParser(description="Find phones")

parser.add_argument('-i', '--input_file', required=True,
                    help='path to input.txt')
parser.add_argument('-c', '--cell_codes', required=True,
                    help='path to ua_cell_codes.csv')
parser.add_argument('-p', '--provider', action='append', required=True,
                    help='phone provider name')
parser.add_argument('-o', '--output_file', required=True,
                    help='path to output file: phones.csv')
args = parser.parse_args()


def format_phone(number):
    """This function formats phone number according to the following mask: +38(0XX)XXX-XX-XX"""
    formatted_phone = []

    for num in number:
        formatted_phone.append(num)

    formatted_phone.insert(0, "+380(")
    formatted_phone.insert(3, ")")
    formatted_phone.insert(7, "-")
    formatted_phone.insert(10, "-")
    formatted_phone = "".join(formatted_phone)
    return formatted_phone


provider_pattern = []

with open(args.cell_codes, newline="", encoding="utf-8") as csv_input:
    reader = csv.DictReader(csv_input)
    for row in reader:
        if row["provider"] in args.provider:
            row["number_pattern"] = re.sub(r"\W", "", row["number_pattern"])
            row["number_pattern"] = re.sub(r"x", "[0-9]", row["number_pattern"])
            provider_pattern.append({"number_pattern": row["number_pattern"],
                                     "provider": row["provider"]})


phone_number = []

with open(args.input_file, "r", encoding="utf-8") as txt_file:
    for row in txt_file:
        for matches in re.findall(r"[0-9|\+|(][0-9()\-\+ ]{7,20}[0-9]", row):
            phone = re.sub(r"(^\+*3*8*\s*\(*0*\s*0*)|(\W)", "", format(matches))
            for element in provider_pattern:
                reObj = re.compile(element["number_pattern"])
                if reObj.match(phone):
                    phone_number.append({"phone": phone, "provider":element["provider"]})


with open(args.output_file, "w", newline="", encoding="utf-8") as output_csv:
    column_names = ["phone", "provider"]
    writer = csv.DictWriter(output_csv, delimiter=" ", fieldnames=column_names)
    writer.writeheader()
    for row in phone_number:
        phone = format_phone(row["phone"])
        writer.writerow({"phone": phone, "provider":row["provider"]})
