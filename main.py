#import scenario
import agent
import postprocessing as post

#sc = scenario.Scenario("scenario01.json") # TODO get this from the command line arguments

ag = agent.Agent()
ag.run()

print(ag.action_log)
print(ag.log_pd)

post.post_bar(ag.log_pd)
#post.line_chart(ag.log_pd) # TODO fix error
post.fancy_chart(ag.log_pd)

print(f"Total constraint violations: {ag.violations}")
