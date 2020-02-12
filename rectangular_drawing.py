import networkx as nx
import matplotlib.pyplot as plt
import copy
import json
from networkx.algorithms.planarity import PlanarEmbedding


PATH = []


def FindBorderDfs(g, idx, embeddings, forced_next=None, stack=[], prev=None):
    node_mark = 'was'
    edge_mark = 'used'
    if g.nodes[idx].get(node_mark):
        return stack
    g.nodes[idx][node_mark] = True
    if forced_next:
        g.edges[idx, forced_next][edge_mark] = True
        r = FindBorderDfs(g, forced_next, embeddings, stack=[idx], prev=idx)
        return r
    node = embeddings[idx][prev]['ccw']
    while node != prev:
        if not g.get_edge_data(idx, node).get(edge_mark):
            g.edges[idx, node][edge_mark] = True
            r = FindBorderDfs(g, node, embeddings, stack=stack + [idx], prev=idx)
            if r:
                return r
        node = embeddings[idx][node]['ccw']
    return stack


def CornersInBorder(borders, corners):
    borders_set = set(borders)
    for corner in corners:
        if corner not in borders_set:
            return False
    pos_nw = borders.index(corners[0])
    pos_ne = borders.index(corners[1])
    pos_se = borders.index(corners[2])
    pos_sw = borders.index(corners[3])
    return pos_nw < pos_sw < pos_se < pos_ne


def MarkBorders(g, borders, corners):
    borders_mark = "is_border"
    path_mark = "path_mark"
    orient_mark = "orient"
    corners_set = set(corners)
    idx = 0
    marks = ["W", "S", "E", "N"]
    orient_marks = ["v", "h", "v", "h"]
    for i in range(1, len(borders)):
        g.nodes[borders[i]][borders_mark] = 1
        g.edges[borders[i - 1], borders[i]][borders_mark] = 1
        g.edges[borders[i - 1], borders[i]][path_mark] = marks[idx]
        g.edges[borders[i - 1], borders[i]][orient_mark] = orient_marks[idx]
        if marks[idx] == "E" or marks[idx] == "N":
            g.edges[borders[i - 1], borders[i]]['prior'] = borders[i]
        else:
            g.edges[borders[i - 1], borders[i]]['prior'] = borders[i - 1]
        if borders[i] in corners_set:
            idx += 1
            g.nodes[borders[i]][path_mark] = marks[idx - 1] + marks[idx]
        else:
            g.nodes[borders[i]][path_mark] = marks[idx]

    g.nodes[borders[0]][borders_mark] = 1
    g.nodes[borders[0]][path_mark] = "NE"
    g.edges[borders[0], borders[-1]][borders_mark] = 1
    g.edges[borders[0], borders[-1]][path_mark] = "N"
    g.edges[borders[0], borders[-1]][orient_mark] = 'h'
    g.edges[borders[0], borders[-1]]["prior"] = borders[0]
    return g


def MarkPathDfs(g, idx, embeddings, forced_next=None, path=[], prev=None, last_border=None, path_dict={}, ignore_nodes=set({})):
    node_mark = 'was'
    edge_mark = 'used'
    border_mark = "is_border"
    global PATH
    if g.nodes[idx].get("out_left") is None:
        g.nodes[idx]["out_left"] = g.out_degree(idx)

    if g.nodes[idx].get(border_mark):
        PATH = PATH + [idx]
        if len(PATH) > 2 or len(PATH) == 2 and g.edges[PATH[0], PATH[1]].get("is_border") is None:
            path_dict[tuple(PATH)] = last_border + g.nodes[idx].get("path_mark")
        last_border = g.nodes[idx].get("path_mark")
        PATH = []

    g.nodes[idx][node_mark] = True

    if forced_next:
        g.edges[idx, forced_next][edge_mark] = True
        PATH = PATH + [idx]
        g.nodes[idx]["out_left"] -= 1
        MarkPathDfs(g, forced_next, embeddings, path=path + [forced_next], prev=idx, last_border=last_border, path_dict=path_dict, ignore_nodes=ignore_nodes)
        return path_dict

    node = embeddings[idx][prev]['ccw']
    while g.nodes[idx].get("out_left") > 0:
        if node not in ignore_nodes and not g.get_edge_data(idx, node).get(edge_mark):
            g.edges[idx, node][edge_mark] = True
            PATH = PATH + [idx]
            g.nodes[idx]["out_left"] -= 1
            MerkPathDfs(g, node, embeddings, path=path + [node], prev=idx, last_border=last_border, path_dict=path_dict, ignore_nodes=ignore_nodes)
        node = embeddings[idx][node]['ccw']
    return path_dict


def MarkPaths(g, embeddings, corners, borders, ignore_nodes=set({})):
    global PATH
    PATH = []
    g = mark_border(g, borders, corners)

    path_dict = MarkPathDfs(g.to_directed(), borders[0], embeddings, forced_next=borders[1], last_border=g.nodes[borders[0]]["path_mark"], path_dict={}, ignore_nodes=ignore_nodes)

    return g, path_dict


def TryCutPath(g, borders, corners, embeddings, ignore_nodes=set([])):
    if corners_in_border(borders, corners):
        start_node = corners[0]
        next_nodes = list(g.adj[start_node].keys())

        global PATH

        PATH = []
        path_dict = []

        g_marked, path_dict = MarkPaths(g.copy(), embeddings, corners, borders, ignore_nodes=ignore_nodes)

        if len(borders) == len(g_marked.edges):
            return (True, g_marked, "OK")

        orient = {
            "SN" : 'v',
            "NS" : 'v',
            "EW" : 'h',
            "WE" : 'h'
        }

        for path, mark in path_dict.items():
            if mark in orient.keys():
                start_pos = borders.index(path[0])
                end_pos = borders.index(path[-1])
                path = list(path)
                if mark == "NS":
                    new_corners = [path[0], corners[1], corners[2], path[-1]]
                    new_border = path + borders[end_pos + 1 : start_pos]
                elif mark == "SN":
                    new_corners = [corners[0], path[-1], path[0], corners[3]]
                    new_border = borders[ : start_pos] + path + borders[end_pos + 1 :]
                elif mark == "EW":
                    new_corners = [path[-1], path[0], corners[2], corners[3]]
                    new_border = borders[end_pos : start_pos] + path[ : -1]
                elif mark == "WE":
                    new_corners = [corners[0], corners[1], path[-1], path[0]]
                    new_border = borders[ : start_pos] + path + borders[end_pos + 1 : ]

                for i in range(len(path) - 1):
                    if mark == "SN" or mark == "WE":
                        g_marked.edges[path[i], path[i + 1]]['prior'] = path[i + 1]
                    else:
                        g_marked.edges[path[i], path[i + 1]]['prior'] = path[i]

                for i in range(len(path) - 1):
                    g_marked.edges[path[i], path[i + 1]]["orient"] = orient[mark]
                cut_path = []
                can_cat = False
                for i in borders + borders:
                    if i == path[0] or i == path[-1]:
                        if can_cat:
                            break
                        can_cat = True
                        cut_path = []
                    else:
                        cut_path.append(i)
                        if g_marked.degree(i) != 2:
                            can_cat = False
        g_cutted = g_marked.copy()
        g_cutted.remove_nodes_from(cut_path)
        for node in cut_path:
            ignore_nodes.add(node)
        res, g_cutted_marked, comment = GetEdgesOrientations(g_cutted, new_corners, borders=new_border, embeddings=embeddings, ignore_nodes=ignore_nodes)
        for edge in g_cutted_marked.edges:
            g_marked.edges[edge]["orient"] = g_cutted_marked.get_edge_data(edge[0], edge[1])["orient"]
            g_marked.edges[edge]["prior"] = g_cutted_marked.get_edge_data(edge[0], edge[1])["prior"]
        return (res, g_marked, comment)
    else:
        return (False, None, "border doesn't contain corners")


def GetEdgesOrientations(g, corners, embeddings=None, borders=None, ignore_nodes=set({})):
    is_planar = True
    if embeddings is None:
        is_planar, embeddings = nx.algorithms.planarity.check_planarity(g, counterexample=True)

    for corner in corners:
        if len(g.adj[corner]) != 2:
            return (False, [], "Corner nodes must have 2 neighbors, but {} has {}".format(corner, g.degree[corner]))

    start_node = corners[0]
    next_nodes = list(g.adj[start_node].keys())

    borders_first = borders_second = None
    if not borders:
        borders_first = find_border_dfs(g.copy(), start_node, embeddings, forced_next=next_nodes[0])
        borders_second = find_border_dfs(g.copy(), start_node, embeddings, forced_next=next_nodes[1])
        res, g_res, comment = TryCutPath(g.copy(), borders_first, corners, embeddings, ignore_nodes=set({}))
        if not res:
            res, g_res, comment = TryCutPath(g.copy(), borders_second, corners, embeddings, ignore_nodes=set({}))
    else:
        res, g_res, comment = TryCutPath(g.copy(), borders, corners, embeddings, ignore_nodes=ignore_nodes)
    if res:
        g_res.__setattr__("embed", embeddings)
    return res, g_res, comment


def GetEdgeTo(g, node, direction="N"):
    for node_adj in g.adj[node]:
        edge = g.adj[node][node_adj]
        if direction == "N" and edge["prior"] != node and edge["orient"] == 'v':
            return (node, node_adj)
        if direction == "W" and edge["prior"] != node and edge["orient"] == 'h':
            return (node, node_adj)
        if direction == "E" and edge["prior"] == node and edge["orient"] == 'h':
            return (node, node_adj)
        if direction == "S" and edge["prior"] == node and edge["orient"] == 'v':
            return (node, node_adj)
    return None


def CalculateYPosDFS(g, idx, embeddings, forced_next=None, prev=None, max_y=0, path=[]):
    node_mark = 'was'
    edge_mark = 'used'
    if prev is not None:
        if g.get_edge_data(prev, idx).get("orient") == "h":
            if g.get_edge_data(prev, idx).get("prior") == prev:
                edge = GetEdgeTo(g, idx, "S")
                if edge and g.adj[edge[0]][edge[1]].get("transparent"):
                    max_y = max(g.nodes[edge[1]]['y'] + 1, max_y)
            else:
                g.nodes[idx]['y'] = max_y
                g.nodes[prev]['y'] = max_y
        else:
            if g.get_edge_data(prev, idx).get('prior') == idx:
                max_y = max(g.nodes[idx]['tmp_y'], g.nodes[prev]['y'] + 1)
                g.nodes[idx]['y'] = max_y
            else:
                edge = GetEdgeTo(g, idx, "S")
                g.nodes[prev]['tmp_y'] = max_y
                if edge and g.adj[edge[0]][edge[1]].get("transparent"):
                    max_y = g.nodes[edge[1]]['y'] + 1
                else:
                    max_y = 0
                g.nodes[idx]['y'] = max_y
    if g.nodes[idx].get("out_left") is None:
        g.nodes[idx]["out_left"] = 0
        for node_adj in g.adj[idx]:
            if g.adj[idx][node_adj].get("transparent") is None:
                g.nodes[idx]["out_left"] += 1
    g.nodes[idx][node_mark] = True
    if forced_next is not None:
        g.edges[idx, forced_next][edge_mark] = True
        g.nodes[idx]["out_left"] -= 1
        res = CalculateYPosDFS(g, forced_next, embeddings, prev=idx, max_y=max_y)
        return res
    node = embeddings[idx][prev]['ccw']
    while g.nodes[idx].get("out_left") > 0:
        if not g.get_edge_data(idx, node).get(edge_mark) and not g.get_edge_data(idx, node).get("transparent"):
            g.edges[idx, node][edge_mark] = True
            g.nodes[idx]["out_left"] -= 1
            CalculateYPosDFS(g, node, embeddings, prev=idx, max_y=max_y)

        node = embeddings[idx][node]['ccw']
    res = {}
    for node in g.nodes:
        res[node] = g.nodes[node]['y']
    return res


def CalculateXPosDFS(g, idx, embeddings, forced_next=None, prev=None, max_x=0, path=[]):
    node_mark = 'was'
    edge_mark = 'used'
    if prev is not None:
        if g.get_edge_data(prev, idx).get("orient") == "v":
            if g.get_edge_data(prev, idx).get("prior") == prev:
                edge = GetEdgeTo(g, idx, "W")
                if edge and g.adj[edge[0]][edge[1]].get("transparent"):
                    max_x = max(g.nodes[edge[1]]['x'] + 1, max_x)
            else:
                g.nodes[idx]['x'] = max_x
                g.nodes[prev]['x'] = max_x
        else:
            if g.get_edge_data(prev, idx).get('prior') == prev:
                max_x = max(g.nodes[idx]['tmp_x'], g.nodes[prev]['x'] + 1)
                g.nodes[idx]['x'] = max_x
            else:
               edge = GetEdgeTo(g, idx, "W")

               g.nodes[prev]['tmp_x'] = max_x
               if edge and g.adj[edge[0]][edge[1]].get("transparent"):
                   max_x = g.nodes[edge[1]]['x'] + 1
               else:
                   max_x = 0
               g.nodes[idx]['x'] = max_x
    if g.nodes[idx].get("out_left") is None:
        g.nodes[idx]["out_left"] = 0
        for node_adj in g.adj[idx]:
            if g.adj[idx][node_adj].get("transparent") is None:
                g.nodes[idx]["out_left"] += 1
    g.nodes[idx][node_mark] = True
    if forced_next is not None:
        g.edges[idx, forced_next][edge_mark] = True
        g.nodes[idx]["out_left"] -= 1
        res = CalculateXPosDFS(g, forced_next, embeddings, prev=idx, max_x=max_x)
        return res

    node = embeddings[idx][prev]['ccw']
    while g.nodes[idx].get("out_left") > 0:
        if not g.get_edge_data(idx, node).get(edge_mark) and not g.get_edge_data(idx, node).get("transparent"):
            g.edges[idx, node][edge_mark] = True
            g.nodes[idx]["out_left"] -= 1
            CalculateXPosDFS(g, node, embeddings, prev=idx, max_x=max_x)

        node = embeddings[idx][node]['ccw']
    res = {}
    for node in g.nodes:
        res[node] = g.nodes[node].get('x')
    return res


def GetRectangularEmbedding(g, corners):
    g_y = g.copy()
    for node in g_y.nodes:
        upper_edge = GetEdgeTo(g, node, "N")
        left_edge = GetEdgeTo(g, node, "W")
        if left_edge and upper_edge:
            g_y.edges[upper_edge[0], upper_edge[1]]['transparent'] = True
    y_nodes = CalculateYPosDFS(g_y.to_directed(), corners[0], g.embed, forced_next=GetEdgeTo(g, corners[0], 'S')[1])

    g_x = g.copy()
    for node in g_x.nodes:
        upper_edge = GetEdgeTo(g, node, "N")
        right_edge = GetEdgeTo(g, node, "E")
        if right_edge and upper_edge:
            g_x.edges[right_edge[0], right_edge[1]]['transparent'] = True
    x_nodes = CalculateXPosDFS(g_x.to_directed(), corners[1], g.embed, forced_next=GetEdgeTo(g, corners[1], 'W')[1])
    embed = {}
    for i in range(len(x_nodes)):
        embed[i] = (x_nodes[i], y_nodes[i])
    return embed


def Draw(g, embed, save_to=None):
    nx.draw(g, pos=embed, with_labels=True)
    if save_to is None:
        plt.show()
    else:
        plt.savefig(save_to)
    plt.close()
