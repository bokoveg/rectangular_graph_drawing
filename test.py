import rectangular_drawing as rd
import networkx as nx
import os


def read_test_with_corners(file_path):
    with open(file_path, "r") as f:
        g = nx.Graph()
        n, m = [int(x) for x in f.readline().strip().split()]
        g.add_nodes_from(range(n))
        for i in range(m):
            v, u = [int(x) for x in f.readline().strip().split()]
            g.add_edge(v, u)
        corners = [int(x) for x in f.readline().strip().split()]
        res = bool(f.readline().strip() == "1")
        return g, corners, res


def run_tests():
    for file_name in os.listdir("./tests"):
        if file_name.endswith(".png"):
            continue
        g, corners, ground_res = read_test_with_corners("./tests/" + file_name)
        print("starting " + file_name + "...")

        try:
            res, g, reason = rd.GetEdgesOrientations(g, corners)
            if res:
                rectangular_embed = rd.GetRectangularEmbedding(g, corners)
                rd.Draw(g, rectangular_embed, save_to="./tests/" + file_name + "_res.png")
        except:
            res = False
            reason = "Unhandled exception"
        finally:
            if ground_res == res:
                print("Test {} passed.".format(file_name))
            else:
                print("Test {} failed.".format(file_name))
                print("res == {}".format(res))
                print("ground_res == {}".format(ground_res))
                if reason:
                    print("Possible reason: {}".format(reason))
        print("-----------------------------")


if __name__ == "__main__":
    run_tests()
