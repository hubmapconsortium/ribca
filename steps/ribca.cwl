#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca
  DockerGpuRequirement: {}
baseCommand: ["python", "-m", "cell_type_annotation"]

inputs:
  marker_list_file:
    type: File
    inputBinding:
      position: 0
  image_file:
    type: File
    inputBinding:
      position: 1
  mask_file:
    type: File
    inputBinding:
      position: 2

outputs:
  results_dir:
    type: Directory
    outputBinding:
      glob: results
