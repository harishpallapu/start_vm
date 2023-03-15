import json
import subprocess
import jsonify

def vm_list():
    data = []
    vm_list_query = "aws ec2 describe-instances --query  'Reservations[*].Instances[*].[Tags[*].Value, State.Name,InstanceId]'"
    result = subprocess.run(["powershell.exe", vm_list_query], stdout=subprocess.PIPE)
    vm_list_result = result.stdout.decode("utf-8")
    vm_list = json.loads(vm_list_result)
    #print(vm_list)
    #print(len(vm_list))
    for i in range(len(vm_list)):
        for _ in range(len(vm_list[i])):
            instance_id = vm_list[i][_][2]
            ###getting vm ips
            ip_script = 'aws ec2 describe-instances --instance-ids ' + str(instance_id) + " --query 'Reservations[*].Instances[*].[PrivateIpAddress, PublicIpAddress]'"
            result = subprocess.run(["powershell.exe", ip_script], stdout=subprocess.PIPE)
            ip_result = result.stdout.decode("utf-8")
            ip_result = json.loads(ip_result)
            local_ip = get_local_ip()
            if local_ip['PrivateIpAddress'] != ip_result[0][0][0] and local_ip['PublicIpAddress'] != ip_result[0][0][1]:
                vm_details = {}
                vm_details['instance_name'] = vm_list[i][_][0][0]
                vm_details['instance_id'] = vm_list[i][_][2]
                vm_details['status'] = vm_list[i][_][1]
                data.append(vm_details)
            else:
                pass
    #print(data)
    return data


def get_local_ip():
    vm_localip_query = "Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress"
    result = subprocess.run(["powershell.exe", vm_localip_query], stdout=subprocess.PIPE)
    vm_ip_result = result.stdout.decode("utf-8")
    vm_local_ip_result = vm_ip_result.replace('\r', "").replace(" ", "").split("\n")
    data = {}
    data['PrivateIpAddress'] = vm_local_ip_result[4]
    data['PublicIpAddress'] = vm_local_ip_result[3]
    return data
