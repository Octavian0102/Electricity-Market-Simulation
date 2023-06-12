import agent
import postprocessing as post

import matplotlib.pyplot as plt

ag = agent.Agent()
ag.run()

print(ag.action_log)
print(ag.log_pd)
#post.post_bar(ag.log_pd)
#post.line_chart(ag.log_pd)

plt.figure(figsize = (20, 10))
plt.plot(ag.log_pd["battery_charge"], marker = "o", markersize = 4)
plt.plot(ag.log_pd["pv"], marker = "o", markersize = 4)
plt.axhline(y = 0, color = "red", linestyle = "dashed")
plt.axhline(y = 100, color = "red", linestyle = "dashed")
plt.savefig("output.png")
