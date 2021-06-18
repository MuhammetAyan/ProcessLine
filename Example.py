import ProcessLine.Process as pr
import sys

# Define IO
inp = pr.ProcessInput("input-example.csv", pr.ProcessIOType.Csv)
inp.attributes["split-char"] = ','

out = pr.ProcessOutput("output.csv", pr.ProcessIOType.Csv)
out.attributes["split-char"] = '\t'

# Define process object
pro = pr.Process(inp, out)

# As an example, the test layer is defined.
def TestLayer(lyr):
    # Gender information will be abbreviated.
    maleCount = 0
    femaleCount = 0
    passCount = 0
    for row in lyr:
        if row[4].lower() == "male":
            row[4] = "M"
            maleCount += 1
        elif row[4].lower() == "female":
            row[4] = "F"
            femaleCount += 1
        else:
            passCount += 1
            continue
        yield row
    # After all the data is read, it will be written to the console.
    print("Male count:", maleCount)
    print("Female count:", femaleCount)
    print("Pass count:", passCount)

# Specify middleware layers
pro.Layers = [
    pr.Layer(TestLayer)
    # Here middleware functions will be specified.
]

# IO files are opening. 
pro.start()

print("Start data processing...")
count = 0
# The process works here.
for row in pro.process():
    count += 1
    sys.stdout.write(f"\r{count} pieces of data were preprocessed.")
print("Preprocessing is complete.")

# IO files are closing.
pro.close()