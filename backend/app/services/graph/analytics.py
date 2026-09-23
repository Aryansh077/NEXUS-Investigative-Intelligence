import networkx as nx
from ...database.db import get_conn

def load_graph(case_id):
    conn = get_conn()
    ents = [dict(r) for r in conn.execute("SELECT * FROM entities WHERE case_id=?", (case_id,)).fetchall()]
    rels = [dict(r) for r in conn.execute("SELECT * FROM relationships WHERE case_id=?", (case_id,)).fetchall()]
    conn.close()
    G = nx.Graph()
    for e in ents:
        G.add_node(e["id"], label=e["name"], type=e["type"])
    for r in rels:
        G.add_edge(r["source_id"], r["target_id"], id=r["id"], type=r["type"], confidence=r["confidence"], timestamp=r["timestamp"], source_record=r["source_record"], verification=r["verification"])
    return G, ents, rels

def graph_for_case(case_id, entity_type=None, search=None):
    G, ents, rels = load_graph(case_id)
    if entity_type:
        allowed_types = {value.strip().upper() for value in entity_type.split(",")}
        allowed_nodes = {entity["id"] for entity in ents if entity["type"].upper() in allowed_types}
        G.remove_nodes_from(set(G.nodes) - allowed_nodes)
        ents = [entity for entity in ents if entity["id"] in allowed_nodes]
    if search:
        needle = search.casefold()
        matching_nodes = {
            entity["id"] for entity in ents
            if needle in entity["id"].casefold() or needle in entity["name"].casefold()
        }
        G.remove_nodes_from(set(G.nodes) - matching_nodes)
        ents = [entity for entity in ents if entity["id"] in matching_nodes]
    nodes = [{"id":n, **d} for n,d in G.nodes(data=True)]
    visible_nodes = set(G.nodes)
    edges = [{"id":d.get("id"), "source":u, "target":v, **{k:d[k] for k in ["type","confidence","timestamp","source_record","verification"]}} for u,v,d in G.edges(data=True) if u in visible_nodes and v in visible_nodes]
    return {"nodes":nodes, "edges":edges}

def find_path(case_id, source, target):
    G, ents, rels = load_graph(case_id)
    if source not in G or target not in G:
        # allow entity names
        mapping = {d.get("label"):n for n,d in G.nodes(data=True)}
        source, target = mapping.get(source, source), mapping.get(target, target)
    if source not in G or target not in G or not nx.has_path(G, source, target):
        return None
    path = nx.shortest_path(G, source, target)
    node_map = {e["id"]:e for e in ents}
    steps=[]
    for a,b in zip(path,path[1:]):
        d=G.get_edge_data(a,b)
        steps.append({"from":node_map[a]["name"],"to":node_map[b]["name"],"relation":d.get("type"),"confidence":d.get("confidence"),"evidence_id":d.get("source_record"),"timestamp":d.get("timestamp")})
    return {"path":[node_map[x]["name"] for x in path], "steps":steps}

def graph_metrics(case_id):
    G, ents, _ = load_graph(case_id)
    degree = nx.degree_centrality(G) if len(G) else {}
    between = nx.betweenness_centrality(G) if len(G) else {}
    communities = list(nx.connected_components(G))
    names={e["id"]:e["name"] for e in ents}
    return {
        "degree": sorted([{"entity":names.get(k,k),"score":round(v,3)} for k,v in degree.items()], key=lambda x:-x["score"])[:10],
        "betweenness": sorted([{"entity":names.get(k,k),"score":round(v,3)} for k,v in between.items()], key=lambda x:-x["score"])[:10],
        "communities":[[names.get(x,x) for x in c] for c in communities]
    }
