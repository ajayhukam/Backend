from fastapi import FastAPI,Request,HTTPException,Query
from .config import DATABASE_URL,WEBHOOK_SECRET
from .storage import init_db,insert_message
from .models import WebhookMessage
from .metrics import http_requests,webhook_requests,metrics_text
from .logging_utils import log_request
import hmac,hashlib

app=FastAPI()
app.middleware("http")(log_request)

db=init_db(DATABASE_URL.replace("sqlite:///",""))

def verify_sig(body,signature):
    sig=hmac.new(WEBHOOK_SECRET.encode(),body,hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig,signature)

@app.get("/health/live")
def live(): return {"status":"ok"}

@app.get("/health/ready")
def ready():
    if not DATABASE_URL or not WEBHOOK_SECRET:
        raise HTTPException(503)
    return {"status":"ready"}

@app.post("/webhook")
async def webhook(req:Request):
    body=await req.body()
    sig=req.headers.get("X-Signature")
    if not sig or not verify_sig(body,sig):
        webhook_requests["invalid_signature"]+=1
        raise HTTPException(401,detail="invalid signature")
    data=WebhookMessage.parse_raw(body)
    res=insert_message(db,data)
    webhook_requests[res]+=1
    return {"status":"ok"}

@app.get("/messages")
def messages(limit:int=50,offset:int=0,from_:str=None,since:str=None,q:str=None):
    sql="SELECT * FROM messages WHERE 1=1"
    params=[]
    if from_:
        sql+=" AND from_msisdn=?";params.append(from_)
    if since:
        sql+=" AND ts>=?";params.append(since)
    if q:
        sql+=" AND lower(text) LIKE ?";params.append(f"%{q.lower()}%")
    cur=db.execute(sql+" ORDER BY ts ASC,message_id ASC",params)
    rows=cur.fetchall()
    total=len(rows)
    data=[{"message_id":r[0],"from":r[1],"to":r[2],"ts":r[3],"text":r[4]} for r in rows[offset:offset+limit]]
    return {"data":data,"total":total,"limit":limit,"offset":offset}

@app.get("/stats")
def stats():
    cur=db.execute("SELECT COUNT(*),COUNT(DISTINCT from_msisdn),MIN(ts),MAX(ts) FROM messages")
    t,s,f,l=cur.fetchone()
    senders=db.execute("SELECT from_msisdn,COUNT(*) FROM messages GROUP BY from_msisdn ORDER BY COUNT(*) DESC LIMIT 10").fetchall()
    return {"total_messages":t,"senders_count":s,"messages_per_sender":[{"from":x[0],"count":x[1]} for x in senders],"first_message_ts":f,"last_message_ts":l}

@app.get("/metrics")
def metrics():
    return metrics_text()
