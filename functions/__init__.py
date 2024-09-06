import logging
import azure.functions as func
from functions.my_chrono_module import run_update  # Import the function from your script

app = func.FunctionApp()
@app.schedule(schedule="0 0 * * 2,5", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def func_chrono_db_update(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    try:
        # Call the function to run the database update
        run_update()
        logging.info('Database update completed successfully.')
    except Exception as e:
        logging.error(f"An error occurred during the database update: {e}")