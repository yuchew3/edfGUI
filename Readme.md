#### Run the GUI
The newest program runs in python3. If any of the modules are not installed, try pip3 install *package*.

To run the GUI, run
```
python3 annotator.py
```
. Select Choose file to open a file you want to read. Loading the data might take a while. After the data is loaded the GUI will show a label "data loaded".

After you are done with labeling, click on save to save your current response files. If you didn't finish labeling the whole file, you could read this response file next time to continue labeling.

#### Flag files
A flag file stores the seconds for potential outliers for a input file. If a flag file is not provided, potential outliers are calculated by default. The default function can be modified in 
```
output.py check_bad()
```

#### Response files
A response file stores the responses for a given input file and flag file (if it has one). It is stored as a OutputDF object. See the detailed format in `output.py`


