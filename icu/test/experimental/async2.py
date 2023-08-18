import asyncio
import time


class TaskRepeatable:

    def __init__(self, fun, interval, repeat):
        self.fun = fun
        self.interval = interval
        self.repeat = repeat

    async def __call__(self):
        if self.repeat is not None:
            for _ in range(self.repeat):
                await asyncio.sleep(self.interval)
                await self.fun()
        else:
            while True:
                await asyncio.sleep(self.interval)
                await self.fun()
        
class Scheduler:

    def __init__(self):
        pass 
    def after(self, interval):
        return self.every(interval, repeat=1)

    def every(self, interval, repeat=None):
        def decorator(task_func):
            task = TaskRepeatable(task_func, interval, repeat)
            return task
        return decorator

    
async def main():
    scheduler = Scheduler()

    @scheduler.after(2)
    async def delayed_task():
        print("Delayed task executed", time.strftime('%X'))

    @scheduler.every(1)
    async def periodic_task():
        print("Periodic task executed", time.strftime('%X'))

    print("START: ", time.strftime('%X'))
    asyncio.create_task(delayed_task())
    asyncio.create_task(periodic_task())

    await asyncio.sleep(5)  # Run for 10 seconds
    print("DONE: ", time.strftime('%X'))



    
asyncio.run(main())
