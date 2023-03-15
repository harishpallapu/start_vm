from flask import *
from flask_cors import CORS
import subprocess
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import functions
app = Flask(__name__)
CORS(app)
app.debug = True
app.secret_key = 'development key'
app.config['JSON_SORT_KEYS'] = False

# import parametercode.parameter


@app.route('/', methods=['get'])
def homepage():
    return "hi"


@app.route('/fetch_vm_ip', methods=['post'])
def fetch_vm_ip():
    vm_ip_data = []
    response = request.json
    instance_id = response['instance_id']
    print(instance_id)
    # instance_name = "windows2"
    #ip_script = "aws ec2 describe-instances --instance-ids i-05893ba5aa8c8af2a --query 'Reservations[*].Instances[*].[PrivateIpAddress, PublicIpAddress]'"
    ip_script = 'aws ec2 describe-instances --instance-ids '+  str(instance_id) +  " --query 'Reservations[*].Instances[*].[PrivateIpAddress, PublicIpAddress]'"
    print(ip_script)
    result = subprocess.run(["powershell.exe", ip_script], stdout=subprocess.PIPE)
    ip_result = result.stdout.decode("utf-8")
    ip_result = json.loads(ip_result)
    #ip_result = ast.literal_eval(ip_result)
    print(ip_result)
    print(ip_result[0][0][0])
    password_script = "aws ec2 get-password-data --instance-id "+ str(instance_id) +" --priv-launch-key 'C:\\fetch_vm_ip\\ansible_tower.pem'"
    password_result = subprocess.run(["powershell.exe", password_script], stdout=subprocess.PIPE)
    password = password_result.stdout.decode("utf-8")
    #password = ast.literal_eval(password_result.stdout.decode("utf-8"))
    password = json.loads(password)
    data = {}
    data['PrivateIpAddress'] = ip_result[0][0][0]
    data['PublicIpAddress']  = ip_result[0][0][1]
    data['instance_id'] = instance_id
    data['Username'] = "Administrator"
    data['Password'] = str(password['PasswordData'])
    vm_ip_data.append(data)
    print(vm_ip_data)
    #return vm_ip_data
    return jsonify({
        "message": "Success",
        "status": "200",
        "data": vm_ip_data
    })

@app.route('/vm_list', methods=['get'])
def get_vm_list():
    data = functions.vm_list()
    return jsonify({
        "message": "Success",
        "status": "200",
        "data": data
    })

# def __vm_list__():
#     data = []
#     vm_list_query = "aws ec2 describe-instances --query  'Reservations[*].Instances[*].[Tags[*].Value, State.Name,InstanceId]'"
#     result = subprocess.run(["powershell.exe", vm_list_query], stdout=subprocess.PIPE)
#     vm_list_result = result.stdout.decode("utf-8")
#     vm_list = json.loads(vm_list_result)
#     for i in range(len(vm_list)):
#         instance_id = vm_list[i][0][2]
#         ###getting vm ips
#         ip_script = 'aws ec2 describe-instances --instance-ids ' + str(instance_id) + " --query 'Reservations[*].Instances[*].[PrivateIpAddress, PublicIpAddress]'"
#         result = subprocess.run(["powershell.exe", ip_script], stdout=subprocess.PIPE)
#         ip_result = result.stdout.decode("utf-8")
#         ip_result = json.loads(ip_result)
#         local_ip = get_local_ip()
#         if local_ip['PrivateIpAddress'] != ip_result[0][0][0] and local_ip['PublicIpAddress'] != ip_result[0][0][1]:
#             vm_details = {}
#             vm_details['instance_name'] = vm_list[i][0][0][0]
#             vm_details['instance_id'] = vm_list[i][0][2]
#             vm_details['status'] = vm_list[i][0][1]
#             data.append(vm_details)
#         else:
#             pass
#     return jsonify({
#         "message": "Success",
#         "status": "200",
#         "data": data
#     })
#


# def get_local_ip():
#     vm_localip_query = "Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress"
#     result = subprocess.run(["powershell.exe", vm_localip_query], stdout=subprocess.PIPE)
#     vm_ip_result = result.stdout.decode("utf-8")
#     vm_local_ip_result = vm_ip_result.replace('\r', "").replace(" ", "").split("\n")
#     data = {}
#     data['PrivateIpAddress'] = vm_local_ip_result[4]
#     data['PublicIpAddress'] = vm_local_ip_result[3]
#     return data



@app.route('/fetch_vm_message', methods=['get'])
def fetch_vm_message():
    #time.sleep(50)
    response = requests.get("http://3.108.57.125/api/v2/job_templates/9/jobs/?order_by=-id",
                            auth=HTTPBasicAuth('3iflexib', 'flexib@3i'), timeout=10)
    vm_list = json.loads(response.text)
    if vm_list['results'][0]['summary_fields']['project']['status'].upper() == 'SUCCESSFUL':
        print("SUCCESSFUL")
        return jsonify({
            "message": "VM created successfully",
            "status": "200"
        })
    elif vm_list['results'][0]['summary_fields']['project']['status'].upper() == 'FAILED':
        print("FAILED")
        return jsonify({
            "message": "Creation of VM is Failed",
            "status": "200"
        })
    elif vm_list['results'][0]['summary_fields']['project']['status'].upper() == 'RUNNING':
        time.sleep(20)
        print("RUNNING")
        return jsonify({
            "message": "Creating of VM is in Progress",
            "status": "200"
        })

@app.route('/instance_event', methods=['post'])
def instance_event():
    response = request.json
    instance_id = response['instance_id']
    event = response['event']
    if event.upper() == "START":
        filename = 'C:\\fetch_vm_ip\\parametercode\\start_var.yml'
        with open(filename, 'w') as file:
            file.truncate(0)
            file.write('instance_id:'+ " " +'"' +str(instance_id) +'"')
        try:
            cd = push_code('git add start_var.yml','git commit -m "start_var"')
            time.sleep(58)
            return jsonify({
                "message": "Instance Started Successfully",
                "status": "200"
            })
        except:
            return jsonify({
                "message": "Something went wrong",
                "status": "400"
            })

    elif event.upper() == "STOP":
        try:
            query = "aws ec2 stop-instances --instance-ids " + str(instance_id)
            result = subprocess.run(["powershell.exe", query], stdout=subprocess.PIPE)
            vm_stop = result.stdout.decode("utf-8")
            return jsonify({
                "message": "Instance Stopped Successfully",
                "status": "200"
            })
        except:
            return jsonify({
                "message": "Something went wrong",
                "status": "400"
            })

    elif event.upper() == "TERMINATE":
        try:
            query = "aws ec2 terminate-instances --instance-ids " + str(instance_id)
            result = subprocess.run(["powershell.exe", query], stdout=subprocess.PIPE)
            vm_terminate = result.stdout.decode("utf-8")
            return jsonify({
                "message": "Instance Terminated Successfully",
                "status": "200"
            })
        except:
            return jsonify({
                "message": "Something went wrong",
                "status": "400"
            })


def push_code(commit_file,commit_message):
    cmds = [commit_file, commit_message, "git push"]
    cd = []
    for i in range(3):
        query = cmds[i]
        result = subprocess.run(["powershell.exe", query], stdout=subprocess.PIPE)
        cd.append(result)
    return cd


@app.route('/instance_start', methods=['post'])
def instance_start():
    start = time.time()
    vm_names =[]
    response = request.json
    instance_name = response['instance_name']
    instance_type = response['instance_type']
    group = response['group']
    count = response['count']
    security_group = response['security_group']
    data = functions.vm_list()
    for i in range(len(data)):
        if data[i]['instance_name'] == instance_name:
            return jsonify({
                "message": "Duplicate Instance name"
            })
        else:
            pass
    print("passed the condition")
    filename = 'C:\\fetch_vm_ip\\parametercode\\variable.yml'
    with open(filename, 'w') as file:
        lines = ['Instance_Name:' + " " + str(instance_name) + '\n', 'keypair:' + " " + "ansible_tower" + '\n',
                 'instance_type:' + " " + str(instance_type) + '\n', 'image:' + " " + "ami-0398ed544cd6d0ae7" + '\n',
                 'wait:' + " " + "No" + '\n', 'group:' + " " + str(group) + '\n',
                 'count:' + " " + str(count) + '\n', 'region:' + " " + "ap-south-1" + '\n',
                 'security_group:' + " " + str(security_group)]
        file.truncate(0)
        file.writelines(lines)
        file.close()
    push_code('git add variable.yml','git commit -m "create_ec2"')
    condition = False
    while condition != True:
        for i in range(100):
            print(i)
            time.sleep(5)
            try:
                data1 = functions.vm_list()
                print(data1)
            except:
                pass
            for i in range(len(data1)):
                if data1[i]['instance_name'] == instance_name:
                    print(i)
                    condition = True
                    if data1[i]['status'] == "running":
                        end = time.time()
                        print(end- start)
                        return jsonify({
                            "message": "Vm Provision successfully",
                            "status": "200"
                        })
                    elif data1[i]['status'] == "failed":
                        end = time.time()
                        print(end - start)
                        return jsonify({
                            "message": "Vm Provision failed",
                            "status": "200"
                        })
                else:
                    condition = False
                    pass


@app.route('/get_instance_details', methods=['post'])
def get_instance_details():
    data = []
    response = request.json
    instance_id = response['instance_id']
    print(instance_id)
    describe_instance = 'aws ec2 describe-instances --instance-ids '+  str(instance_id) +  " --query 'Reservations[*].Instances[*].[InstanceType, ImageId,Placement.AvailabilityZone,Tags[*],SecurityGroups]'"
    result = subprocess.run(["powershell.exe", describe_instance], stdout=subprocess.PIPE)
    describe_instance_result = result.stdout.decode("utf-8")
    describe_instance_details = json.loads(describe_instance_result)
    #describe_instance_details = ast.literal_eval(describe_instance_result)
    print(describe_instance_details)
    count_details = '(Get-EC2Instance -Filter @{Name="tag:Name";Values=' +'"' + describe_instance_details[0][0][3][0]['Value'] +'"' + "}).Instances.Count"
    result_count = subprocess.run(["powershell.exe", count_details], stdout=subprocess.PIPE)
    count_details_result = result_count.stdout.decode("utf-8")
    count_result_json = json.loads(count_details_result)
    instance_details ={}
    instance_details['instance_type'] = describe_instance_details[0][0][0]
    instance_details['os_image'] = describe_instance_details[0][0][1]
    instance_details['region'] = describe_instance_details[0][0][2]
    instance_details['instance_name'] = describe_instance_details[0][0][3][0]['Value']
    instance_details['instance_id'] = instance_id
    instance_details['security_group'] = describe_instance_details[0][0][4][0]['GroupName']
    instance_details['count'] = count_result_json
    data.append(instance_details)
    return jsonify({
    "message": "Success",
    "status": "200",
    "data" : data
    })
@app.route('/autoscale_configuration', methods=['post'])
def autoscale_configuration():
    response = request.json
    instance_id = response['instance_id']
    instance_type = response['instance_type']
    describe_instance = 'Edit-EC2InstanceAttribute -InstanceId '+  str(instance_id) +  " -InstanceType " + str(instance_type)
    print(describe_instance)
    result = subprocess.run(["powershell.exe", describe_instance], stdout=subprocess.PIPE)
    print(result)
    describe_instance_result = result.stdout.decode("utf-8")
    print(describe_instance_result)
    # describe_instance_details = json.loads(describe_instance_result)
    # print(describe_instance_details)
    return jsonify({
        "message": "Success",
        "status": "200"
    })


#Edit-EC2InstanceAttribute -InstanceId i-01e801dc3679fdb45 -InstanceType t2.micro
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006, debug=True)
