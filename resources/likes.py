from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error


class LikeResource(Resource):
    @jwt_required()
    def post(self,combined_id):
        user_id=get_jwt_identity()

        type = request.args['type']

        if type == '1':
            table_name = 'concertLikes'
            column_name  ='concertId'
        elif type == '2':
            table_name = 'artistLikes'
            column_name  ='artistId'
        elif type =='3':
            table_name = 'genreLikes'
            column_name  ='genreId'
        try:
            connection = get_connection()

            query= f'''
                    insert into {table_name}
                    (userId,{column_name})
                    values
                    ({user_id},{combined_id})'''
            
            
            cursor = connection.cursor()
            cursor.execute(query,)
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
    
    @jwt_required()
    def delete(self,combined_id):
        type = request.args['type']

        if type == '1':
            table_name = 'concertLikes'
            column_name  ='concertId'
        elif type == '2':
            table_name = 'artistLikes'
            column_name  ='artistId'
        elif type =='3':
            table_name = 'genreLikes'
            column_name  ='genreId'
        else:
            return {'message': 'type 설정이 범위의 값 (1~3)인지 확인합ㄴ디ㅏ.'}, 400
        user_id=get_jwt_identity()
        try:
            connection = get_connection()

            query = f'''
                DELETE FROM `{table_name}`
                WHERE `userId` = {user_id} AND `{column_name}` = {combined_id};
            '''
            cursor = connection.cursor()
            cursor.execute(query,)
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
    

class myLikResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()

            query= '''select genre
                        from genreLikes L
                        join genre g
                        on L.genreId=g.id
                        where userId=%s
                        limit '''+offset+''','''+limit+''';'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            genre_likes = cursor.fetchall()


            query= '''select name,url
                from artistLikes L
                join artist a
                on L.artistId = a.id
                where L.userId=%s;'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            artist_likes = cursor.fetchall()
            
            query= '''select c.id,title
                    from concertLikes L
                    join concert c 
                    on L.concertId = c.id
                    where L.userId =%s;'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            concert_likes = cursor.fetchall()


            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success',
                'genreLike' : genre_likes,
                'artistLike' : artist_likes,
                'concertLike' : concert_likes}, 200
    

class mygenreLikResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()

            query= '''select genre
                        from genreLikes L
                        join genre g
                        on L.genreId=g.id
                        where userId=%s
                        limit '''+offset+''','''+limit+''';'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            genre_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success',
                'genreLike' : genre_likes}, 200
    
class myartistLikResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select a.id,name,url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            join artistLikes l
                            on a.id = l.artistId and l.userId = %s
                            join gender g
                            on a.gender = g.genderId
                            join member m 
                            on a.member = m.memberId
                            join genre r
                            on a.genre = r.id;
                limit '''+offset+''','''+limit+''';'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            artist_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success',
                'artistLike' : artist_likes, 'count': len(artist_likes)}, 200

class myconcertLikResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select c.id,title,thumbnailUrl,place,startDate,endDate,IF(L.id IS NULL, 0, 1) AS isLike
                    from concertLikes L
                    join concert c 
                    ON L.concertId = c.id AND L.userId = %s
                    limit '''+offset+''','''+limit+''';'''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            concert_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        for row in concert_likes:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

        return {'result': 'success', 'items': concert_likes, 'count': len(concert_likes)}
    






class myconcertLikResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select c.id,title,thumbnailUrl,place,startDate,endDate,IF(L.id IS NULL, 0, 1) AS isLike
                    from concertLikes L
                    join concert c 
                    ON L.concertId = c.id AND L.userId = %s
                    limit '''+offset+''','''+limit+''';'''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            concert_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        for row in concert_likes:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

        return {'result': 'success', 'items': concert_likes, 'count': len(concert_likes)}
    






class artistLikSearchResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select a.id,name,url,g.genre,d.gender,m.member,IF(L.id IS NULL, 0, 1) AS isLike
                from artistLikes L
                right join artist a
                ON L.artistId = a.id AND L.userId = %s
                join genre g
                on a.genre = g.id
                join gender d
                on d.genderId = a.gender
                join member m
                on m.memberId = a.member
                limit '''+offset+''','''+limit+''';'''
            
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            artist_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success',
                'artistLike' : artist_likes}, 200


class concertLikSearchResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        try:
            connection = get_connection()
            query= '''select c.id,title,thumbnailUrl,place,startDate,endDate,IF(L.id IS NULL, 0, 1) AS isLike
                    from concertLikes L
                    right join concert c 
                    ON L.concertId = c.id AND L.userId = %s
                    order by title
                    limit '''+offset+''','''+limit+''';'''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            concert_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        for row in concert_likes:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

        return {'result': 'success', 'items': concert_likes, 'count': len(concert_likes)}
    



class myLikeSearchResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id=get_jwt_identity()
        if 'query' not in request.args:
            return{'result':'fail',
                   'error': '검색어는 필수입니다.'}, 400
        keyword=request.args['query']
        try:
            connection = get_connection()
            query= '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,g.genre,l.location,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           join genre g
                           on g.id = c.genre
                           join location l
                           on l.id = c.location
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s OR g.genre LIKE %s OR l.location LIKE %s
                           limit '''+offset+''','''+limit+''';'''
            record = (user_id, '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            concert_likes = cursor.fetchall()

            query = '''select a.id,name,url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                        from artist a
                        join artistLikes l
                        on a.id = l.artistId and l.userId = %s
                        join gender g
                        on a.gender = g.genderId
                        join member m 
                        on a.member = m.memberId
                        join genre r
                        on a.genre = r.id
                        where name LIKE %s
                        limit '''+offset+''','''+limit+''';'''
            record = (user_id, '%{}%'.format(keyword))
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            artist_likes = cursor.fetchall()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        for row in concert_likes:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

        return {'result': 'success', 'items': concert_likes, 'count': len(concert_likes),'artist' : artist_likes}