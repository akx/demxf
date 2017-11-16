import argparse
import json

from demxf.viz import PatchGrapher


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', help='input JSON file', required=True)
    ap.add_argument('-o', '--output', help='output graphviz', required=True)
    args = ap.parse_args()
    with open(args.input, 'rb') as infp:
        patch = json.load(infp)
        pg = PatchGrapher()
        pg.initialize(patch)
        graph = pg.dump()
        graph.render(args.output)

if __name__ == '__main__':
    main()
