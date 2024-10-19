#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca-prep-convert
baseCommand: "/opt/convert_input_ometiffs.py"

inputs:
  expr_input:
    type: File
    inputBinding:
      position: 0
  mask_input:
    type: File
    inputBinding:
      position: 1

outputs:
  marker_list_file:
    type: File
    outputBinding:
      glob: markers.txt
  image_file:
    type: File
    outputBinding:
      glob: expr.tiff
  mask_file:
    type: File
    outputBinding:
      glob: mask.tiff
