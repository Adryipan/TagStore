from flask import Flask,request, render_template, redirect,flash
import os
import requests
import json
from werkzeug.utils import secure_filename
import boto3

id_token=''
access_token=''
UPLOAD_FOLDER = "upload-pics"

ALLOWED_EXTENSIONS = {"jpg","jpeg"}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploadImage", methods=["GET","POST"])
def uploadImage():
    if request.method == "POST":
        if not id_token:
            return "Invalid Request"
        else:
            # If the post request has the file
            if "image" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["image"]
            # if the user does not select a file
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                
                cogclient=boto3.client('cognito-identity',region_name='us-east-1')
                
                idp='cognito-idp.us-east-1.amazonaws.com/us-east-1_uAsw8dIiE'
                resp=cogclient.get_id(IdentityPoolId='us-east-1:4cfe525a-4f51-4b06-887e-7f0865514061',Logins={idp:id_token})
                identityID=resp['IdentityId']
                
                resp2=cogclient.get_credentials_for_identity(IdentityId=identityID,Logins={idp:id_token})
                acki=resp2['Credentials']['AccessKeyId']
                asak=resp2['Credentials']['SecretKey']
                ast=resp2['Credentials']['SessionToken']


                cogsess=boto3.Session(aws_access_key_id=acki,aws_secret_access_key=asak,aws_session_token=ast,region_name='us-east-1')
                clt=cogsess.client('s3',region_name='us-east-1')
                clt.upload_file(UPLOAD_FOLDER + "/" + filename,'fit5225-tagstore-upload-bucket',filename,ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
                os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return render_template("index.html")


@app.route("/searchTag", methods=["POST"])
def searchTag():
    # Take t user input, split it with comma and assign it to a list
    if not access_token:
        return "Invalid Request"
    else:
        text = request.form["tags"]
        processed_text = text.lower()
        tagList = processed_text.split(",")
        s=''
        parm={}
        count=1
        for i in tagList:
            parm['tag{}'.format(count)]=i
            count+=1
        objURL="https://wpbms48c06.execute-api.us-east-1.amazonaws.com/prod/api/search"
        header={'auth':access_token}
        resp=requests.get(url=objURL,headers=header,params=parm)
        objSTRING=[]
        count1=1
        for i in resp.json():
            objSTRING.append(i['url{}'.format(count1)])
            count1+=1
        JSON={'url':str(objSTRING)}
        return JSON
    
@app.route("/getHomeTemp", methods=["GET"])
def getHomeTemp():
    return render_template("index.html")

@app.route("/getSearchTemp", methods=["GET"])
def getSearchTemplate():
    return render_template("searchImage.html")

@app.route("/getUploadTemp", methods=["GET"])
def getUploadTemplate():
    return render_template("uploadImage.html")


@app.route("/")
def hello():
    code=request.args.get('code')
    if code:
        tokURL="https://fit5225-domain.auth.us-east-1.amazoncognito.com/oauth2/token"
        Data = {'grant_type':'authorization_code',
                'client_id':'5495h8gtqjm9cvm8sr05isfh5e',
                'redirect_uri':'https://174.129.206.198:4000',
                'code':code}
        tok=requests.post(url=tokURL,data=Data)
        if tok.ok:
            res=tok.json()
            global id_token
            id_token=res['id_token']
            global access_token
            access_token=res['access_token']
            return render_template("index.html")
        else:
            return "Invalid Code"
    else:
        return "Invalid Request"

if __name__ == "__main__":
    app.secret_key=os.urandom(24)
    app.run(ssl_context=('certificate/cert.pem', 'certificate/key.pem'), host='0.0.0.0', port=4000, threaded=True, debug=True)
