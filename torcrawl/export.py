import os
import json
import sqlite3
import xml.etree.ElementTree as ET


def _build_xml_tree(data):
    """ Build XML tree structure from crawl data.

    :param data: Dict - Crawl data dictionary.
    :return: Element - XML root element.
    """
    root = ET.Element("crawl", start_url=data.get("start_url", ""))
    tag_map = {
        "links": "link",
        "external_links": "external_link",
        "images": "image",
        "scripts": "script",
        "telephones": "telephone",
        "emails": "email",
        "files": "file",
    }

    for section, child_tag in tag_map.items():
        section_el = ET.SubElement(root, section)
        for item in data.get(section, []):
            child = ET.SubElement(section_el, child_tag)
            child.text = item
    return root


def export_json(export_path, prefix, data, verbose=False):
    """ Export crawl findings to JSON file.

    :param export_path: String - Path where JSON file will be saved.
    :param prefix: String - Prefix for the JSON filename.
    :param data: Dict - Crawl data to export.
    :param verbose: Boolean - Whether to print verbose output.
    :return: String - Path to the created JSON file.
    """
    json_path = os.path.join(export_path, f"{prefix}.json")
    with open(json_path, "w", encoding="UTF-8") as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)
    if verbose:
        print(f"## JSON results created at: {json_path}")
    return json_path


def export_xml(export_path, prefix, data, verbose=False):
    """ Export crawl findings to XML file.

    :param export_path: String - Path where XML file will be saved.
    :param prefix: String - Prefix for the XML filename.
    :param data: Dict - Crawl data to export.
    :param verbose: Boolean - Whether to print verbose output.
    :return: String - Path to the created XML file.
    """
    xml_path = os.path.join(export_path, f"{prefix}.xml")
    root = _build_xml_tree(data)
    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="UTF-8", xml_declaration=True)
    if verbose:
        print(f"## XML results created at: {xml_path}")
    return xml_path


def export_database(export_path, prefix, data, edges, titles, resources=None, verbose=False):
    """ Export crawl findings and link graph to SQLite database.

    :param export_path: String - Path where database file will be saved.
    :param prefix: String - Prefix for the database filename.
    :param data: Dict - Crawl data dictionary.
    :param edges: Set - Set of tuples (from_url, to_url) representing link relationships.
    :param titles: Dict - Dictionary mapping URLs to page titles.
    :param resources: Dict - Dictionary of resources by category and source URL.
    :param verbose: Boolean - Whether to print verbose output.
    :return: String - Path to the created database file.
    """
    db_path = os.path.join(export_path, f"{prefix}.db")

    nodes = set(data.get("links", []))
    nodes.update([edge[0] for edge in edges])
    nodes.update([edge[1] for edge in edges])

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                url TEXT PRIMARY KEY,
                title TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_url TEXT,
                to_url TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                from_url TEXT,
                value TEXT
            );
        """)

        cur.executemany(
            "INSERT OR REPLACE INTO nodes(url, title) VALUES(?, ?);",
            [(url, titles.get(url)) for url in nodes]
        )

        cur.executemany(
            "INSERT OR IGNORE INTO edges(from_url, to_url) VALUES(?, ?);",
            list(edges)
        )
        
        # Resources
        res_payload = resources if resources is not None else data.get("resources", {})
        res_rows = []
        for category, mapping in res_payload.items():
            for from_url, values in mapping.items():
                for val in values:
                    res_rows.append((category, from_url, val))
        if res_rows:
            cur.executemany(
                "INSERT OR IGNORE INTO resources(category, from_url, value) VALUES(?, ?, ?);",
                res_rows
            )
        conn.commit()
        if verbose:
            print(f"## SQLite results created at: {db_path}")
    finally:
        conn.close()

    return db_path

