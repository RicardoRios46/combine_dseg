# NIfTI dseg Label Combiner

A Python utility (`combine_dseg.py`) for merging multiple label values in a NIfTI segmentation volume (dseg) into a fewer number of combined ROI labels.

(NOTE/disclaimer: This whole repository was made with the assistance of copilot and gemini. I am experimenting with both tools).

-----

## 🛠️ Installation and Setup

This project uses **Pixi** to manage dependencies and create a reproducible environment using the Conda ecosystem.

### **Prerequisites**

You must have **Pixi** installed on your system.

  * **Install Pixi:** Follow the official installation instructions for your operating system. For linux:
    ```bash
    curl -Ls https://pixi.sh/install.sh | bash
    ```

### **1. Clone the Repository**

First, clone the repository to your local machine:

```bash
git clone [YOUR_REPOSITORY_URL]
cd [YOUR_REPOSITORY_NAME]
```

### **2. Install Dependencies**

Pixi reads the `pixi.toml` file and installs all required packages (including `python`, `numpy`, and `nibabel`) into an isolated environment.

```bash
pixi install
```


-----

## 🚀 Usage

The main script is `combine_dseg.py`. All execution should be done using `pixi run` to ensure you are using the correct virtual environment and dependencies.

### **Syntax**

```bash
pixi run python combine_dseg.py <dseg_input_file> --groups <group_mapping> --output <output_file> [options]
```

### **Required Arguments**

| Argument | Description |
| :--- | :--- |
| `<dseg_input_file>` | Path to the input NIfTI segmentation image (`dseg.nii.gz`). |
| `--groups` (`-g`) | The mapping of original labels to new labels. Can be a JSON/Python literal string or a path to a file containing the mapping. |

### **Groups Mapping (`--groups`)**

The grouping argument must be a sequence of groups or a mapping of new labels.

| Format | Example | Result |
| :--- | :--- | :--- |
| **Sequence** (New labels assigned sequentially) | `[[1, 2, 3], [4, 5]]` | Original labels 1, 2, 3 become new label **1**. <br> Original labels 4, 5 become new label **2**. |
| **Mapping** (New labels explicitly defined) | `{10: [1, 2, 3], 20: [4, 5]}` | Original labels 1, 2, 3 become new label **10**. <br> Original labels 4, 5 become new label **20**. |

### **Optional Arguments**

| Option | Default | Description |
| :--- | :--- | :--- |
| `--output`, `-o` | None | Path to save the resulting NIfTI file. |
| `--start-label` | 1 | The label for the first group when `--groups` is a sequence. |
| `--preserve-zero` | True | Keeps voxels with original label 0 as 0 in the output. |
| `--no-preserve-zero` | | Do not preserve original zeros (assigns them a new label if mapped). |
| `--out-dtype` | Inferred | Output numpy data type (`int8`, `int16`, `int32`, etc.). |

### **Example Execution**

The example uses the pre-defined task in `pixi.toml` file to combine labels 17 and 53 into a single ROI.

**Note:** Ensure you replace `input.nii.gz` with the path to your actual segmentation file.

```bash
# Combine labels 17 and 53 into a new sequential label (default 1)
pixi run combine-example
# Equivalent to:
# python combine_dseg.py input.nii.gz -g '[[17, 53]]' -o combined_output.nii.gz
```

-----

## Alternative: Standard `pip` Installation

If you prefer to use standard Python tools without Pixi, you can install the dependencies using the `requirements.txt` file.

### **1. Create a Virtual Environment (Recommended)**

It is highly recommended to isolate your project dependencies using a virtual environment: (The example use venv but you can create one with conda/mamba)

```bash
# Create the environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate
```

### **2. Install Dependencies**

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

### **3. Run the Script**

Run the script directly using the Python interpreter within the active virtual environment:

```bash
python combine_dseg.py input.nii.gz -g '[[17, 53]]' -o combined_output.nii.gz
```

-----

## Repository ToDo
- It's not clear what the "example execution" does. What is the purporse of those pixi task?
- How to build a python application? Is it worth it?
- Create python test. Add them in the pixi toml.
- How to run github automatic test?
