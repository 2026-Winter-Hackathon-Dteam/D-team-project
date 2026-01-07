# D-team-project
2026 ハッカソン冬の陣、開発用リポジトリです

----
## 開発環境構築手順
1. 'git clone'する
2. docker-compose.ymlと同じ階層に.envを各自作成する（.envの内容はMattermostおよびNotionで共有します）
3. 'docker compose up --build'をする
4. 'docker exec -it dteam_dev_mysql mysql -u testuser -p'で.envの通りのパスワードを入力し、MySQLにアクセスできることを確認してください