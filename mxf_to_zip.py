import argparse
import zipfile
from io import BytesIO

from demxf.catalog import read_mxf_catalog


def convert_mxf_to_zip(mxf_fp):
    bio = BytesIO()
    zf = zipfile.ZipFile(bio, 'w')
    for ce in read_mxf_catalog(mxf_fp):
        filename = (ce.filename or 'unknown/{offset}.{type}'.format(offset=ce.offset, type=(ce.type or 'unknown')))
        zf.writestr(filename, ce.extract_from(mxf_fp))
    zf.close()
    return bio.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', help='input MXF file', required=True)
    ap.add_argument('-o', '--output', help='output ZIP file', required=True)
    args = ap.parse_args()
    with open(args.input, 'rb') as infp:
        zip_data = convert_mxf_to_zip(infp)
    with open(args.output, 'wb') as outfp:
        outfp.write(zip_data)


if __name__ == '__main__':
    main()
