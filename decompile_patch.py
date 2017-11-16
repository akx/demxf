import argparse
import json

from demxf.decompiler import decompile_patch, decompile_patchverse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', help='input JSON file', required=True)
    args = ap.parse_args()
    with open(args.input, 'rb') as infp:
        patchverse = json.load(infp)
        if 'patcher' in patchverse:
            decompile_patch(patchverse)
        else:
            decompile_patchverse(patchverse)


if __name__ == '__main__':
    main()
