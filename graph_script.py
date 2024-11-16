import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
data = pd.read_csv("cwnd_vs_rtt1%.csv")

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(data["RTT"], data["cwnd"], marker='o', color='b', label='cwnd')

# Add labels, title, and legend
plt.xlabel("RTT #")
plt.ylabel("cwnd")
#plt.title("Congestion Window (cwnd) vs. Time (RTT) 1%")
plt.title("cwnd vs. Time (RTT) 1%")
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
