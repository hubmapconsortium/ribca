#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca-prep-convert
baseCommand: "/opt/convert_ribca_output.py"

inputs:
  ribca_results_dir:
    type: Directory[]
    inputBinding:
      position: 0

outputs:
  results_hdf5:
    type: File[]
    outputBinding:
      glob: "*.hdf5"
  results_csv_dir:
    type: Directory
    outputBinding:
      glob: "ribca"
