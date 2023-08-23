Triage
=======



.. code:: sh

  # 1. Set your <fuzzing output path> and <target path> in `config.py`

  # 2. Run targets
  python3 app.py

  # 3. Filter output.txt
  python3 filter.py
  # -v, --verbose: print crash id, ASAN summary information

  # 4. Generate report
  python3 pretty-print.py --id <id>


