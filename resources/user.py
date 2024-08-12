from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from email_validator import EmailNotValidError,validate_email

from mysql_connection import get_connection
from utils import check_password, hash_password
from mysql.connector import Error




class UserRegisterResource(Resource):
    def post(self):
        #1. 클라이언트가 보낸 데이터를 받아준다.
        data = request.get_json()
        #2. 데이터가 모두 있는지 확인
        # if 'email' not in data or 'usrname' not in data or 'password' not in data:
        #     return {"result": "fail"},400
        # if data['email'].strip() =='' or data['username'].strip() =='' or data['password'].strip() =='':
        #     return {"result": "fail"},400
        if data.get('email') is None or data.get('email').strip() =='' or \
            data.get('name') is None or data.get('name').strip() =='' or \
            data.get('gender') is None or\
            data.get('password') is None or data.get('password').strip() =='' :
            return {"result": "fail"},400
        # 3. 비밀번호가 비어 있는지 확인
        #3. 이메일 주소 형식이 올바른지 확인한다.

        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return{'result' : 'fail' , 'error' : str(e)},400
        

        #4. 비밀번호 길이가 유효한지 체크한다.
        if not 4 <= len(data['password']) <=12 :
            return {"result": "fail"},401
        #   예) 비번은 4자링 이상 12자리 이하

        #5. 비밀번호를 암호화 한다.
        passwrod = hash_password(data['password'])
        print(passwrod)

        #6. db에 저장한다.
        try: 
            connection = get_connection()
            query = '''insert into users
                    (name, email, password, gender)
                    values
                    (%s,%s,%s,%s);'''
            record = (data['name'],data['email'],passwrod,data['gender'])
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            ###DB에 회원가입하여, user 테이블에 insert된 후 , 
            ### 이 user 테이블의 id 값을 가져와야 한다.
            user_id=cursor.lastrowid

            cursor.close()
            connection.close()
            
        except Error as e:
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result': 'fail','error': str(e)}, 501
        #6-2. user_id 를 바로 클라이언트에게 보내면 안되고, 
        ## JWT 로 암호화 해서, 인증토큰을 보내야한다.
        access_token = create_access_token(user_id)
        # 토큰 기간정하기
        # access_token=create_access_token(user_id,expires_delta=datetime.timedelta(minutes=3))
        #7. 응답할 테이터를 json으로 만들어서 리턴.
        return {"result": "success",'accessToken' : access_token}


class UserLoginResource(Resource) :
    def post(self) :
        
        # 1. 클라이언트로부터 데이터를 받는다.
        data = request.get_json()

        if 'email' not in data or 'password' not in data:
            return {'result' : 'fail'}, 400
        if data['email'].strip() == '' or data['password'].strip() == '':  
            return {'result' : 'fail'}, 400
        # 2. DB로부터 이메일에 해당하는 유저 정보를 가져온다.
        try :
            connection = get_connection()
            query = '''select *
                        from users
                        where email = %s ;'''
            record = ( data['email'] ,  )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result':'fail', 'error':str(e)},500

        # 3. 회원인지 확인한다.
        if result_list == [] :
            return {'result' : 'fail'} , 401

        # 4. 비밀번호를 체크한다.
        # 유저가 입력한 비번 data['password']
        # DB에 암호화된 비번 result_list[0]['password']
        isCorrect = check_password(data['password'] , result_list[0]['password'])
        if isCorrect == False :
            return {'result' : 'fail'} , 401

        # 5. 유저아이디를 가져온다.
        user_id = result_list[0]['id']

        # 6. JWT 토큰을 만든다.
        # access_token = create_access_token(user_id,
        #                                    expires_delta= datetime.timedelta(minutes=3))
        access_token = create_access_token(user_id)
        # 7. 클라이언트에 응답한다.

        return {'result' : 'success', 'accessToken':access_token}



# 로그아웃된 토큰을 저장할, set 을 만든다. 
jwt_blacklist = set()

class UserLogoutResource(Resource) :

    @jwt_required()
    def delete(self):

        jti = get_jwt()['jti']
        jwt_blacklist.add(jti)
        return {'result' : 'success'}

class myinfoResource(Resource):
    @jwt_required()

    def get(self):
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select id,name,email
                    from users
                    where id = %s;'''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result = cursor.fetchall()
            cursor.close()
            connection.close()
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        return {'result': 'success', 'items': result}
