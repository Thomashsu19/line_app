from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
import urllib

@sched.scheduled_job('cron', minute="*/20")
def scheduled_job():
    url = "https://thomaslinebot.herokuapp.com/"
    conn = urllib.request.urlopen(url)
    print("process")
    for key, value in conn.getheaders():
        print(key, value)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    url = "https://thomaslinebot.herokuapp.com/"
    conn = urllib.request.urlopen(url)
    print("process")
    for key, value in conn.getheaders():
        print(key, value)

sched.start()