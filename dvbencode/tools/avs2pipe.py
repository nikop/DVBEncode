# -*- coding: utf-8 -*-
import subprocess, re

def avs2pipe_info(filename):
    """Run avs2pipe on a file"""

    proc = subprocess.Popen(["avs2pipe\\avs2pipemod.exe", "-info", filename], stdout=subprocess.PIPE)
    proc.wait()

    out = proc.stdout.read().decode('cp1252')

    ans = {}

    for m in re.findall('([^ ]+)\s+(.+)\r\n', out):
        ans[m[0]] = m[1]

    ans["v:fps"] = eval(ans["v:fps"])

    return ans