#!/usr/bin/env cwl-runner
cwlVersion: v1.1
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: hubmap/ribca-prep-convert
baseCommand: "/opt/convert_input_ometiffs.py"

inputs:
  directory:
    type: Directory
    inputBinding:
      position: 0

outputs:
  image_directories:
    type: Directory[]
    outputBinding:
      glob: manifest.json
      loadContents: True
      outputEval: $(eval(self[0].contents))
