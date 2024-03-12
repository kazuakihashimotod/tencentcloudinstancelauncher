
##usage list ->インスタンスリスト獲得
##      end  ->指定インスタンスの停止
##      start->startからパスのクリップボードコピーとリモートデスクトップの起動、終了まで
##引数なしだとpythonの変数参照エラーが出ます。また各種エラーはSDKの英語＆中国語のエラーになります
##tencentcloudsdkとpyperclipはpipを使ってインストールが必要
#pip install tencentcloud-sdk-python
#pip install pyperclip
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.cvm.v20170312 import cvm_client, models
import time
import sys              #コマンドライン引数取得用
import subprocess       #リモートデスクトップ起動用
import pyperclip        #パスワードのクリップボードコピー用

##ID/KEYの設定
secretid="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
secretkey="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx""
#リージョンは、シンガポールなら「ap-singapore」東京なら「ap-tokyo」といった「ap-」に地域名を入れる感じのわかりやすい文字列
useap="ap-singapore"        ##リージョン
instance_name="GPUTEST"     ##インスタンス名
adminpass='xxxxxxxxxxxxxx' ##リモートデスクトップのパスワード

##リモートデスクトップの起動
def start_remote_desktop(ip, user, password):
    rdp_file_content = f"""
    full address:s:{ip}
    username:s:{user}
    password:s:{password}"""
    with open('temp.rdp', 'w') as f:
        f.write(rdp_file_content)
    subprocess.run(['mstsc', 'temp.rdp'])

class TencentClient:
    def __init__(self, secret_id, secret_key, region):
        cred = credential.Credential(secret_id, secret_key)
        httpProfile_cvm = HttpProfile()
        clientProfile_cvm = ClientProfile()
        clientProfile_cvm.httpProfile = httpProfile_cvm
        httpProfile_cvm.endpoint = "cvm.tencentcloudapi.com"
        self.client = cvm_client.CvmClient(cred, region, clientProfile_cvm)

##インスタンスのシャットダウン
    def shutdown_instance(self,instance_id):
        req = models.StopInstancesRequest()
        req.InstanceIds = [instance_id]
        req.StoppedMode="STOP_CHARGING"
        resp = self.client.StopInstances(req) 
        print(resp.to_json_string()) 

##インスタンス一覧の表示
    def get_instance_list(self):
        req = models.DescribeInstancesRequest()
        params = '{}'
        req.from_json_string(params)
        resp = self.client.DescribeInstances(req) 
        print(resp.to_json_string()) 

##インスタンスの開始
    def start_instance(self, instance_id):
        req = models.StartInstancesRequest()
        req.InstanceIds = [instance_id]
        resp = self.client.StartInstances(req) 
        
# インスタンスの状態がRunningになるまで待機
        while True:
            req = models.DescribeInstancesRequest()
            req.InstanceIds = [instance_id]
            resp = self.client.DescribeInstances(req) 
            instance_status = resp.InstanceSet[0].InstanceState
            if instance_status == "RUNNING":
                break
            print(f"Instance status: {instance_status}. Waiting 5sec")
            time.sleep(5)
        return instance_id

##インスタンスIDの獲得
    def get_instance_id_by_name(self, instance_name):
        req = models.DescribeInstancesRequest()
        try:
            resp = self.client.DescribeInstances(req)
            for instance in resp.InstanceSet:
                if instance.InstanceName == instance_name:
                    return instance.InstanceId
        except TencentCloudSDKException as err: 
            print(err) 
        return None

##インスタンスのipの獲得
    def get_instance_ip(self,instance_id):
        req = models.DescribeInstancesRequest()
        req.InstanceIds = [instance_id]
        resp = self.client.DescribeInstances(req) 
        if resp.InstanceSet and resp.InstanceSet[0].PublicIpAddresses:
            return resp.InstanceSet[0].PublicIpAddresses[0]
        else:
            print(f"No PublicIP instance found with ID {instance_id}")
            return None

####ここから実際の関数の実行
client = TencentClient(secretid,secretkey,useap) ##tencentSDKクラスの初期化
##インスタンスIDの獲得
instance_id = client.get_instance_id_by_name(instance_name) 
if instance_id:
    print("Instance ID:", instance_id)
else:
    print("Instance not found.")
##引数の解釈
if sys.argv[1]=='list':
    client.get_instance_list()
    exit()
elif sys.argv[1]=='end':
    print ("end")
    client.shutdown_instance(instance_id)
    exit()
elif sys.argv[1]!='start':
    print("Usage: list | end | start")
    exit(1)
else:
##スタートから終了までの処理
    print ("start")
    client.start_instance(instance_id)
    ips=client.get_instance_ip(instance_id)
    print (f"IP: {ips}")
    pyperclip.copy(adminpass)
    start_remote_desktop(ips, 'Administrator', adminpass)
    print ("shutdown")
    client.shutdown_instance(instance_id)
