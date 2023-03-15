import subprocess

def push_code():
    cmds = ['git add --all', 'git commit -m "start_var"', "git push"]
    cd = []
    for i in range(3):
        query = cmds[i]
        result = subprocess.run(["powershell.exe", query], stdout=subprocess.PIPE)
        cd.append(result)
    return cd
push_code()

# def hello():
#     return "hello from "