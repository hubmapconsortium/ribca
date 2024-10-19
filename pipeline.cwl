#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1

inputs:
  image_file:
    type: File
  mask_file:
    type: File

outputs:
  ribca_results_dir:
    type: Directory
    outputSource: ribca/results_dir

steps:
  pre-convert:
    run: steps/pre-convert.cwl
    in:
      expr_input: image_file
      mask_input: mask_file
    out:
      - marker_list_file
      - image_file
      - mask_file

  ribca:
    run: steps/ribca.cwl
    in:
      marker_list_file: pre-convert/marker_list_file
      image_file: pre-convert/image_file
      mask_file: pre-convert/mask_file
    out: [results_dir]
