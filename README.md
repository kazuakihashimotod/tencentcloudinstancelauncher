TencentCloudのインスタンスを起動/停止を行うスクリプトです
Windows用で、自動的にリモートデスクトップを起動したり、パスワードをクリップボードにコピーしたりもします
TencentCloudのSDKを使っていますので、サンプル的にも使えます。

tc_il start でクラウドの起動
tc_il_end   でクラウドの停止
tc_il list は今のクラウド一覧を表示する機能

となっています。何も指定しないとエラーが出ます。
ぞ全に、pipで
pip install tencentcloud-sdk-python
pip install pyperclip
が必要です。また、secureid securepassword GPUの名前、Region/APの設定はソース内にハードコーディングしてあるので、書き換えてください。
バッチファイルのようなものなので、利用はご自由に。
