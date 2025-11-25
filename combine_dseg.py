import os
import warnings
from typing import Iterable, Mapping, Sequence, Union, Any
import argparse
import json
import ast

import nibabel as nib
import numpy as np

# combine_dseg.py
# GitHub Copilot



def _parse_groups_arg(arg: str) -> Any:
    # arg can be a path to a file containing JSON or Python literal,
    # or a JSON/Python literal string on the command line.
    if os.path.exists(arg):
        with open(arg, "r") as fh:
            txt = fh.read()
    else:
        txt = arg
    try:
        return json.loads(txt)
    except Exception:
        return ast.literal_eval(txt)

def _dtype_from_str(s: str):
    if s is None:
        return None
    s = s.lower()
    mapping = {"int8": np.int8, "int16": np.int16, "int32": np.int32, "int64": np.int64}
    return mapping.get(s, np.dtype(s))

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Combine labels in a dseg NIfTI")
    p.add_argument("dseg", help="Path to input dseg NIfTI")
    p.add_argument("--groups", "-g", required=True,
                   help="Groups mapping. JSON or Python literal. Examples: "
                        "'[[1,2,3],[4,5]]' or '{1:[1,2,3],2:[4,5]}' or path to file containing either.")
    p.add_argument("--output", "-o", help="Output NIfTI path (optional).")
    p.add_argument("--start-label", type=int, default=1, help="Start label when groups is a sequence.")
    p.add_argument("--preserve-zero", dest="preserve_zero", action="store_true", default=True,
                   help="Preserve original zeros (default).")
    p.add_argument("--no-preserve-zero", dest="preserve_zero", action="store_false",
                   help="Do not preserve original zeros.")
    p.add_argument("--out-dtype", help="Output dtype name, e.g. int8,int16,int32. If omitted inferred automatically.")
    return p

def _cli() -> Any:
    parser = _build_arg_parser()
    args = parser.parse_args()

    groups = _parse_groups_arg(args.groups)
    out_dtype = _dtype_from_str(args.out_dtype)

    # Directly call the worker function (no reload) when running as a script.
    result = combine_dseg_labels(
        args.dseg,
        groups,
        output_path=args.output,
        start_label=args.start_label,
        preserve_zero=args.preserve_zero,
        out_dtype=out_dtype,
    )

    if args.output:
        print(f"Saved combined dseg to {args.output}")
    else:
        print("Combined labels (no output file).")
    return result

# Note: do not call _cli() here directly; the code above will trigger it when executing the script.
def combine_dseg_labels(
    dseg_input: Union[str, nib.Nifti1Image],
    groups: Union[Sequence[Iterable[int]], Mapping[int, Iterable[int]]],
    output_path: str = None,
    start_label: int = 1,
    preserve_zero: bool = True,
    out_dtype: np.dtype = None,
) -> nib.Nifti1Image:
    """
    Combine label values in a dseg (label) NIfTI into fewer ROI labels.

    Parameters
    - dseg_input: path to dseg NIfTI file or a nibabel Nifti1Image.
    - groups: either
        * a sequence (list/tuple) of iterables of integers, e.g. [[1,2,3],[4,5]]
          Each inner group becomes a single ROI with label start_label + index.
        * a mapping {new_label: iterable_of_original_labels}, e.g. {1: [1,2,3], 2: [4,5]}
          When mapping is provided, keys are used directly as new labels.
    - output_path: optional path to save the resulting NIfTI. If None the file is not saved.
    - start_label: used only when `groups` is a sequence; first group's new label.
    - preserve_zero: if True, voxels with original label 0 remain 0 in output.
    - out_dtype: numpy dtype for output volume. If None, chosen based on max label.

    Returns
    - nib.Nifti1Image of the combined-label volume. If output_path was provided, file is saved.
    """
    # Load image
    if isinstance(dseg_input, str):
        img = nib.load(dseg_input)
    elif isinstance(dseg_input, nib.Nifti1Image):
        img = dseg_input
    else:
        raise TypeError("dseg_input must be a file path or a nibabel Nifti1Image")

    data = img.get_fdata(dtype=np.float32).astype(np.int32)

    # Build mapping: original_label -> new_label
    mapping = {}
    if isinstance(groups, Mapping):
        for new_label, originals in groups.items():
            for lab in originals:
                if lab in mapping:
                    warnings.warn(f"Original label {lab} already mapped to {mapping[lab]}; keeping first mapping.")
                    continue
                mapping[int(lab)] = int(new_label)
    else:
        # sequence of groups
        for idx, grp in enumerate(groups):
            new_label = int(start_label + idx)
            for lab in grp:
                lab = int(lab)
                if lab in mapping:
                    warnings.warn(f"Original label {lab} already mapped to {mapping[lab]}; keeping first mapping.")
                    continue
                mapping[lab] = new_label

    # Determine output dtype
    max_new = max(mapping.values()) if mapping else 0
    reserve = 1 if preserve_zero else 0
    needed_max = max(max_new, reserve)
    if out_dtype is None:
        if needed_max <= np.iinfo(np.int8).max:
            out_dtype = np.int8
        elif needed_max <= np.iinfo(np.int16).max:
            out_dtype = np.int16
        else:
            out_dtype = np.int32

    out = np.zeros(data.shape, dtype=out_dtype)

    # Optionally preserve zeros (already zero)
    # Apply mappings
    for orig_label, new_label in mapping.items():
        if orig_label == 0 and preserve_zero:
            continue
        out[data == orig_label] = new_label

    # Create new image preserving affine and (most of) header info
    new_img = nib.Nifti1Image(out, img.affine, header=img.header.copy())
    # update header like dtype
    new_img.set_data_dtype(out_dtype)

    if output_path:
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        nib.save(new_img, output_path)

    return new_img


# Example usage:
# if __name__ == "__main__":
#     # Combine labels 1,2,3 -> new label 1; labels 4,5 -> new label 2
#     combine_dseg_labels("dseg.nii.gz", [[1, 2, 3], [4, 5]], output_path="combined.nii.gz")

# From terminal: (check README.md)
# python3 combine_dseg.py \
#  /pathToFile/dseg.nii.gz \
#  -g '[[17,53]]' \
#  -o /pathToOut/ROI.nii.gz


# ...existing code...
if __name__ == "__main__":
    _cli()
# ...existing code...