from celery.result import AsyncResult

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CheckJobStatus(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, task_id):
        result = AsyncResult(task_id)

        # Possible task status: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED, <CUSTOM STATE>
        return Response({"status": result.status, "info": result.info})
