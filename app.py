from flask import Flask, jsonify,request
import re
from dateutil import parser
app=Flask(__name__)
@app.route('/preprocess',methods=["POST"])
def validation():
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
        pre_processed=pre_process(data)
        return pre_processed,200
    
#@app.route('/preprocess',methods=["POST"])   
def pre_process(data):
    for key,value in data["schema"].items():
        if value=="string":
            changed=data["document"][key].strip()
            regexed=re.sub(r'\s+','',changed)
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
#Preprocessing isn't up to the mark (Strict date parsing has to be done using datetime) 
        elif value=="YYYY-MM-DD":
            dateval=str(data["document"][key])
            try:
                final_date=parser.parse(dateval, fuzzy=False)
                data["document"][key]=final_date.strftime("%Y-%m-%d")
            except:
                data["document"][key]=None
        elif isinstance(value,dict):
            for k,v in value.items():
                if v=="string":
                    changed=data["document"][key][k].strip()
                    regexed=re.sub(r'\s+','',changed)
                    data["document"][key][k]=regexed
                elif v=="number":
                    numbered=str(data["document"][key][k])#1
                    if(numbered=="" or numbered=="N/A"):
                        numbered=None 
                        data["document"][key][k]=numbered #2
                    else:
                        wanted="0123456789."
                        for i in numbered:
                            if i not in wanted:
                                numbered=numbered.replace(i,"")
                        numbered=float(numbered)
                        data["document"][key][k]=numbered #3
                elif v=="YYYY-MM-DD":
                    dateval=data["document"][key][k]
                    try:
                        final_date=parser.parse(str(dateval),fuzzy=False) #this converts string to datetime 
                        data["document"][key][k]=final_date.strftime("%Y-%m-%d") #this converts datetime to string in desired format
                    except(ValueError, TypeError):
                        data["document"][key][k]=None
    return data

@app.route('/extract',methods=["POST"])
def extract():
    data=request.get_json()
    ans={}
    for i in data["required_fields"]:
        if i in data["document"].keys():
            ans[i]=data["document"].get(i)
        else:
            ans[i]=None
    return ans

if __name__=="__main__":
    app.run(debug=True)