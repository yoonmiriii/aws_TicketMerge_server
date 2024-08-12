from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error


class postCommentResource(Resource):
    @jwt_required()
    def post(self,post_id):
        data = request.get_json()
        user_id=get_jwt_identity()
        if data.get('comment') is None or data.get('comment').strip() =='':
            return {"result": "fail"},400
        try:
            connection = get_connection()

            query= '''
                    insert into comment 
                    (userId,postId,content)
                    values
                    (%s,%s,%s)'''
            
            record = (user_id,post_id,data['comment'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success'}, 200
    
class PostCommentDeleteResource(Resource):
    @jwt_required()
    def delete(self,comment_id):
        user_id=get_jwt_identity()
        try:
            connection = get_connection()

            query= '''delete from comment
                    where  userId = %s and id = %s;   '''
            
            record = (user_id,comment_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success'}, 200
