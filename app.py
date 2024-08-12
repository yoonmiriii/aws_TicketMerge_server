import serverless_wsgi

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.user import jwt_blacklist


from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource,myinfoResource
from resources.concert import ConcertListResource, ConcertListViewSortResource, ConcertListSearchResource,ConcertInformationResource,ConcertListMainResource,ConcertListSearch2Resource,ConcertListImageSearchResourc
from resources.post import PostCreateResource,PostDeleteResource,PostReadResource,PostUpdateResource,PostInformationResource,PostListSearchResource
from resources.likes import LikeResource,myLikResource,myartistLikResource,myconcertLikResource,mygenreLikResource,concertLikSearchResource,artistLikSearchResource,myLikeSearchResource
from resources.comment import postCommentResource,PostCommentDeleteResource
from resources.artist import ArtistListResource
app = Flask(__name__)
app.config['DEBUG'] = True

# 환경변수 셋팅
app.config.from_object(Config)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist


api = Api(app)
# 경로와 리소스를 연결하는 코드 작성.
api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')
api.add_resource(myinfoResource,'/me')



api.add_resource(ConcertListResource, '/concert')
api.add_resource(ConcertListViewSortResource, '/concert/sort')
api.add_resource(ConcertListSearch2Resource, '/concert/search/old')
api.add_resource(ConcertInformationResource,'/concert/information/<int:concert_id>')
api.add_resource(ConcertListMainResource,'/concert/main')
api.add_resource(ConcertListSearchResource,'/concert/search')

api.add_resource(ConcertListImageSearchResourc,'/concert/image/search')

api.add_resource(PostCreateResource,'/post/create')
api.add_resource(PostReadResource,'/post')
api.add_resource(PostDeleteResource, '/post/delete/<int:post_id>')
api.add_resource(PostUpdateResource, '/post/update/<int:post_id>')
api.add_resource(postCommentResource,'/post/comment/<int:post_id>')
api.add_resource(PostCommentDeleteResource,'/post/comment/delete/<int:comment_id>')
api.add_resource(PostInformationResource,'/post/information/<int:post_id>')
api.add_resource(PostListSearchResource,'/post/search')

# api.add_resource(postLikeResource,'/post/like/<int:post_id>')
# api.add_resource(artistLikeResource,'/artist/like/<int:artist_id>')
# api.add_resource(concertLikeResource,'/concert/like/<int:concert_id>')
api.add_resource(LikeResource,'/like/<int:combined_id>')
api.add_resource(myLikResource,'/mylike')
api.add_resource(myartistLikResource,'/mylike/artist')
api.add_resource(myconcertLikResource,'/mylike/concert')
api.add_resource(mygenreLikResource,'/mylike/genre')
api.add_resource(ArtistListResource,'/artist')
api.add_resource(myLikeSearchResource,'/mylike/search') 

api.add_resource(concertLikSearchResource,'/concert/title')
api.add_resource(artistLikSearchResource,'/artist/')




def handler(event,context):
    return serverless_wsgi.handle_request(app,event,context)

if __name__=="__main__":
    app.run(debug=True)
