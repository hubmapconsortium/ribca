#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca:1.0
  DockerGpuRequirement: {}
  EnvVarRequirement:
    envDef:
      CUDA_VISIBLE_DEVICES: "0"
baseCommand: ["python", "-m", "cell_type_annotation"]

inputs:
  directory:
    type: Directory
    inputBinding:
      position: 0
  hyperparameters_file:
    type: File?
    inputBinding:
      position: 1

outputs:
  results_dir:
    type: Directory
    outputBinding:
      glob: results
