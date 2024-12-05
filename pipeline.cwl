#!/usr/bin/env cwl-runner
class: Workflow
cwlVersion: v1.1
requirements:
  ScatterFeatureRequirement: {}

inputs:
  input_directory:
    type: Directory
  hyperparameters_file:
    type: File?

outputs:
  ribca_results_full:
    type: Directory
    outputSource: post-convert/ribca_results_full
  ribca_results_for_sprm:
    type: Directory
    outputSource: post-convert/ribca_results_for_sprm

steps:
  pre-convert:
    run: steps/pre-convert.cwl
    in:
      directory: input_directory
    out:
      - image_directories

  ribca:
    run: steps/ribca.cwl
    scatter: directory
    in:
      directory: pre-convert/image_directories
      hyperparameters_file: hyperparameters_file
    out: [results_dir]

  post-convert:
    run: steps/post-convert.cwl
    in:
      ribca_results_dir: ribca/results_dir
    out: [ribca_results_full, ribca_results_for_sprm]
