from apscheduler.schedulers.background import BackgroundScheduler

scheduler=BackgroundScheduler()

def monthly_scan():

    print("Monthly Search AI Scan Running")

scheduler.add_job(monthly_scan,"cron",day=1)

scheduler.start()