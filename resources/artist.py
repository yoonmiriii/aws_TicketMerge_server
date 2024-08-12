from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required,verify_jwt_in_request
from mysql.connector import Error
from mysql_connection import get_connection
import boto3
from config import Config
from datetime import datetime


class ArtistListResource(Resource):
    
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            user_id = None

        connection = get_connection()
        print (user_id)
        try:
            if user_id:
                query = ''' select a.id,a.name,a.url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            LEFT JOIN artistLikes l
                            on l.artistId = a.id AND l.userId = %s
                            LEFT JOIN gender g
                            on g.genderId=a.gender
                            LEFT join genre r
                            on r.id = a.genre
                            LEFT join member m
                            on m.memberId = a.member
                            limit '''+offset+''','''+limit+''';'''
                record = (user_id, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()
                cursor.close()
            else:
                query = '''select a.id,a.name,a.url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            LEFT JOIN artistLikes l
                            on l.artistId = a.id AND l.userId = Null
                            LEFT JOIN gender g
                            on g.genderId=a.gender
                            LEFT join genre r
                            on r.id = a.genre
                            LEFT join member m
                            on m.memberId = a.member
                           limit '''+offset+''','''+limit+''';'''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query)
                result_list = cursor.fetchall()
                cursor.close()

            connection.close()

            return {'result': 'success', 'items': result_list, 'count': len(result_list)}

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500  