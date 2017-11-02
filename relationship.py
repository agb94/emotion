import operator
import util
import math
try:
    import matplotlib.pyplot as plt
except:
    raise
import networkx as nx

def get_appearance(metadata):
    appearance = {}
    for character in set(list(map(lambda row: row['character_id'], metadata))):
        appearance[character] = list(map(lambda row: row['frame_number'], list(filter(lambda row: row['character_id'] == character, metadata))))
        appearance[character].sort()
    return appearance

def get_relationship(appearance):
    def relationship_key(a, b):
        if a < b:
            return (a, b)
        return (b, a)

    total_apperance_count = 0
    for character in appearance:
        total_apperance_count += len(appearance[character])
    
    relationship = {}
    for character in appearance:
        for other in appearance:
            if character == other:
                continue
            key = relationship_key(character, other)
            if key in relationship:
                continue
            else:
                relationship[key] = 0.0
            for frame in appearance[character]:
                if frame in appearance[other]:
#                    relationship[key] += float(len(appearance[character]) + len(appearance[other])) / total_apperance_count
                    continue

    for character in appearance:
        for i in range(len(appearance[character]) - 1):
            start = appearance[character][i]
            end = appearance[character][i+1]
            if start == end:
                continue
            weight = 1/float((end-start))
            for other in appearance:
                if character == other:
                    continue
                key = relationship_key(character, other)
                relationship[key] += weight * len(list(filter(lambda f: f in range(start, end+1), appearance[other])))
    return relationship

def draw_relationship_graph(appearance, relationship):
    G=nx.Graph()

    for u in appearance:
        G.add_node(u)

    for key in relationship:
	u, v = key
	weight = relationship[key]
        if weight > 0.01:
            G.add_edge(u, v, weight=weight)

    pos=nx.spring_layout(G) # positions for all nodes

    # nodes
    nx.draw_networkx_nodes(G,pos,node_size=350)

    # edges
    for (u, v, d) in G.edges(data=True):
        nx.draw_networkx_edges(G, pos, edgelist=[(u,v)], 
            width=math.ceil(relationship[(u,v)] * 10),
            edge_color='b'
        )

    nx.draw_networkx_labels(G,pos,font_size=10,font_family='sans-serif')

    plt.axis('off')
    plt.savefig("weighted_graph.png") # save as png
    plt.show() # display


metadata = util.parse_metadata_file('yellows1ep01-oracle.tsv')
appearance = get_appearance(metadata)
relationship = get_relationship(appearance)
sorted_relationship = sorted(relationship.items(), key=operator.itemgetter(1))
sorted_relationship.reverse()
print(sorted_relationship)
  
#draw_relationship_graph(appearance, relationship)
