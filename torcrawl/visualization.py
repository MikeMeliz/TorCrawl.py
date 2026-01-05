import os
import sqlite3

import networkx as nx  # type: ignore
from pyvis.network import Network  # type: ignore

MAX_IN_DEGREE = 50
RESOURCE_COLORS = {
    "images": "#7cb5ec",
    "scripts": "#f7a35c",
    "telephones": "#90ed7d",
    "emails": "#f45b5b",
    "external_links": "#8085e9",
    "files": "#91e8e1",
}


def export_visualization(export_path, prefix, start_url, verbose=False):
    """ Generate an HTML visualization from the SQLite database using NetworkX and PyVis.

    :param export_path: String - Path where the database and output will be saved.
    :param prefix: String - Prefix for the database filename.
    :param start_url: String - Starting URL for the crawl visualization.
    :param verbose: Boolean - Whether to print verbose output.
    :return: String - Path to the generated HTML file, or None if database not found.
    """
    db_path = os.path.join(export_path, f"{prefix}.db")
    if not os.path.exists(db_path):
        print("## Visualization skipped: database not found. Use --database (-DB).")
        return None

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT url, title FROM nodes;")
        nodes = cur.fetchall()
        cur.execute("SELECT from_url, to_url FROM edges;")
        edges = cur.fetchall()
        try:
            cur.execute("SELECT category, from_url, value FROM resources;")
            resources = cur.fetchall()
        except sqlite3.OperationalError:
            resources = []
    finally:
        conn.close()

    graph = nx.DiGraph()
    for url, title in nodes:
        graph.add_node(url, title=title or url, label=title or url)
    for src, dst in edges:
        if src and dst:
            graph.add_edge(src, dst, title=f"{src} -> {dst}")

    # Remove very high in-degree nodes to keep layout readable/performance sane.
    indegrees = dict(graph.in_degree())
    to_remove = [n for n, deg in indegrees.items() if deg > MAX_IN_DEGREE and n != start_url]
    if to_remove:
        graph.remove_nodes_from(to_remove)

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=True,
        cdn_resources="remote"
    )
    net.from_nx(graph)
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.25,
          "springLength": 130,
          "springConstant": 0.04,
          "damping": 0.85,
          "avoidOverlap": 1
        },
        "stabilization": {
          "iterations": 300
        }
      },
      "edges": {
        "smooth": false,
        "color": {
          "color": "rgba(180,180,180,0.15)"
        }
      },
      "interaction": {
        "hover": true,
        "dragNodes": true,
        "zoomView": true
      }
    }
    """)

    # Add resource nodes under each page node
    for category, from_url, value in resources:
        if from_url not in graph:
            continue
        res_id = f"{category}|{from_url}|{value}"
        res_label = value
        res_color = RESOURCE_COLORS.get(category, "#cccccc")
        net.add_node(
            res_id,
            label=res_label,
            title="-",  # no title for resource nodes
            color=res_color,
            shape="dot",
            size=12,
            type=category,
            url_value=value,
        )
        net.add_edge(from_url, res_id, color=res_color, arrows="to")

    degrees = dict(graph.degree())
    out_degrees = dict(graph.out_degree())
    try:
        levels = nx.single_source_shortest_path_length(graph, start_url)
    except Exception:
        levels = {}

    for node in net.nodes:
        url = node.get("id")
        type_val = node.get("type")
        is_page = url in graph
        level_val = levels.get(url) if is_page else None
        links_out_val = out_degrees.get(url) if is_page else None
        url_value = node.get("url_value") if not is_page else url
        title_val = node.get("title") if is_page else "-"

        node["label"] = ""
        node["title"] = (
            f"Title: {title_val or '-'}\n"
            f"URL: {url_value or '-'}\n"
            f"Type: {type_val or ('page' if is_page else 'resource')}\n"
            f"Depth: {level_val if level_val is not None else '-'}\n"
            f"Links out: {links_out_val if links_out_val is not None else '-'}"
        )
        node["size"] = min(8 + degrees.get(url, 0) * 1.5, 40)
        node["type"] = node.get("type") or ("page" if is_page else "resource")
        if url == start_url:
            node["size"] = 50
            node["color"] = "#ffcc00"

    html_path = os.path.join(export_path, f"{prefix}_graph.html")
    net.write_html(html_path)
    if verbose:
        print(f"## Visualization created at: {html_path}")
    return html_path

