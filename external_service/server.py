from flask import Flask,jsonify,request
app=Flask(__name__)
@app.get("/health")
def health(): return jsonify(status="ok")
@app.post("/execute")
def execute():
    x=request.get_json(force=True)
    print(f"[ExternalPaymentService] Transacción recibida: value={x.get('value')} code={x.get('code')}", flush=True)
    if float(x.get("value",0))<=0: return jsonify(approved=False),400
    return jsonify(approved=True,reference="EXT-"+str(x.get("code")))
if __name__=="__main__": app.run(host="0.0.0.0",port=5001)
