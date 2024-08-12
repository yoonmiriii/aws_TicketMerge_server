from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector import Error
import boto3
from config import Config
from datetime import datetime

from mysql_connection import get_connection

class PostCreateResource(Resource):

    @jwt_required()
    def post(self):
        
        # 1. 클라이언트로부터 데이터 받아오기
        title = request.form['title']
        content = request.form['content']
        types = request.args['types']
        user_id = get_jwt_identity()

        img_url = None  # 기본값으로 None 설정

        # 이미지 파일이 있을 경우 처리
        if 'image' in request.files:
            file = request.files['image']
            
            if file and 'image' in file.content_type:
                # 파일 이름을 유니크하게 만들어주기
                current_time = datetime.now()
                file_extension = file.content_type.split('/')[-1]  # 확장자 추출
                file_name = current_time.isoformat().replace(':', '_') + '_' + str(user_id) + '.' + file_extension

                client = boto3.client('s3',
                                      aws_access_key_id=Config.AWS_ACCESS_KEY,
                                      aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
                try:
                    client.upload_fileobj(file, Config.S3_BUCKET, file_name, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
                    img_url = Config.S3_URL + file_name
                except Exception as e:
                    return {'result': 'fail', 'error': str(e)}, 500

        # 3. 데이터베이스에 정보 저장하기
        try:
            connection = get_connection()
            query = '''INSERT INTO post 
                       (userId, title, type, content, imgUrl)
                       VALUES (%s, %s, %s, %s, %s);'''
            record = (user_id, title, types, content, img_url)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        
        return {"result" : "success"}

class PostReadResource(Resource):
    
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='20',)
        types = request.args.get('type', '0')
        
        if types == '0':
            types_list = list(range(1, 4))
        else:
            types_list = [int(t) for t in types.split(',')]
        types_str = ','.join(map(str, types_list))
        try:
            connection = get_connection()
            query = f'''select p.id,u.name,p.userId,p.title,t.type,p.content,p.imgUrl,p.viewCnt,p.createdAt,p.updatedAt,count(c.id) as commentCnt
                        from post p
                        left join comment c
                        on p.id = c.postId
                        join users u
                        on p.userId=u.id
                        join postType t
                        on t.id=p.type
                        WHERE p.type IN ({types_str})
                        group by p.id
                        order by createdAt desc;
                        LIMIT {offset},{limit};'''
        
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, )
            result_list = cursor.fetchall()
            cursor.close()
            connection.close()          

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        
        # 3. 결과를 json 으로 응답한다.
        i = 0
        for row in result_list:
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}
     
class PostDeleteResource(Resource):
    @jwt_required()
    def delete(self, post_id):

        print(post_id)

        user_id = get_jwt_identity()

        try:
            connection = get_connection()

            query = '''delete from postLikes
                        where  postId = %s;;'''
            record = (post_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            query = '''delete from comment
                    where  postId = %s;'''
            record = (post_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            query = '''delete from post
                    where id=%s and userId= %s;'''
            record = (post_id, user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()
            
            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        
        return {"result" : "success"}

class PostUpdateResource(Resource):

    @jwt_required()
    def put(self, post_id):
        
        title = request.form['title']
        types = request.args['types']
        content = request.form['content']

        user_id = get_jwt_identity()

        img_url = None  # 기본값으로 None 설정

        # 이미지 파일이 있을 경우 처리
        if 'image' in request.files:
            file = request.files['image']
            
            if file and 'image' in file.content_type:
                # 파일 이름을 유니크하게 만들어주기
                current_time = datetime.now()
                file_extension = file.content_type.split('/')[-1]  # 확장자 추출
                file_name = current_time.isoformat().replace(':', '_') + '_' + str(user_id) + '.' + file_extension

                client = boto3.client('s3',
                                      aws_access_key_id=Config.AWS_ACCESS_KEY,
                                      aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
                try:
                    client.upload_fileobj(file, Config.S3_BUCKET, file_name, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
                    img_url = Config.S3_URL + file_name
                except Exception as e:
                    return {'result': 'fail', 'error': str(e)}, 500


        try:
            connection = get_connection()
            query = '''update post set
                        title = %s,
                        type = %s,
                        content = %s,
                        imgUrl = %s
                        where id= %s and userId = %s;'''
            record = (title,types,content,img_url,post_id,user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
            
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500

        return {"result" : "success"}
    
class PostInformationResource(Resource):

    def get(self,post_id):
        connection = get_connection()
        try:
        
            query = '''select *
                    from post p 
                    where id = %s;'''
            
            record = (post_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            post_list = cursor.fetchone()

            query = '''
                    select c.*,u.name
                    from comment c
                    join users u
                    on c.userId = u.id
                    where postId=%s;'''
            
            record = (post_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            comment_list = cursor.fetchall()

            query = '''update post
                    set viewcnt = viewcnt +1
                    where id =%s
                    AND updatedAt =updatedAt;'''
            record = (post_id,)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            
            post_list['createdAt'] = post_list['createdAt'].isoformat()
            post_list['updatedAt'] = post_list['updatedAt'].isoformat()
            for row in comment_list:
                row['createdAt'] = row['createdAt'].isoformat()
                row['updatedAt'] = row['updatedAt'].isoformat()

            return {'result': 'success',
                    'post': post_list, 
                    'comment' : comment_list}

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        
class PostListSearchResource(Resource):
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)    
        connection = get_connection()
        if 'query' not in request.args:
            return{'result':'fail',
                   'error': '검색어는 필수입니다.'}, 400
        keyword=request.args['query']

        try:
            
            query = '''select p.id,u.name,title,t.type,p.content,imgUrl,ViewCnt,p.createdAt,p.updatedAt,count(c.content) as commentCnt
                        from post p
                        join users u
                        on p.userId = u.id
                        left join comment c
                        on p.id= c.postId
                        join postType t
                        on p.type = t.id
                        WHERE u.name LIKE %s OR p.title LIKE %s OR c.content LIKE %s OR p.content LIKE %s
                        group by p.id
                        limit '''+offset+''','''+limit+''';'''
            record = ('%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
        
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            cursor.close()
            connection.close()    

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        
        # 3. 결과를 json 으로 응답한다.
        i = 0
        for row in result_list:
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}