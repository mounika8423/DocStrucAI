from flask import Flask,request
import re
import datetime
from dateutil import parser
app=Flask(__name__)
@app.route('/extract',methods=["POST"])
def extract():
    try:
        data=request.get_json()
        if data is None:
            return {"error":"Request body is missing or empty."},400
        missing_data=[]
        if "document" not in data:
            missing_data.append("document")
        if "schema" not in data:
            missing_data.append("schema")
        if missing_data:
            return {"error":f"Missing required fields:{','.join(missing_data)}"},400
        if not isinstance(data["document"], dict) or not data["document"]:
            return {"error": "'document' must be a non-empty string."}, 400
        if not isinstance(data["schema"], dict) or not data["schema"]:
            return {"error": "'schema' must be a non-empty JSON object."}, 400

    except Exception as e:
        return {"error": "Internal server error during validation."}, 500
    else:
        return data,200
    
def pre_process(data):
    for key,value in data["schema"].items():
        if value=="string":
            changed=data["document"][key].strip()
            regexed=re.sub(r'\s+',' ',changed)
            data["document"][key]=regexed
        #Known limitations for number logic : no negatives, multiple dots invalid, float("")->crash
        elif value=="number":
            numbered=str(data["document"][key])#1
            if(numbered=="" or numbered=="N/A"):
                numbered=None 
                data["document"][key]=numbered #2
            else:
                wanted="0123456789."
                for i in numbered:
                    if i not in wanted:
                        numbered=numbered.replace(i,"")
                numbered=float(numbered)
                data["document"][key]=numbered #3
        elif value=="YYYY-MM-DD":
            dateval=data["document"][key]
            try:
                final_date=parser.parse(str(dateval),fuzzy=False) #this converts string to datetime 
                data["document"][key]=final_date.strftime("%Y-%m-%d") #this converts datetime to string in desired format
            except(ValueError, TypeError):
                data["document"][key]=None
            

        
    return data

if __name__=="__main__":
    app.run(debug=True)
