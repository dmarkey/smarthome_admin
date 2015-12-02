import datetime

from celery.task import task

from smarthome_admin.models import SocketTimerSlot


@task
def check_schedule():
    now = datetime.datetime.now()
    next = datetime.datetime.now() + datetime.timedelta(hours=1)
    args = {datetime.datetime.now().strftime("%A").lower(): True}
    tasks = SocketTimerSlot.objects.filter(**args).filter(
        start_time__gt=datetime.time(hour=now.hour), start_time__lt=datetime.time(hour=next.hour))

    [t.countdown() for t in tasks]



