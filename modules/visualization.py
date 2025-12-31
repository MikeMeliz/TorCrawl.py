import os
import sqlite3

import networkx as nx  # type: ignore
from pyvis.network import Network  # type: ignore


def export_visualization(export_path, prefix, start_url, verbose=False):
    """Generate an HTML visualization from the SQLite database using NetworkX and PyVis."""
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
    finally:
        conn.close()

    graph = nx.DiGraph()
    for url, title in nodes:
        graph.add_node(url, title=title or url, label=title or url)
    for src, dst in edges:
        if src and dst:
            graph.add_edge(src, dst, title=f"{src} -> {dst}")

    try:
        shortest = dict(nx.single_source_shortest_path_length(graph, start_url))
    except Exception:
        shortest = {}
    for node in graph.nodes:
        graph.nodes[node]["level"] = shortest.get(node, 0)
        graph.nodes[node]["value"] = 1

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=False,
        cdn_resources="remote",
    )
    net.from_nx(graph)
    net.set_options("""
    {
      "physics": {
        "enabled": false
      },
      "edges": {
        "smooth": false
      },
      "layout": {
        "improvedLayout": true,
        "hierarchical": {
          "enabled": true,
          "sortMethod": "directed",
          "direction": "LR",
          "shakeTowards": "roots",
          "nodeSpacing": 180,
          "treeSpacing": 260,
          "blockShifting": true,
          "edgeMinimization": true,
          "parentCentralization": true,
          "spacingFactor": 1.2
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": false,
        "dragNodes": false,
        "zoomView": true
      }
    }
    """)

    for node in net.nodes:
        url = node.get("id")
        title = node.get("title") or url
        is_root = url == start_url
        node["label"] = title if is_root else ""
        node["title"] = f"{title} <br/> {url}" if url else title

    for edge in net.edges:
        edge["color"] = "rgba(150,150,150,0.15)"

    html_path = os.path.join(export_path, f"{prefix}_graph.html")
    net.write_html(html_path)
    if verbose:
        print(f"## Visualization created at: {html_path}")
    return html_path

