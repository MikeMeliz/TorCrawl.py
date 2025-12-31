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

    # Build BFS tree from start_url (one parent per node)
    try:
        tree = nx.bfs_tree(graph, start_url)
    except Exception:
        tree = graph.copy()

    # Assign levels (depth)
    levels = nx.single_source_shortest_path_length(tree, start_url) if tree else {}
    for node, level in levels.items():
        tree.nodes[node]["level"] = level
        tree.nodes[node]["value"] = 1

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=False,
        cdn_resources="remote"
    )
    net.from_nx(tree)
    net.set_options("""
    {
      "physics": {
        "enabled": false
      },
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "nodeSpacing": 180,
          "treeSpacing": 240,
          "levelSeparation": 200,
          "edgeMinimization": true,
          "blockShifting": true,
          "parentCentralization": true
        }
      },
      "edges": {
        "smooth": false
      },
      "interaction": {
        "dragNodes": false,
        "zoomView": true
      }
    }
    """)

    # Add resource nodes under each page node
    for category, from_url, value in resources:
        if from_url not in tree:
            continue
        res_id = f"{category}|{from_url}|{value}"
        res_label = value
        level = tree.nodes[from_url].get("level", 0) + 1
        res_color = RESOURCE_COLORS.get(category, "#cccccc")
        net.add_node(
            res_id,
            label=res_label,
            title=f"{category}: {value}",
            level=level,
            color=res_color,
            shape="dot",
            size=12,
        )
        net.add_edge(from_url, res_id, color=res_color, arrows="to")

    for node in net.nodes:
        url = node.get("id")
        if url in tree:
            title = node.get("title") or url
            level = tree.nodes[url].get("level", 0)
            node["label"] = node["label"] if level <= 1 else ""
            node["title"] = f"{title}\n{url}" if url else title
            node["size"] = 10 + tree.out_degree(url) * 2

    for edge in net.edges:
        edge["color"] = "rgba(150,150,150,0.15)"

    html_path = os.path.join(export_path, f"{prefix}_graph.html")
    net.write_html(html_path)
    if verbose:
        print(f"## Visualization created at: {html_path}")
    return html_path

