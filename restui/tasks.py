from celery import shared_task # decorator to make asynchronous task
from celery.utils.log import get_task_logger

# this defines the core work
from restui.pipeline import bulk_upload

logger = get_task_logger(__name__)

"""
The bind argument means that the function will be a “bound method”
so that you can access attributes and methods on the task type instance.
"""
@shared_task(name="ensembl_upload", bind=True, track_started=True)
def bulk_upload_task(self, **kwargs):

    logger.info("Executing job id {0.id}".format(self.request))
    bulk_upload(self, **kwargs)
 
    # return the task id to make the polling endpoint available
    return self.request.id
