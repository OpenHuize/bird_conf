from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import re
import datetime
import schedule  # 引入 schedule 库
import time

app = Flask(__name__)

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 定义 AS 和其对应的 AS-SET
as_dict = {
    "AS208753": "AS-DANGELO",
    "AS123456": "AS-ANOTHER",
    # 添加更多的 AS 和 AS-SET 对应关系
}

# 获取节点代码
def get_node_id():
    node_id = None
    with open(os.path.join(script_dir, "../vars.conf"), "r") as vars_file:
        for line in vars_file:
            match = re.match(r'define\s+NODE_ID\s+=\s+(\d+);', line)
            if match:
                node_id = match.group(1)
                break
    return node_id

# 运行 bgpq4 获取配置文件
def run_bgpq4(as_number, as_set, r_option, output_file, ip_version):
    try:
        output = subprocess.check_output(
            ["bgpq4", "-b", f"-A", f"-{ip_version}", as_set, f"-R {r_option}", f"-l {as_number}_ipv{ip_version}"],
            text=True,
            stderr=subprocess.STDOUT,
        )

        with open(output_file, "w") as f:
            f.write(output)
    except subprocess.CalledProcessError as e:
        error_msg = e.output.strip()
        with open(os.path.join(script_dir, "log/bgpq4.log"), "a") as log_file:
            log_file.write(f"{datetime.datetime.now()} - Error (IPv{ip_version}): ASN {as_number} - {error_msg}\n")

# 生成 BGP 配置文件的函数
def generate_bgp_config():
    for as_number, as_set in as_dict.items():
        # IPv4 Configuration
        run_bgpq4(as_number, as_set, "24", f"../filters/{as_number}.ipv4.conf", 4)

        # IPv6 Configuration
        run_bgpq4(as_number, as_set, "48", f"../filters/{as_number}.ipv6.conf", 6)

# 定时任务，每十分钟运行一次 generate_bgp_config
schedule.every(10).minutes.do(generate_bgp_config)

# 主页，输入 AS 号码页面
@app.route('/')
def index():
    node_id = get_node_id()
    return render_template('index.html', node_id=node_id)

# 处理搜索框的提交
@app.route('/submit', methods=['POST'])
def submit():
    asn = request.form['asn'].strip().upper()  # 去除首尾空格并强制转换为大写
    if re.match(r'^AS\d+$', asn):
        if asn in as_dict:
            as_set = as_dict[asn]
            return redirect(f'/filter/{asn}/{as_set}')
        else:
            return "ASN not found."
    else:
        return "Invalid ASN format. Please enter a valid ASN (e.g., AS208753)."


# 显示 AS-SET 过滤器页面
@app.route('/filter/<asn>/<as_set>')
def show_filter(asn, as_set):
    node_id = get_node_id()
    return render_template('select_filter.html', asn=asn, node_id=node_id, as_set=as_set)

# 生成 IPv4 过滤器页面
@app.route('/filter/<asn>/<as_set>/ipv4')
def show_ipv4_filter(asn, as_set):
    node_id = get_node_id()
    ipv4_file = f"../filters/{asn}.ipv4.conf"
    
    # 读取bgpq4生成的IPv4过滤器内容
    try:
        with open(ipv4_file, 'r') as ipv4_file:
            ipv4_content = ipv4_file.read().splitlines()
    except FileNotFoundError:
        return "IPv4 Filter not found."

    return render_template('filter.html', asn=asn, node_id=node_id, ip_type="IPv4", filter_content=ipv4_content, as_set=as_set)

# 生成 IPv6 过滤器页面
@app.route('/filter/<asn>/<as_set>/ipv6')
def show_ipv6_filter(asn, as_set):
    node_id = get_node_id()
    ipv6_file = f"../filters/{asn}.ipv6.conf"
    
    # 读取bgpq4生成的IPv6过滤器内容
    try:
        with open(ipv6_file, 'r') as ipv6_file:
            ipv6_content = ipv6_file.read().splitlines()
    except FileNotFoundError:
        return "IPv6 Filter not found."

    return render_template('filter.html', asn=asn, node_id=node_id, ip_type="IPv6", filter_content=ipv6_content, as_set=as_set)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

    
    while True:
        schedule.run_pending()  # 检查定时任务是否需要运行
        time.sleep(1)
