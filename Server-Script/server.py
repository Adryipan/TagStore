from flask import Flask,request, render_template, redirect
import requests
import json
from werkzeug.utils import secure_filename

id_token=''
access_token=''

ALLOWED_EXTENSIONS = {"jpg","jpeg"}

app = Flask(__name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploadImage", methods=["POST"])
def uploadImage():
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
        #Add the code to upload the image to the S3 budket here
	#Add code here
        return redirect("index.html")


@app.route("/searchTag", methods=["POST"])
def searchTag():
    # Take t user input, split it with comma and assign it to a list
    text = request.form["tags"]
    processed_text = text.lower()
    tagList = processed_text.split(",")
    s=''
    parm={}
    count=1
    for i in tagList:
        parm['tag{}'.format(count)]=i
        count+=1
        #if not s:
        #    s+="tag{}={}".format(count,i)
        #else:
        #    s+="&tag{}={}".format(count,i)
    objURL="https://8wl1a323h1.execute-api.us-east-1.amazonaws.com/prod/api/search"
    header={'auth':access_token}
    resp=requests.get(url=objURL,headers=header,params=parm)
    #print(resp.json())
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
    tokURL="https://fit5225-a2.auth.us-east-1.amazoncognito.com/oauth2/token"
    Data = {'grant_type':'authorization_code',
            'client_id':'26o7svq9f4d9nktrkkapicdg50',
            'redirect_uri':'https://3.209.221.168:4000',
            'code':code}
    tok=requests.post(url=tokURL,data=Data)
    res=tok.json()
    global id_token
    id_token=res['id_token']
    global access_token
    access_token=res['access_token']
    return render_template("index.html")

if __name__ == "__main__":
    app.run(ssl_context=('certificate/cert.pem', 'certificate/key.pem'), host='0.0.0.0', port=4000, threaded=True, debug=True)
