from Don_Quarlos import *

dq = DonQuarlos()

results = dq.response("Do you have a horse I could ride?")

for res in results:
    print(res[1], res[0])
