import json,uuid,time
from datetime import datetime

async def log_request(request,call_next):
    rid=str(uuid.uuid4())
    start=time.time()
    response=await call_next(request)
    latency=round((time.time()-start)*1000,2)
    print(json.dumps({
        "ts":datetime.utcnow().isoformat()+"Z",
        "level":"INFO",
        "request_id":rid,
        "method":request.method,
        "path":request.url.path,
        "status":response.status_code,
        "latency_ms":latency
    }))
    return response
