from collections import defaultdict

http_requests = defaultdict(int)
webhook_requests = defaultdict(int)

def metrics_text():
    out=[]
    for k,v in http_requests.items():
        out.append(f'http_requests_total{{path="{k[0]}",status="{k[1]}"}} {v}')
    for k,v in webhook_requests.items():
        out.append(f'webhook_requests_total{{result="{k}"}} {v}')
    return "\n".join(out)
