import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path

# Maximum pages per import file
MAX_PAGES_PER_FILE = 50


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_mediawiki_import(pages, output_file):
    """Create a MediaWiki XML import file with the given pages."""
    # Create root mediawiki element
    mediawiki = ET.Element('mediawiki')
    mediawiki.set('xmlns', 'http://www.mediawiki.org/xml/export-0.11/')
    mediawiki.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    mediawiki.set('xsi:schemaLocation', 'http://www.mediawiki.org/xml/export-0.11/ http://www.mediawiki.org/xml/export-0.11.xsd')
    mediawiki.set('version', '0.11')
    mediawiki.set('xml:lang', 'en')

    # Add siteinfo
    siteinfo = ET.SubElement(mediawiki, 'siteinfo')
    sitename = ET.SubElement(siteinfo, 'sitename')
    sitename.text = 'Wiki'

    # Add each page
    for page_title, page_content in pages:
        page = ET.SubElement(mediawiki, 'page')

        title = ET.SubElement(page, 'title')
        title.text = page_title

        ns = ET.SubElement(page, 'ns')
        ns.text = '0'

        revision = ET.SubElement(page, 'revision')

        timestamp = ET.SubElement(revision, 'timestamp')
        timestamp.text = '2024-01-01T00:00:00Z'

        contributor = ET.SubElement(revision, 'contributor')
        username = ET.SubElement(contributor, 'username')
        username.text = 'WikiBot'

        comment = ET.SubElement(revision, 'comment')
        comment.text = 'Automated import'

        model = ET.SubElement(revision, 'model')
        model.text = 'wikitext'

        format_elem = ET.SubElement(revision, 'format')
        format_elem.text = 'text/x-wiki'

        text = ET.SubElement(revision, 'text')
        text.set('xml:space', 'preserve')
        text.set('bytes', str(len(page_content.encode('utf-8'))))
        text.text = page_content

    # Write to file
    xml_str = prettify_xml(mediawiki)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)


def load_wiki_file(filepath):
    """Load a wiki file and return its content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def get_page_title_from_filename(filename):
    """Extract page title from filename (remove .wiki extension)."""
    return os.path.splitext(filename)[0]


def process_directory(input_dir):
    """Process all .wiki files in a directory and create import files."""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Directory not found: {input_dir}")
        return

    # Get all .wiki files
    wiki_files = sorted(input_path.glob('*.wiki'))

    if not wiki_files:
        print(f"No .wiki files found in {input_dir}")
        return

    print(f"Found {len(wiki_files)} wiki files in {input_dir}")

    # Create import subdirectory
    import_dir = input_path / 'import'
    import_dir.mkdir(exist_ok=True)

    # Load all pages
    pages = []
    for wiki_file in wiki_files:
        page_title = get_page_title_from_filename(wiki_file.name)
        page_content = load_wiki_file(wiki_file)
        pages.append((page_title, page_content))

    # Split into batches and create import files
    num_batches = (len(pages) + MAX_PAGES_PER_FILE - 1) // MAX_PAGES_PER_FILE

    for batch_num in range(num_batches):
        start_idx = batch_num * MAX_PAGES_PER_FILE
        end_idx = min(start_idx + MAX_PAGES_PER_FILE, len(pages))
        batch_pages = pages[start_idx:end_idx]

        # Create output filename
        output_file = import_dir / f'import_batch_{batch_num + 1:02d}.xml'

        print(f"  Creating {output_file.name} with {len(batch_pages)} pages...")
        create_mediawiki_import(batch_pages, output_file)

    print(f"Created {num_batches} import file(s) in {import_dir}")


def main():
    """Main function to process all output directories."""
    print("MediaWiki Import File Generator")
    print("=" * 50)

    output_base = Path("output")

    if not output_base.exists():
        print(f"Output directory not found: {output_base}")
        return

    # Find all subdirectories with .wiki files
    processed = False
    for subdir in output_base.iterdir():
        if subdir.is_dir():
            wiki_files = list(subdir.glob('*.wiki'))
            if wiki_files:
                print(f"\nProcessing {subdir.name}...")
                process_directory(subdir)
                processed = True

    if not processed:
        print("No directories with .wiki files found in output/")
    else:
        print("\n" + "=" * 50)
        print("Done!")


if __name__ == "__main__":
    main()
