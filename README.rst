Triage
=======



.. code:: sh

  # 1. Set your <fuzzing output path> and <target path> in `config.py` and create pocs directory
  mkdir pocs

  # 2. Run targets
  python3 app.py

  # 3. Filter output.txt
  python3 filter.py
  # -v, --verbose: print crash id, ASAN summary information

  # 4. Generate report, pretty print `output.txt`
  python3 pretty-print.py
  # -i, --id <int>: generate report with crash id


