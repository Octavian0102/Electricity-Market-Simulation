import agent
import postprocessing as post

ag = agent.Agent()
ag.run()

print(ag.action_log)
print(ag.log_pd)
#post.post_bar(ag.log_pd)
#post.line_chart(ag.log_pd)
