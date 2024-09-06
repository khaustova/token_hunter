from core.celery import app

def get_watch_dexscreener_task_id():
    try:
        insp = app.control.inspect()
        active_lst = insp.active()
        worker = list(active_lst.keys())[0]
        for task in active_lst.get(worker):
            if task["name"] == "toss_a_coin.tasks.watch_dexscreener_task":
                return task["id"]
        return None
    
    except:   
        return None