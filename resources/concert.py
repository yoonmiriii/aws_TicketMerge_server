from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required,verify_jwt_in_request
from mysql.connector import Error
from mysql_connection import get_connection
import boto3
from config import Config
from datetime import datetime
class ConcertListResource(Resource):
    
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
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           order by endDate desc
                           limit '''+offset+''','''+limit+''';'''
                record = (user_id, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()
                cursor.close()
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId IS NULL
                           order by endDate desc
                           limit '''+offset+''','''+limit+''';'''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query)
                result_list = cursor.fetchall()
                cursor.close()

            connection.close()

            # Format dates to ISO format
            for row in result_list:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

            return {'result': 'success', 'items': result_list, 'count': len(result_list)}

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500  
    
class ConcertListViewSortResource(Resource):
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
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                            order by viewCnt desc
                            limit '''+offset+''','''+limit+''';'''
                record = (user_id, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()
                cursor.close()
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId IS NULL
                            order by viewCnt desc
                            limit '''+offset+''','''+limit+''';'''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query)
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
            result_list[i]['startDate'] = row['startDate'].isoformat()
            result_list[i]['endDate'] = row['endDate'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}
    
    
class ConcertInformationResource(Resource):
    
    def get(self,concert_id):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            user_id = None

        connection = get_connection()
        print (user_id)
        try:
            if user_id:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           where c.id=%s;'''
                
                record = (user_id,concert_id )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchone()

                
                result_list['startDate'] = result_list['startDate'].isoformat()
                result_list['endDate'] = result_list['endDate'].isoformat()

                connection = get_connection()
                query = '''update concert
                        set viewcnt = viewcnt +1
                        where id =%s;'''
                record = (concert_id,)
                cursor = connection.cursor()
                cursor.execute(query, record)
                connection.commit()

                casting_list = result_list['castingList']
                print(casting_list)
                artist_list =[]
                if not casting_list or casting_list == ['']:
                    return {'result': 'success', 'concert': result_list}
                    
                else:
                    if isinstance(casting_list, list):
                        artists = casting_list
                        print(artists)
                    else:
                        # 그렇지 않다면, split(', ')을 사용하여 문자열을 리스트로 변환합니다.
                        artists = [artist.strip() for artist in casting_list.split(',')]  # Assuming the casting list is a comma-separated string
                        print(artists)
                    for artist in artists:
                        print(artist)
                        query = '''SELECT distinct a.name,a.id,a.url,g.genre,m.member,IF(L.id IS NULL, 0, 1) AS isLike
                            FROM artist a
                            join genre g
                                on a.genre = g.id
                            left join member m
                                on a.member = m.memberId
                            LEFT join artistLikes L
                            ON a.id = L.artistId AND L.userId = %s
                                WHERE name LIKE %s;'''
                        record = [user_id, f"{artist}%"]
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query,record)
                        artist_info = cursor.fetchall()
                        artist_list.extend(artist_info)  # Flattening the list
                            
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = Null
                           where c.id=%s;'''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query,(concert_id,))
                result_list = cursor.fetchone()

                result_list['startDate'] = result_list['startDate'].isoformat()
                result_list['endDate'] = result_list['endDate'].isoformat()


                connection = get_connection()
                query = '''update concert
                        set viewcnt = viewcnt +1
                        where id =%s;'''
                record = (concert_id,)
                cursor = connection.cursor()
                cursor.execute(query, record)
                connection.commit()

                casting_list = result_list['castingList']
                print(casting_list)
                artist_list =[]
                if not casting_list or casting_list == ['']:
                    return {'result': 'success', 'concert': result_list}
                    
                else:
                    if isinstance(casting_list, list):
                        artists = casting_list
                    else:
                        # 그렇지 않다면, split(', ')을 사용하여 문자열을 리스트로 변환합니다.
                        artists = [artist.strip() for artist in casting_list.split(',')]  # Assuming the casting list is a comma-separated string
                        print(artists)
                        for artist in artists:
                            print(artist)
                            query = '''SELECT distinct a.name,a.id,a.url,g.genre,m.member,IF(L.id IS NULL, 0, 1) AS isLike
                                FROM artist a
                                join genre g
                                    on a.genre = g.id
                                left join member m
                                    on a.member = m.memberId
								LEFT join artistLikes L
                                ON a.id = L.artistId AND L.userId = Null
                                    WHERE name LIKE %s;'''
                            cursor = connection.cursor(dictionary=True)
                            cursor.execute(query, (f"{artist}",))
                            artist_info = cursor.fetchall()
                            artist_list.extend(artist_info)  # Flattening the list
                

            cursor.close()
            connection.close()

            
        



            return {'result': 'success', 'concert': result_list, 'artist' : artist_list}

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        

class ConcertListSearchResource(Resource):
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()

        print (user_id)
        
        if 'query' not in request.args:
            return{'result':'fail',
                   'error': '검색어는 필수입니다.'}, 400
        keyword=request.args['query']

        try:
            if user_id:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,g.genre,l.location,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           join genre g
                           on g.id = c.genre
                           join location l
                           on l.id = c.location
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s OR g.genre LIKE %s OR l.location LIKE %s
                           limit '''+offset+''','''+limit+''';'''
                record = (user_id, '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()

                query = '''select a.id,name,url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            left join artistLikes l
                            on a.id = l.artistId and l.userId = %s
                            join gender g
                            on a.gender = g.genderId
                            join member m 
                            on a.member = m.memberId
                            join genre r
                            on a.genre = r.id
                            where name like %s;'''
                record = (user_id,'%{}%'.format(keyword),)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                artist_list = cursor.fetchall()
                if not result_list:
                    try:
                        query = '''select l.userId
                                from artistLikes l
                                join artist a
                                on l.artistId = a.id
                                where a.name like %s;'''
                        record = ('%{}%'.format(keyword),)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query, record)
                        user_list = cursor.fetchall()
                        users = [user['userId'] for user in user_list] 
                        users_list = ','.join(map(str, users))
                        
                        if not users_list:
                            return {'result' : 'success',
                                'comment' :keyword+'에 대한 정보가 없습니다.'}

                        query = f'''SELECT title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,viewCnt,COUNT(l.userId) AS likeCnt,IF(l2.id IS NULL, 0, 1) AS isLike
                                    FROM concert c
                                    LEFT JOIN concertLikes l 
                                    ON l.concertId = c.id
                                    LEFT JOIN (SELECT concertId, id FROM concertLikes WHERE userId ={user_id}) l2 ON l2.concertId = c.id
                                
                                    WHERE l.userId IN ({users_list})
                                    GROUP BY c.id
                                    ORDER BY likeCnt DESC
                                    limit '''+offset+''','''+limit+''';'''
                        print(query)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query,)
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
                    i = 0
                    for row in result_list:
                        result_list[i]['startDate'] = row['startDate'].isoformat()
                        result_list[i]['endDate'] = row['endDate'].isoformat()
                        i = i + 1

                    return {'result' : 'success',
                    'comment' :'현재 공연이 없습니다.'+keyword+' 을 좋아하는 가수로 선택하신 분들의 좋아하시는 콘서트 목록입니다.',
                    'items' : result_list,
                    'count' : len(result_list),
                    'artist' : artist_list,
                    'artistCount':len(artist_list)}
                    
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,g.genre,l.location,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = Null
                           join genre g
                           on g.id = c.genre
                           join location l
                           on l.id = c.location
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s OR g.genre LIKE %s OR l.location LIKE %s
                           limit '''+offset+''','''+limit+''';'''
                record = ('%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()

                query = '''select a.id,name,url,g.gender,m.member,r.genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            left join artistLikes l
                            on a.id = l.artistId and l.userId = Null
                            join gender g
                            on a.gender = g.genderId
                            join member m 
                            on a.member = m.memberId
                            join genre r
                            on a.genre = r.id
                            where name like %s;'''
                record = ('%{}%'.format(keyword),)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                artist_list = cursor.fetchall()
                if not result_list:
                    try:
                        query = '''select l.userId
                                from artistLikes l
                                join artist a
                                on l.artistId = a.id
                                where a.name like %s;'''
                        record = ('%{}%'.format(keyword),)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query, record)
                        user_list = cursor.fetchall()
                        users = [user['userId'] for user in user_list] 
                        users_list = ','.join(map(str, users))
                        
                        if not users_list:
                            return {'result' : 'success',
                                'comment' :keyword+'에 대한 정보가 없습니다.'}

                        query = f'''SELECT title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,viewCnt,COUNT(l.userId) AS likeCnt,IF(l2.id IS NULL, 0, 1) AS isLike
                                    FROM concert c
                                    LEFT JOIN concertLikes l 
                                    ON l.concertId = c.id
                                    LEFT JOIN (SELECT concertId, id FROM concertLikes WHERE userId = Null) l2 ON l2.concertId = c.id
                                
                                    WHERE l.userId IN ({users_list})
                                    GROUP BY c.id
                                    ORDER BY likeCnt DESC
                                    limit '''+offset+''','''+limit+''';'''
                        print(query)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query,)
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
                    
                    i = 0
                    for row in result_list:
                        result_list[i]['startDate'] = row['startDate'].isoformat()
                        result_list[i]['endDate'] = row['endDate'].isoformat()
                        i = i + 1

                    return {'result' : 'success',
                    'comment' :'현재 공연이 없습니다.'+keyword+' 을 좋아하는 가수로 선택하신 분들의 좋아하시는 콘서트 목록입니다.',
                    'items' : result_list,
                    'count' : len(result_list),
                    'artist' : artist_list,
                    'artistCount':len(artist_list)}



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
            result_list[i]['startDate'] = row['startDate'].isoformat()
            result_list[i]['endDate'] = row['endDate'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'comment' : keyword + ' 에 대한 검색 정보입니다.',
                'items' : result_list,
                'count' : len(result_list),
                'artist' : artist_list,
                'artistCount':len(artist_list)}

    

class ConcertListMainResource(Resource):
    
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        try:
            type = request.args.get('type', '1')
            genre = request.args.get('genre', '0')
            sort = request.args.get('sort', '1')
            place = request.args.get('place', '0')

            if sort == '1':
                sort = 'likeCnt DESC'
            elif sort == '2':
                sort = 'viewCnt DESC'
            elif sort =='3':
                sort = 'endDate'
            
        except:
            pass
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            user_id = None
        # viewCnt desc
        connection = get_connection()
        try:
            if user_id:
                if type == '1':
                    if genre == '0':
                        genre_list = list(range(1, 8))
                    else :
                        genre_list = [int(t) for t in genre.split(',')]
                    genre_str = ','.join(map(str, genre_list))
                    query = f'''
                    SELECT title,c.id,thumbnailUrl,contentUrl,place,c.genre,c.location,l.location,g.genre,startDate,endDate,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike,count(k.concertId) as likeCnt
                    from concert c
                                LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = {user_id}
                    join location l
                                on c.location = l.id
                                join genre g
                                on c.genre =g.id
                                left join concertLikes k
                                on c.id = k.concertId
                    where c.genre In ({genre_str})
                    GROUP BY c.id
                    ORDER BY {sort}
                    LIMIT {offset},{limit};
                    '''
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query,)
                    result_list = cursor.fetchall()
                    cursor.close()
                elif type =='2':
                    if place == '0':
                        place_list = list(range(1, 18))
                    else :
                        place_list = [int(t) for t in place.split(',')]
                    place_str = ','.join(map(str, place_list))
                    query =f'''
                    SELECT title,c.id,thumbnailUrl,contentUrl,place,c.genre,c.location,l.location,g.genre,startDate,endDate,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike,count(k.concertId) as likeCnt
                    from concert c
                                LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = {user_id}
                    join location l
                                on c.location = l.id
                                join genre g
                                on c.genre =g.id
                                left join concertLikes k
                                on c.id = k.concertId
                    where c.location In ({place_str})
                    GROUP BY c.id
                    ORDER BY {sort}
                    LIMIT {offset},{limit};
                    '''
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query,)
                    result_list = cursor.fetchall()
                    cursor.close()
                    

            else:
                if type == '1':
                    if genre == '0':
                        genre_list = list(range(1, 8))
                    else :
                        genre_list = [int(t) for t in genre.split(',')]
                    genre_str = ','.join(map(str, genre_list))
                    query = f'''
                    SELECT title,c.id,thumbnailUrl,contentUrl,place,c.genre,c.location,l.location,g.genre,startDate,endDate,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike,count(k.concertId) as likeCnt
                    from concert c
                                LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = Null
                    join location l
                                on c.location = l.id
                                join genre g
                                on c.genre =g.id
                                left join concertLikes k
                                on c.id = k.concertId
                    where c.genre In ({genre_str})
                    GROUP BY c.id
                    ORDER BY {sort}
                    LIMIT {offset},{limit};
                    '''
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query,)
                    result_list = cursor.fetchall()
                    cursor.close()
                elif type =='2':
                    if place == '0':
                        place_list = list(range(1, 18))
                    else :
                        place_list = [int(t) for t in place.split(',')]
                    place_str = ','.join(map(str, place_list))
                    query =f'''
                    SELECT title,c.id,thumbnailUrl,contentUrl,place,c.genre,c.location,l.location,g.genre,startDate,endDate,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike,count(k.concertId) as likeCnt
                                from concert c
                                LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = Null
                                join location l
                                on c.location = l.id
                                join genre g
                                on c.genre =g.id
                                left join concertLikes k
                                on c.id = k.concertId
                                where c.location In ({place_str})
                                GROUP BY c.id
                                ORDER BY {sort}
                                LIMIT {offset},{limit};'''
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query,)
                    result_list = cursor.fetchall()
                    cursor.close()

            connection.close()

            # Format dates to ISO format
            for row in result_list:
                row['startDate'] = row['startDate'].isoformat()
                row['endDate'] = row['endDate'].isoformat()

            return {'result': 'success', 'items': result_list, 'count': len(result_list)}

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500
        












class ConcertListSearch2Resource(Resource):
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()

        print (user_id)
        
        if 'query' not in request.args:
            return{'result':'fail',
                   'error': '검색어는 필수입니다.'}, 400
        keyword=request.args['query']

        try:
            if user_id:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s
                           limit '''+offset+''','''+limit+''';'''
                record = (user_id, '%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId is Null
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s
                           limit '''+offset+''','''+limit+''';'''
                record = ('%{}%'.format(keyword), '%{}%'.format(keyword), '%{}%'.format(keyword))
            
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
            result_list[i]['startDate'] = row['startDate'].isoformat()
            result_list[i]['endDate'] = row['endDate'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}
    





from PIL import Image
from io import BytesIO
class ConcertListImageSearchResourc(Resource):
    def post(self):
        if 'photo' not in request.files:
            return {'result': 'fail', 'error': '사진은 필수입니다.'}

        file = request.files['photo']
        if not file or file.filename == '':
            return {'result': 'fail', 'error': '이미지 파일을 업로드하세요.'}, 400
            
        # 파일 유형 확인 및 jfif 파일 지원 추가
        allowed_extensions = {'jpg', 'jpeg', 'png', 'jfif', 'webp'}
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return {'result': 'fail', 'error': '지원하지 않는 파일 형식입니다.'}, 400

        current_time = datetime.now()
        file_name = current_time.isoformat().replace(':', '_') + '.jpg'

        # PIL을 사용하여 이미지 포맷 변환 (jfif -> jpg)
        image = Image.open(file)
        if image.format == 'JPEG':
            file_format = 'jpeg'
        elif image.format == 'JFIF':
            file_format = 'jpeg'
        else:
            file_format = 'png'  # 다른 형식의 경우 png로 변환하거나 처리할 수 있음

        # 파일을 BytesIO로 변환하여 업로드
        file_stream = BytesIO()
        image.save(file_stream, format=file_format)
        file_stream.seek(0)

        # S3에 이미지 파일 업로드
        client = boto3.client('s3',
                                aws_access_key_id=Config.AWS_ACCESS_KEY,
                                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
        client.upload_fileobj(file_stream, Config.S3_BUCKET, file_name, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})

        # 얼굴 인식 호출
        response = self.recognize_celebrities(file_name, Config.S3_BUCKET)
        try:
            celebrity_names = [celebrity['Name'] for celebrity in response.get('CelebrityFaces', [])]
            label_str = ','.join(celebrity_names)
            label_str = self.translate(label_str)
        except Exception as e:
            return {'result': 'success', 'comment': '검색하신 이미지에 대한 정보가 없습니다.'}
        

    
    
        

        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except:
            user_id = None

        connection = get_connection()
        print (user_id)
        try:
            if user_id:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = %s
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s;'''
                record = (user_id, '%{}%'.format(label_str), '%{}%'.format(label_str), '%{}%'.format(label_str))
                print(query)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()

                query = '''select a.id,name,url,gender,member,genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            left join artistLikes l
                            on a.id = l.artistId and l.userId = %s
                            where name like %s;'''
                record = (user_id,'%{}%'.format(label_str),)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                artist_list = cursor.fetchall()
            
                if not result_list:
                    try:
                        query = '''select l.userId
                                from artistLikes l
                                join artist a
                                on l.artistId = a.id
                                where a.name like %s;'''
                        record = ('%{}%'.format(label_str),)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query, record)
                        user_list = cursor.fetchall()
                        users = [user['userId'] for user in user_list] 
                        users_list = ','.join(map(str, users))
                        
                        if not users_list:
                            return {'result' : 'success',
                                'comment' :'검색 하신 이미지 '+label_str+'에 대한 정보가 없습니다.'}

                        query = f'''SELECT title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,viewCnt,COUNT(l.userId) AS likeCnt,IF(l2.id IS NULL, 0, 1) AS isLike
                                    FROM concert c
                                    LEFT JOIN concertLikes l 
                                    ON l.concertId = c.id
                                    LEFT JOIN (SELECT concertId, id FROM concertLikes WHERE userId = {user_id}) l2 ON l2.concertId = c.id
                                    WHERE l.userId IN ({users_list})
                                    GROUP BY c.id
                                    ORDER BY likeCnt DESC;'''
                        print(query)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query,)
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
                    i = 0
                    for row in result_list:
                        result_list[i]['startDate'] = row['startDate'].isoformat()
                        result_list[i]['endDate'] = row['endDate'].isoformat()
                        i = i + 1

                    return {'result' : 'success',
                    'comment' :'현재 공연이 없습니다.'+label_str+' 을 좋아하는 가수로 선택하신 분들의 좋아하시는 콘서트 목록입니다.',
                    'items' : result_list,
                    'count' : len(result_list)}
                    
            else:
                query = '''SELECT distinct title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,castingList,url,viewCnt,IF(L.id IS NULL, 0, 1) AS isLike
                           FROM concert c
                           LEFT JOIN concertLikes L ON L.concertId = c.id AND L.userId = Null
                           WHERE title LIKE %s OR place LIKE %s OR castingList LIKE %s;'''
                record = ('%{}%'.format(label_str), '%{}%'.format(label_str), '%{}%'.format(label_str))
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()

                query = '''select a.id,name,url,gender,member,genre,IF(l.id IS NULL, 0, 1) AS isLike
                            from artist a
                            left join artistLikes l
                            on a.id = l.artistId and l.userId = Null
                            where name like %s;'''
                record = ('%{}%'.format(label_str),)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                artist_list = cursor.fetchall()
                if not result_list:
                    try:
                        query = '''select l.userId
                                from artistLikes l
                                join artist a
                                on l.artistId = a.id
                                where a.name like %s;'''
                        record = ('%{}%'.format(label_str),)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query, record)
                        user_list = cursor.fetchall()
                        users = [user['userId'] for user in user_list] 
                        users_list = ','.join(map(str, users))
                        
                        if not users_list:
                            return {'result' : 'success',
                                'comment' :label_str+'에 대한 정보가 없습니다.'}

                        query = f'''SELECT title,c.id,thumbnailUrl,contentUrl,place,startDate,endDate,castingList,url,viewCnt,COUNT(l.userId) AS likeCnt,IF(l2.id IS NULL, 0, 1) AS isLike
                                    FROM concert c
                                    LEFT JOIN concertLikes l 
                                    ON l.concertId = c.id
                                    LEFT JOIN (SELECT concertId, id FROM concertLikes WHERE userId = Null) l2 ON l2.concertId = c.id
                                    WHERE l.userId IN ({users_list})
                                    GROUP BY c.id
                                    ORDER BY likeCnt DESC;'''
                        print(query)
                    
                        cursor = connection.cursor(dictionary=True)
                        cursor.execute(query,)
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
                    
                    i = 0
                    for row in result_list:
                        result_list[i]['startDate'] = row['startDate'].isoformat()
                        result_list[i]['endDate'] = row['endDate'].isoformat()
                        i = i + 1

                    return {'result' : 'success',
                    'comment' :'현재 공연이 없습니다.'+label_str+' 을 좋아하는 가수로 선택하신 분들의 좋아하시는 콘서트 목록입니다.',
                    'items' : result_list,
                    'count' : len(result_list)}
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {"result" : "fail", 
                    "error" : str(e)}, 500





        i = 0
        for row in result_list:
            result_list[i]['startDate'] = row['startDate'].isoformat()
            result_list[i]['endDate'] = row['endDate'].isoformat()
            i = i + 1

        return {'result' : 'success',
                'comment' : '검색하신 이미지는 '+label_str + ' 입니다.' +label_str + ' 에 대한 검색 정보입니다.',
                'items' : result_list,
                'count' : len(result_list),
                'artist' : artist_list,
                'artistCount':len(artist_list),
                'imageName':label_str}


    def recognize_celebrities(self, photo, bucket):
        client = boto3.client('rekognition', 'ap-northeast-2',
                              aws_access_key_id=Config.AWS_ACCESS_KEY,
                              aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
    



    def recognize_celebrities(self, photo, bucket):
        client = boto3.client('rekognition', 'ap-northeast-2',
                              aws_access_key_id=Config.AWS_ACCESS_KEY,
                              aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)

        try:
            # S3에 업로드된 이미지를 직접 읽어옴
            response = client.recognize_celebrities(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

            celebrity_list = []
            for celebrity in response['CelebrityFaces']:
                celebrity_info = {
                    'Name': celebrity['Name'],
                    'Id': celebrity['Id'],
                    'KnownGender': celebrity['KnownGender']['Type'],
                    'Smile': celebrity['Face']['Smile']['Value'],
                    'Position': {
                        'Left': '{:.2f}'.format(celebrity['Face']['BoundingBox']['Height']),
                        'Top': '{:.2f}'.format(celebrity['Face']['BoundingBox']['Top'])
                    },
                    'Info': celebrity['Urls']
                }
                celebrity_list.append(celebrity_info)

            return response

        except Exception as e:
            raise Exception(f"얼굴 인식 실패: {str(e)}")
        

    def translate(self,text):
        client = boto3.client(service_name='translate', 
                              region_name='ap-northeast-2',
                              aws_access_key_id = Config.AWS_TRANSLATE_KEY,
                              aws_secret_access_key = Config.AWS_SECRET_TRASLATE_KEY)

        result = client.translate_text(Text=text, 
                    SourceLanguageCode="en", TargetLanguageCode="ko")
        print('TranslatedText: ' + result.get('TranslatedText'))
        print('SourceLanguageCode: ' + result.get('SourceLanguageCode'))
        print('TargetLanguageCode: ' + result.get('TargetLanguageCode'))
        return result.get('TranslatedText')