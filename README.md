# aws_TicketMerge_app
 
## 💁 기획의도
**하나로 만든 데이터**를 API를 사용하여 볼 수 있도록 만들었습니다.<br/>

##  💁 데이터셋 정보
해당 데이터는<br/>
[멜론](https://ticket.melon.com/concert/index.htm?genreType=GENRE_CON, '멜론 티켓')<br/>
[인터파크 티켓](https://tickets.interpark.com/contents/genre/concert, '인터파크 티켓')<br/>
[티켓링크](https://www.ticketlink.co.kr/performance/14, '티켓링크')<br/>
[Yes24](http://ticket.yes24.com/New/Genre/GenreMain.aspx?genre=15456, 'yes24 티켓')<br/>
에서 스크래핑하여 데이터를 가공하였습니다<br/><br/>

## 💁 서버 개발 과정
+ 먼저 기획의도에 따라 순서를 정했습니다.<br/>
1. **Serverless로 서버 배포**하기<br/>
2. **Docker 활용** 하여 **패키징**하기<br/>
3. **GitActions** 사용하여 **자동 배포**하기<br/>
4. 로그인 jwt 적용하기<br/>
5. 콘서트 정렬 쿼리 만들기<br/>
6. 콘서트 상세보기 쿼리 만들기<br/>
7. 좋아요 leftJoin 쿼리 만들기<br/>


## 🔷 결과 🔷
만들어진 데이터파일과 서버로 안드로이드 개발을 진행하였습니다.<br/>
[안드로이드 깃허브 링크](https://github.com/yoonmiriii/TicketMerge_android, '안드로이드 깃허브 링크')<br/>
[프로젝트 기술서 링크](https://docs.google.com/presentation/d/10SK2fhhHQwgktnOjM6e3k2yymyNaWv71hm8S_mkchUI/edit?usp=sharing, '프로젝트 기술서 링크')<br/>
[시연 동영상 링크](https://youtu.be/feCfx006Jew, '시연동영상 링크')<br/>
