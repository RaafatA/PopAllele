# PopAllele
PopAllele is a package that decode the genetic distribution of alleles within populations into QR codes 

#### Installing the package - conda 
``` bash 
cd PopAllele
conda env create -f environment.yml 
conda activate PopAllele
```
#### Usage Documentation
``` bash 
PopAllele/pop_run.py --help
```

```bash
usage: pop_run.py [-h] [--QRd CSV_FILE] [--QRe QR_CODE_IMAGE]

options:
  -h, --help           show this help message and exit
  --QRd CSV_FILE       Generate QR codes from a CSV file
  --QRe QR_CODE_IMAGE  Generate QR codes from a QR code image

```
