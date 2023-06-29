import scenario
import agent
import postprocessing as post

import sys

filename = "scenario_test.json" # default scenario
if(len(sys.argv) > 1): filename = sys.argv[1] + ".json" # if present, use custom scenario specified on the command line

sc = scenario.Scenario(filename)

print(f"Running scenario specified in {filename}...")

ag = agent.Agent(sc)
ag.run()

print(ag.action_log)
print(ag.log_pd)

post.line_chart(ag.log_pd)
post.battery_chart(ag.log_pd)
#post.bar_chart(ag.log_pd)
#post.demand_line1(ag.log_pd)
post.price_line1(ag.log_pd)

print(f"Total constraint violations: {ag.violations}")
if(ag.violations > 0):
    print(ag.violation_log)
    ag.violation_log.to_csv("output/violation_log.csv", sep="\t")
    ag.log_pd.to_csv("output/log_pd.csv", sep="\t")
