from app.core.logging_config import logger
from app.core.middleware import get_correlation_id

def send_booking_confirmation(candidate_email: str, job_title: str, start_time, end_time):
    logger.info(
        f"[{get_correlation_id()}] EMAIL SENT | type=booking_confirmation | "
        f"to={candidate_email} | job={job_title} | "
        f"start={start_time} | end={end_time}"
    )
    # SMTP when in prod
    print(f"""
          -----------------------------------------------
          TO: {candidate_email}
          SUBJECT: Interview Confirmed - {job_title}
          
          Your interview has been scheduled.
          Job: {job_title}
          Time: {start_time} to {end_time}
          Good luck!
          -----------------------------------------------
          """)
    
def send_cancellation_notice(candidate_email: str, job_title: str, start_time):
    logger.info(
        f"[{get_correlation_id()}] EMAIL SENT | type=cancellation_notice | "
        f"to={candidate_email} | job={job_title} | "
        f"start={start_time}" 
    )
    # SMTP when in prod
    print(f"""
    -----------------------------------------------
    TO: {candidate_email}
    SUBJECT: Interview Cancelled — {job_title}
    
    Your interview has been cancelled.
    Job: {job_title}
    Scheduled time was: {start_time}
    -----------------------------------------------
    """)   