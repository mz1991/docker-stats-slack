# Docker containers statistics notifications in Slack

Monitor Docker containers resource utilization statistics and post alarm messages to a Slack channel:

Environment variables needed:
<ul>
 	<li>SLACK_WEBHOOK_URL: the webhook url for your Slack team</li>
 	<li>SLACK_CHANNEL: the channel id (where the message will be posted)</li>
 	<li>SLACK_USERNAME: the username for the incoming messages</li>
 	<li>SLACK_EMOJI: the emoji for the incoming messages</li>
 	<li>MEMORY_PERCENTAGE: maximum percentage of RAM memory used for each container. When the percentage of used memory will exceed this threshold, an alarm will be posted to the Slack channel</li>
 	<li>CPU_PERCENTAGE: maximum percentage CPU usage for each container. When the CPU percentage usage will exceed this threshold, an alarm will be posted to the Slack channel</li>
 	<li>SLEEP_TIME (seconds) : interval between each message posted to Slack. Number of seconds between messages, unique for container.</li>
</ul>

To run the script:

```shell
$ SLACK_WEBHOOK_URL=https://hooks.slack.com/services/yourSlackWebHookId
   SLACK_CHANNEL=#docker-stats 
   SLACK_USERNAME="Docker Hook" SLACK_EMOJI=:whale: 
   MEMORY_PERCENTAGE=20 CPU_PERCENTAGE=40 SLEEP_TIME=60 
   python3 docker_stat.py
```

Read more about this here: [Docker containers stats notifications in Slack](https://whiletrue.run/2017/01/06/post-docker-containers-statistics-to-slack/)

Code reference:

 * [docker-py](https://github.com/docker/docker-py) to connect to the Docker deamon