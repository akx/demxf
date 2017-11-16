import argparse
import json

import os

from demxf.catalog import read_mxf_catalog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', help='input MXF file', required=True)
    ap.add_argument('-c', '--combined', help='output combined JSON file')
    ap.add_argument('-d', '--directory', help='output directory for separate files')
    args = ap.parse_args()
    combined = {}
    with open(args.input, 'rb') as infp:
        for ce in read_mxf_catalog(infp):
            if ce.filename.endswith('.maxpat'):
                print(ce.filename)
                patch = json.loads(ce.extract_from(infp).rstrip(b'\x00'))

                if args.directory:
                    out_name = os.path.join(args.directory, ce.filename)
                    os.makedirs(os.path.dirname(out_name), exist_ok=True)
                    with open(out_name, 'w') as outfp:
                        json.dump(patch, outfp, ensure_ascii=False, indent=2, sort_keys=True)
                        print('-> {}'.format(outfp.name))

                if args.combined:
                    combined[ce.filename] = patch

    if args.combined:
        print('Writing combined file...')
        with open(args.combined, 'w') as outfp:
            json.dump(combined, outfp, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
