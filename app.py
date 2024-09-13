from datetime import datetime
from itertools import count

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, jsonify, request
from sqlalchemy import Column, String, Integer, Date

from model import Student, db, AiTeacher, Picture

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from SDimg2img import generate_image

#配置讯飞模型
#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v4.0/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = '7070c464'
SPARKAI_API_SECRET = 'OGY0ZTVmMThlMmUyY2RiZWJhMjQ5ZWRm'
SPARKAI_API_KEY = 'c563b03287f44abb8bb194a123fd1d4e'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = '4.0Ultra'
app = Flask(__name__)
#解决跨域请求问题
CORS(app)

# 配置数据库连接
USERNAME = 'root'
PASSWORD = '123456'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'stuinfo'

#配置app config
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
app.config['SQLALCHEMY_ECHO'] = True

#将数据库与flask连接
db.init_app(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

#api接口的
#TODO：都需要把最后的返回的东西包装成对象{status： ，message： ，data：}的形式
# class ReturnClass:
#     def __init__(self, status, message , data):
#         self.status = status
#         self.message = message
#         self.data = data
@app.route('/api/getExamplePic',methods=['GET'])
def getExamplePic():
    students = Student.query.all()  # 查询所有学生
    student_snos = [student.sno for student in students]
    # response_object = ReturnClass(status=200, message="success", data=student_snos)
    return jsonify({
        "status": 200,
        "message": "success",
        "data": student_snos
    })

@app.route('/user/historyPlan/{id}',methods=['GET'])
def getHistoryPlan(id):
    plans = AiTeacher.query.filter_by(userId=id).all()
    return jsonify({
        "status": 200,
        "message": "success",
        "data": {
            "count": len(plans),
            "list": [{"date":plan.time,"plan":plan.plan} for plan in plans]
        }
    })

@app.route('/user/historyPicture/{id}',methods=['GET'])
def getHistoryPicture(id):
    pictures = Picture.query.filter_by(userId=id).all()
    return jsonify({
        "status": 200,
        "message": "success",
        "data": {
            "count": len(pictures),
            "list": [{"date": picture.time, "url": picture.url} for picture in pictures]
        }
    })
def parse_llm_result(llm_result):
    texts = []
    if llm_result.generations:
        for generation in llm_result.generations:
            for item in generation:
                texts.append(item.text)
    return texts

def insert_plan(time, plan, user_id):
    new_plan = AiTeacher(time=time, plan=plan, userId=user_id)
    db.session.add(new_plan)
    db.session.commit()
    print("数据插入成功!")

def insert_aiPicture(time, url, user_id):
    new_picture = Picture(time=time, url=url, userId=user_id)
    db.session.add(new_picture)
    db.session.commit()
    print("数据插入成功!")
@app.route('/api/aiPlan',methods=['POST'])
def getAIPlan():
    text_content = request.json.get('text')
    userId = request.json.get('userId')
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content=text_content
    )]
    handler = ChunkPrintHandler()
    aiPlan = spark.generate([messages], callbacks=[handler])
    plan = parse_llm_result(aiPlan)
    print(plan)
    insert_plan(datetime.now(),plan,userId)
    return jsonify({
        "status": 200,
        "message": "success",
        "data": {
            "plan": plan
        }
    })

OUTPUT_DIR = "generated_images"
@app.route('/api/aiPS',methods=['POST'])
def getAIPS():
    pic_url = request.form.get('url')
    userId = request.json.get('userId')
    print(pic_url)
    if not pic_url:
        return jsonify(
            {
                "status": 400,
                "message": "error",
                "data": {
                    "error": "No image path provided"
                }
            })

    result, status_code = generate_image(pic_url, OUTPUT_DIR)
    if status_code == 200:
        insert_aiPicture(datetime.now(),result['url'],userId)
        message = "success"
    else:
        message = "error"
    return jsonify(
        {
            "status": status_code,
            "message": message,
            "data": result
        })

if __name__ == '__main__':
    app.run()

