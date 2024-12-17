#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca-prep-convert:1.0
baseCommand: "/opt/convert_ribca_output.py"

inputs:
  ribca_results_dir:
    type: Directory[]
    inputBinding:
      position: 0

outputs:
  ribca_results_full:
    type: Directory
    outputBinding:
      glob: "ribca_results"
  ribca_results_for_sprm:
    type: Directory
    outputBinding:
      glob: "ribca_for_sprm"
