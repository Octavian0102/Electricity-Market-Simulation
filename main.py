import scenario
import agent
import postprocessing as post

import sys

filename = "scenario_test.json" # default scenario
if(len(sys.argv) > 1): filename = sys.argv[1] + ".json" # if present, use custom scenario specified on the command lin

sc = scenario.Scenario(filename)

ag = agent.Agent(sc)
ag.run()

print(ag.action_log)
print(ag.log_pd)

post.post_bar(ag.log_pd)
#post.line_chart(ag.log_pd) # TODO fix error
post.fancy_chart(ag.log_pd)

print(f"Total constraint violations: {ag.violations}")
