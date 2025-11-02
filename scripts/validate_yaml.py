import os
import glob
import yaml
import logging
from jsonschema import validate, ValidationError

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


def get_filename_only(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def validate_with_schema(file_path, schema):
    try:
        validate(load_yaml(file_path), schema)
        return True
    except ValidationError as ve:
        logging.error(f"Validation error in {get_filename_only(file_path)}")
        logging.error(ve.message)
        return False


def validate_files(files, schema, label):
    logging.info(f"Validating {len(files)} {label}")
    failed_files = []
    for f in files:
        if not validate_with_schema(f, schema):
            failed_files.append(get_filename_only(f))
    if failed_files:
        logging.error(f"Failed {label}: {failed_files}")
        return False
    logging.info(f"All {label} are valid.")
    return True


def main():
    root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    brand_schema = load_yaml(os.path.join(root_path, "schemas/brand_schema.yaml"))
    brand_files = glob.glob(os.path.join(root_path, "data/brands", "*.yaml"))
    brands_ok = validate_files(brand_files, brand_schema, "brands")

    company_schema = load_yaml(os.path.join(root_path, "schemas/company_schema.yaml"))
    company_files = glob.glob(os.path.join(root_path, "data/companies", "*.yaml"))
    companies_ok = validate_files(company_files, company_schema, "companies")

    if not (brands_ok and companies_ok):
        exit(1)


if __name__ == "__main__":
    main()
