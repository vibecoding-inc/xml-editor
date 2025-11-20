# xmleditor/cli.py
import argparse
import sys
from .xml_utils import XMLUtilities

def main():
    parser = argparse.ArgumentParser(description="XML Editor CLI")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate an XML file")
    validate_parser.add_argument("file", help="Path to the XML file")
    validate_parser.add_argument("--schema", help="Path to the XSD schema file")

    args = parser.parse_args()

    if args.command == "validate":
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                xml_content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {args.file}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)

        schema_content = None
        if args.schema:
            try:
                with open(args.schema, "r", encoding="utf-8") as f:
                    schema_content = f.read()
            except FileNotFoundError:
                print(f"Error: Schema file not found at {args.schema}", file=sys.stderr)
                sys.exit(1)
            except IOError as e:
                print(f"Error reading schema file {args.schema}: {e}", file=sys.stderr)
                sys.exit(1)

        if schema_content:
            is_valid, message = XMLUtilities.validate_xml_with_xsd(xml_content, schema_content)
        else:
            is_valid, message = XMLUtilities.validate_xml(xml_content)

        if is_valid:
            print("XML is valid.")
            sys.exit(0)
        else:
            print(f"XML is invalid:\n{message}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
