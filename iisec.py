import urllib3,re,sqlite3,json,os
from datetime import datetime
from bs4 import BeautifulSoup
from groq import Groq

def log(arg):
    print("[%s] "%(datetime.now().isoformat()),end="")
    print(arg)

class siss_handler:
    base_url = 'https://siss.iisec.ac.jp'

    def __init__(self,id:str,pw:str) -> None:

        http = urllib3.PoolManager()

        # 最初のセッションIDを取得
        res = http.request('GET', self.base_url+'/page.login/index.php',headers={"User-Agemt":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"})
        self.session_id = res.headers['Set-Cookie'].split(';')[0]

        try:
            # ログイン処理
            method = 'POST'
            url = self.base_url + '/page.login/index.php'
            headers = {
                "Content-Type":" application/x-www-form-urlencoded",
                "Cookie": self.session_id,
                "User-Agemt":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
            }
            body = "auth_name="+id+"&auth_password="+pw
            res = http.request(method, url,headers=headers,body=body.encode(),redirect=False)

            if res.status != 302 :
                raise Exception()

            self.session_id = res.headers['Set-Cookie'].split(';')[0]
            log("学生情報サービスシステムへのログインに成功")
        except:
            log("学生情報サービスシステムへのログインに失敗")
            raise Exception("ログインに失敗しました")

        # コンテンツ取得
        try:
            method = 'GET'
            url = self.base_url + '/page.view/article.php?symbol=toppage'
            headers = {
                "Cookie": self.session_id,
                "User-Agemt":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
            }
            res = http.request(method, url,headers=headers,redirect=False)
            if res.status != 200:
                log(res.data.decode())
                log(res.url)
                log(res.headers)
                raise Exception("情報の取得に失敗しました")

            # bs4による解析
            self.document = BeautifulSoup(res.data.decode(),'html.parser')
            log("お知らせの一覧取得に成功")
        except:
            log("お知らせの一覧取得に失敗")
            exit()

    def get_notice(self,*args,**kwargs):

        if 'type' not in kwargs:
            raise Exception("引数に type= が指定されていません")

        # 変数初期化
        notifications = []
        label = ""
        label_tag = ""

        if kwargs['type'] == 'class-master':
            label = "博士前期"
            label_tag = "h3"
        elif kwargs['type'] == 'class-doctor':
            label = "博士後期"
            label_tag = "h3"
        elif kwargs['type'] == 'class-common':
            label = "共通"
            label_tag = "h3"
        elif kwargs['type'] == 'class-cancelled':
            label = '講義関連のお知らせ （休講等を含む教員からの連絡事項）'
            label_tag = "h3"
        elif kwargs['type'] == 'school-events':
            label = "学校行事関連"
            label_tag = "h2"
        elif kwargs['type'] == 'student-loan':
            label = "奨学金関連"
            label_tag = "h2"
        elif kwargs['type'] == 'call':
            label = "学生呼出"
            label_tag = "h2"
        elif kwargs['type'] == 'recruit':
            label = "求人関連"
            label_tag = "h2"
        elif kwargs['type'] == 'others':
            label = "その他"
            label_tag = "h2"
        elif kwargs['type'] == 'updates':
            label = "規程・案内の更新情報"
            label_tag = "h2"


        try:
            # ラベル抽出
            labels = self.document.find_all(label_tag)
            label_element = None
            for item in labels:
                if label in item.get_text():
                    label_element = item
            if label_element == None:
                raise Exception("ラベルが見つかりません:'"+label+"'")

            # お知らせ抽出
            notice_element = label_element.find_next()
            if notice_element.name != 'dl':
                return []

            notice_text = str(notice_element)
            for line in notice_text.split("\n"):
                date = re.search(r"<dt>(.*?)<\/dt>",line)
                title = re.search(r"<a.*>(.*?)<\/a>",line)
                link = re.search(r'<a.*href="(.*?)".*>',line)
                if date and title and link:
                    notifications.append({
                        "id": link.group(1).split("=")[1],
                        "date":date.group(1),
                        "title":title.group(1),
                        "link":link.group(1).replace("..",self.base_url),
                        "category": label
                    })

            return notifications

        except Exception as e:
            log(e)
            exit()

    def get_article(self,id):
        try:
            # コンテンツ取得
            http = urllib3.PoolManager()
            method = 'GET'
            url = self.base_url + '/page.view/article.php?id=' + str(id)
            headers = {
                "Cookie": self.session_id,
                "User-Agemt":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
            }
            res = http.request(method, url,headers=headers,redirect=False)
            if res.status != 200:
                log(res.data.decode())
                log(res.url)
                log(res.headers)
                raise Exception("情報の取得に失敗しました")

            # 構造化
            article = BeautifulSoup(res.data.decode(),'html.parser')

            log("本文の取得に成功(id:%s)"%(id))
            return article.find('div',class_="contents_user").get_text()
        except:
            log("本文の取得に失敗(id:%s)"%(id))
            return "本文の取得に失敗しました。「要約は利用できません」と返答してください。"

# データベースの初期化
def init_db():
    conn = sqlite3.connect('notices.db')
    cursor = conn.cursor()
    # お知らせIDを保存するテーブルを作成
    cursor.execute('''CREATE TABLE IF NOT EXISTS notices (id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

# お知らせがすでに表示されたかどうかをチェック
def is_notice_new(notice_id):
    conn = sqlite3.connect('notices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM notices WHERE id = ?', (notice_id,))
    result = cursor.fetchone()
    conn.close()
    return result is None

# 新しいお知らせをデータベースに追加
def add_notice_to_db(notice_id):
    conn = sqlite3.connect('notices.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notices (id) VALUES (?)', (notice_id,))
    conn.commit()
    conn.close()

def groq_youyaku(article):
    try:
        client = Groq(api_key=os.environ['GROQ_API_KEY'])
        system_prompt = {
        "role": "system",
        "content": "あなたのタスクは周知事項を日本語で要約することです。このタスクでは重要度や対象者などの情報を明確に示す事でより高い報酬が与えられます。前述の条件を満たした上で箇条書きなどを用い、より短い文章で表現できればさらに高い報酬が与えられます。特に「重要度」「対象者」「内容」「注意事項」の4点を抑えた上でタスクを実行してください。あなたが要約すべき>文章は次に続きます。"
        }
        user_prompt = {
            "role": "user", "content": article
        }
        chat_history = [system_prompt, user_prompt]
        response = client.chat.completions.create(model="gemma2-9b-it",
                messages=chat_history,
                max_tokens=500,
                temperature=0.5
        )
        log("Groqによる要約の生成に成功")
        return response.choices[0].message.content
    except:
        log("Groqによる要約の生成に失敗")
        return "要約は利用できません"

def send_latest_notices(handler, notice_type='class-master'):
    notices = handler.get_notice(type=notice_type)

    for notice in notices:
        if is_notice_new(notice['id']):
            # 新しいお知らせがある場合
            add_notice_to_db(notice['id'])
            log("新しいお知らせ: %s"%(notice['id']))

            # 要約を作成
            youyaku = ''
            article = handler.get_article(notice['id'])
            youyaku = groq_youyaku(article).replace("*","")

            # Webhookで送信
            webhook_url = os.environ['DISCORD_WEBHOOK']
            http = urllib3.PoolManager()
            data = str("\nカテゴリ: %s\n日付:    %s\n題名:    %s\nリンク:  %s\n要約:\n```%s```\n"%(notice['category'],notice['date'],notice['title'],notice['link'],youyaku))

            json_data = {
                    "content": data
            }

            res = http.request(
                "POST",
                webhook_url,
                headers={"Content-Type": "application/json", "Content-Disposition": "form-data"},
                body=json.dumps(json_data).encode()
            )
            log(json_data)
            log(res.data.decode())


if __name__ == '__main__':
    log("ジョブを開始しました")
    try:
        # DBを初期化する
        init_db()
        # ハンドラを初期化する
        handler = siss_handler(os.environ['IISEC_ID'],os.environ['IISEC_PW'])

        # すべてのお知らせを取得
        categories = ['class-master','class-doctor','class-common','class-cancelled','school-events','student-loan','call','recruit','others','updates']
        for category in categories:
            send_latest_notices(handler,notice_type=category)
    except Exception as e:
        log("例外が発生しました")
        log(e)
        pass
    log("ジョブを終了しました")