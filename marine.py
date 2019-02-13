import asyncio
import os
from datetime import datetime, timedelta
from marine_get import get_driver, get_from_marine
from marine_put import SQLiteBase
from distance import correction
import logging


async def _main():
    future = asyncio.Future()
    event_loop.call_soon(get_from_marine, future, driver, imo)
    data = await future

    now_timestamp = datetime.now().timestamp()
    if data[0][0] == 'not_found':
        logging.info('imo: {} - data not found'.format(imo))
        sqlite_base.set_datestamp(imo, int(now_timestamp))
        return True
    elif data[0][0] == 'error':
        logging.info('imo: {} - error occurred, imo skipped '.format(imo))
        return False
    else:
        sqlite_base.write_coordinates(data[0])
        vessel_timestamp = data[0][-1]
        old_timestamp = (datetime.now() + timedelta(days=-365)).timestamp()
        if vessel_timestamp < old_timestamp:
            sqlite_base.set_datestamp(imo, int(now_timestamp))
        else:
            lat, lon, dwt = data[0][1], data[0][2], data[1][1]
            days_to_sleep = correction(lat, lon, dwt)
            now_timestamp = (datetime.now() + timedelta(days=days_to_sleep)).timestamp()
            sqlite_base.set_datestamp(imo, int(now_timestamp), data[1])
        return True


async def _timer(time_to_sleep=10):
    await asyncio.sleep(time_to_sleep)
    storage_path = os.path.join(os.getcwd(), 'ctrl.data')
    if os.path.isfile(storage_path):
        with open(storage_path) as f:
            s = f.read()
            if s is None or s == '':
                return False
    return True


if __name__ == '__main__':

    pid = str(os.getpid())
    logging.basicConfig(
        filename=r'{0}/Data/marine.log'.format(os.getcwd()), level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('started {}'.format(pid))
    sqlite_base = SQLiteBase(os.getcwd(), 'vessels_db')
    review_from_day = (datetime.now() + timedelta(days=-7)).timestamp()
    imo_list = sqlite_base.read_imo_list(timestamp=review_from_day)
    logging.info(r'start with {0}'.format(len(imo_list)))

    driver = get_driver()
    event_loop = asyncio.get_event_loop()
    try:
        counter = 0
        for imo in imo_list:
            tasks = _main(), _timer()
            ret, run = event_loop.run_until_complete(asyncio.gather(*tasks))
            if not run:
                break
            if not ret:
                event_loop.run_until_complete(_timer(60))
                driver = get_driver()
            counter += 1
            if counter > 3000:
                break

    except Exception as err:
        logging.info(err)
        pass

    finally:
        logging.info(r'exit with {0}'.format(counter))
        for task in asyncio.Task.all_tasks():
            task.cancel()
            event_loop.run_until_complete(task)
        event_loop.close()
        driver.quit()
