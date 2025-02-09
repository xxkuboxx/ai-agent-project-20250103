## アプリの記事
https://zenn.dev/xxkuboxx/articles/98478887b98406

## ローカル実行方法
### 事前準備
- Dockerのインストール
- app配下に以下権限を付与したサービスアカウントキーのjsonファイルを配置
  - Cloud Datastore オーナー（Firestoreアクセス用）
  - Vertex AI ユーザー（Geminiアクセス用）
- app配下に.envファイルを作成し以下を記載する。
  ```
  GCP_PROJECT="<your-project>"
  GOOGLE_APPLICATION_CREDENTIALS="/app/<your-service-account-key-file>.json"
  ```

### 実行方法
- docker image 作成
  ```
  docker build -t langgraph-chat .
  ```

- 以下オプションをつけてコンテナ起動
  - ホスト側のappディレクトリをコンテナ側のappディレクトリにマウント
  - ポート番号8080をフォワーディング
  ```
  docker run --rm -it -v "$(pwd)/app:/app" -p 8080:8080 --name my_langgraph_chat langgraph-chat
  ```

- ブラウザからアクセス
  - http://localhost:8080/


### 停止方法
- ```ctrl+c```でstreamlitを停止し、コンテナから抜ける。


## Cloud Runへのデプロイコマンド
```
gcloud run deploy my-ai-chat --source . 
--update-env-vars GCP_PROJECT=<your-project>
--service-account <your-service-account>
```
