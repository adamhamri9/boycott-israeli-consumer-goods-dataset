import yaml
import csv
import json
import os
import toml
import pandas as pd


def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def clean_value(value):
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return value


def export_to_csv(input_dir, output_csv, schema_file):
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    schema = read_yaml(schema_file)
    with open(output_csv, "w", newline="") as csvfile:
        schema_fields = list(schema["properties"].keys())
        if "stakeholders" in schema_fields:
            schema_fields.remove("stakeholders")
        fieldnames = ["id"] + schema_fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for yaml_file in sorted(os.listdir(input_dir)):
            if yaml_file.endswith(".yaml"):
                yaml_file_path = os.path.join(input_dir, yaml_file)
                data = read_yaml(yaml_file_path)
                cleaned_data = {key: clean_value(data.get(key, None)) for key in fieldnames}
                cleaned_data["id"] = os.path.splitext(yaml_file)[0]
                writer.writerow(cleaned_data)
                print(f"[CSV] Converted {yaml_file} → {output_csv}")


def convert_yaml_to_dict(directory_path, key):
    data = {}
    for file_name in sorted(os.listdir(directory_path)):
        if file_name.endswith(".yaml"):
            file_path = os.path.join(directory_path, file_name)
            yaml_data = read_yaml(file_path)
            data[os.path.splitext(file_name)[0]] = {
                "id": os.path.splitext(file_name)[0],
                **yaml_data,
            }
    return {key: data}


def export_to_json(directory1, directory2, output_json):
    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    brands_data = convert_yaml_to_dict(directory1, "brands")
    companies_data = convert_yaml_to_dict(directory2, "companies")
    combined_data = {**brands_data, **companies_data}

    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(combined_data, json_file, indent=2)
        print(f"[JSON] Combined data written to {output_json}")
    
    return combined_data


def export_to_toml(combined_data, output_toml):
    os.makedirs(os.path.dirname(output_toml), exist_ok=True)

    toml_data = {**combined_data.get("brands", {}), **combined_data.get("companies", {})}
    with open(output_toml, "w", encoding="utf-8") as f:
        toml.dump(toml_data, f)
        print(f"[TOML] Data written to {output_toml}")


def export_to_excel(combined_data, output_excel):
    os.makedirs(os.path.dirname(output_excel), exist_ok=True)

    with pd.ExcelWriter(output_excel) as writer:
        brands_df = pd.DataFrame.from_dict(combined_data.get("brands", {}), orient="index")
        brands_df.to_excel(writer, sheet_name="Brands", index=False)

        companies_df = pd.DataFrame.from_dict(combined_data.get("companies", {}), orient="index")
        companies_df.to_excel(writer, sheet_name="Companies", index=False)
    
    print(f"[Excel] Data written to {output_excel}")


def export_to_parquet(combined_data, output_parquet):
    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)

    # دمج Brands و Companies في ملف واحد مع إضافة عمود type
    all_data = []
    for category, items in combined_data.items():
        for item_id, item_data in items.items():
            all_data.append({"type": category, **item_data})

    df = pd.DataFrame(all_data)
    df.to_parquet(output_parquet, engine="pyarrow", index=False)
    print(f"[Parquet] Data written to {output_parquet}")


if __name__ == "__main__":
    brands_yaml = "data/brands"
    companies_yaml = "data/companies"

    brands_csv_file = "output/csv/brands.csv"
    companies_csv_file = "output/csv/companies.csv"

    data_json_file = "output/json/data.json"
    data_toml_file = "output/toml/data.toml"
    data_excel_file = "output/excel/data.xlsx"
    data_parquet_file = "output/parquet/data.parquet"

    brand_schema = "schemas/brand_schema.yaml"
    company_schema = "schemas/company_schema.yaml"

    export_to_csv(brands_yaml, brands_csv_file, brand_schema)
    export_to_csv(companies_yaml, companies_csv_file, company_schema)

    combined_data = export_to_json(brands_yaml, companies_yaml, data_json_file)
    export_to_toml(combined_data, data_toml_file)
    export_to_excel(combined_data, data_excel_file)
    export_to_parquet(combined_data, data_parquet_file)
