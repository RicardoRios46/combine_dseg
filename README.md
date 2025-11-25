README.md



GitHub Copilot: - Examples assume running from the project directory. Replace paths with your files.

Simple — combine groups given as a sequence:
````bash
python3 /pathToRepository/combine_dseg/combine_dseg.py /path/to/dseg.nii.gz \
  -g '[[1,2,3],[4,5]]' -o /path/to/combined.nii.gz
````

Mapping form (explicit new labels):
````bash
python3 /pathToRepository/combine_dseg/combine_dseg.py /path/to/dseg.nii.gz \
  -g '{1:[1,2,3],2:[4,5]}' -o /path/to/combined_map.nii.gz
````

Use a groups file (recommended for large mappings):
````bash
cat > groups.json <<'JSON'
[[1,2,3],[4,5]]
JSON

python3 /pathToRepository/combine_dseg/combine_dseg.py /path/to/dseg.nii.gz -g groups.json -o combined_from_file.nii.gz
````

Start label offset (when groups is a sequence):
````bash
python3 /pathToRepository/combine_dseg/combine_dseg.py dseg.nii.gz -g '[[10,11],[12]]' --start-label 5 -o out.nii.gz
# first group -> label 5, second -> label 6
````

Disable zero-preservation (make original zeros mappable):
````bash
python3 /pathToRepository/combine_dseg/combine_dseg.py dseg.nii.gz -g '[[1]]' --no-preserve-zero -o out.nii.gz
````

Force output dtype:
````bash
python3 /pathToRepository/combine_dseg/combine_dseg.py dseg.nii.gz -g '[[1,2]]' --out-dtype int16 -o out_int16.nii.gz
````

If you prefer the script to be executable, you can run:
````bash
chmod +x /pathToRepository/combine_dseg/combine_dseg.py
./pathToRepository/combine_dseg/combine_dseg.py dseg.nii.gz -g '[[1,2]]' -o out.nii.gz
````

Adjust paths/arguments as needed.


Notes:
- Use single quotes around JSON on the shell to avoid shell interpretation.
- If you prefer, put complex mappings in a JSON file and pass its path to -g.