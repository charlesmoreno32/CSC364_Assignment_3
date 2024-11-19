import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
data = pd.read_csv("retransmissions_vs_time50%.csv")

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(data["Time"], data["Retransmissions"], marker='o', color='b', label='cwnd')

# Add labels, title, and legend
plt.xlabel("RTT #")
plt.ylabel("retransmissions")
#plt.title("Congestion Window (cwnd) vs. Time (RTT) 1%")
plt.title("Retransmissions vs. Time (RTT) 50%")
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
