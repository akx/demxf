demxf
=====

Tools for manipulating Cycling'74 Max/MSP files.

Convert MXF file to ZIP
-----------------------

* `python3 mxf_to_zip.py -i some.mxf -o some.zip`

Extract and reformat all .maxpats from MXF
------------------------------------------

* `python3 extract_patches.py -i some.mxf -d output_directory`


Extract all .maxpats from MXF into a single (non-compliant) JSON file
---------------------------------------------------------------------

* `python3 extract_patches.py -i some.mxf -o combined.json`

