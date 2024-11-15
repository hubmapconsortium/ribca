#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca
  DockerGpuRequirement: {}
  EnvVarRequirement:
    envDef:
      CUDA_VISIBLE_DEVICES: "0"
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
  hyperparameters_file:
    type: File?
    inputBinding:
      position: 3

outputs:
  results_dir:
    type: Directory
    outputBinding:
      glob: results
