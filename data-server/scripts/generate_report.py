"""
生成压力测试报告
读取 CSV 测试结果，生成 Markdown 格式的报告
"""

import csv
import statistics
from datetime import datetime
import os

def generate_report(csv_file='stress_test_results.csv', output_file='test_report.md'):
    """生成测试报告"""
    
    # 读取 CSV
    if not os.path.exists(csv_file):
        print(f"错误：未找到测试结果文件 {csv_file}")
        return
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    if not results:
        print("错误：测试结果为空")
        return
    
    # 数据分析
    total = len(results)
    successful = sum(1 for r in results if r['是否成功'] == '是')
    failed = total - successful
    
    # 响应时间分析
    response_times = []
    for r in results:
        if r['响应时间 (ms)'] != 'N/A':
            try:
                response_times.append(float(r['响应时间 (ms)']))
            except:
                pass
    
    # 按认证方式分组
    auth_methods = {}
    for r in results:
        method = r.get('认证方式', 'unknown')
        if method not in auth_methods:
            auth_methods[method] = {'total': 0, 'success': 0, 'times': []}
        
        auth_methods[method]['total'] += 1
        if r['是否成功'] == '是':
            auth_methods[method]['success'] += 1
        if r['响应时间 (ms)'] != 'N/A':
            try:
                auth_methods[method]['times'].append(float(r['响应时间 (ms)']))
            except:
                pass
    
    # 生成报告
    report = f"""# 压力测试报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 总体统计

| 指标 | 数值 |
|------|------|
| 总请求数 | {total} |
| 成功请求 | {successful} |
| 失败请求 | {failed} |
| 成功率 | {successful/total*100:.2f}% |

---

## ⏱️ 响应时间统计

| 统计项 | 数值 |
|--------|------|
| 平均响应时间 | {statistics.mean(response_times):.2f} ms |
| 中位数响应时间 | {statistics.median(response_times):.2f} ms |
| 最小响应时间 | {min(response_times):.2f} ms |
| 最大响应时间 | {max(response_times):.2f} ms |
| 标准差 | {statistics.stdev(response_times):.2f} ms |
"""
    
    # 95 百分位
    if len(response_times) > 1:
        sorted_times = sorted(response_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        report += f"| 95 百分位 | {sorted_times[p95_idx]:.2f} ms |\n"
        report += f"| 99 百分位 | {sorted_times[p99_idx]:.2f} ms |\n"
    
    report += "\n---\n\n"
    
    # 按认证方式统计
    report += "## 📈 按认证方式统计\n\n"
    report += "| 认证方式 | 总请求 | 成功 | 失败 | 成功率 | 平均响应时间 |\n"
    report += "|---------|--------|------|------|--------|-------------|\n"
    
    for method, data in auth_methods.items():
        success_rate = data['success']/data['total']*100 if data['total'] > 0 else 0
        avg_time = statistics.mean(data['times']) if data['times'] else 0
        report += f"| {method} | {data['total']} | {data['success']} | {data['total']-data['success']} | {success_rate:.2f}% | {avg_time:.2f}ms |\n"
    
    report += f"""
---

## 📉 性能评估

### 成功率评估
"""
    
    if successful/total > 0.99:
        report += "✅ **优秀** - 成功率超过 99%，系统稳定性良好\n"
    elif successful/total > 0.95:
        report += "⚠️ **良好** - 成功率在 95%-99%之间，基本满足要求\n"
    else:
        report += "❌ **需要改进** - 成功率低于 95%，需要优化\n"
    
    report += f"""
### 响应时间评估
"""
    
    avg_response = statistics.mean(response_times)
    if avg_response < 100:
        report += "✅ **优秀** - 平均响应时间小于 100ms\n"
    elif avg_response < 200:
        report += "⚠️ **良好** - 平均响应时间在 100-200ms 之间\n"
    else:
        report += "❌ **需要优化** - 平均响应时间超过 200ms\n"
    
    report += f"""
---

## 📝 测试详情

### 测试环境
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **测试工具**: Python 压力测试脚本 (jmeter_test.py)
- **测试模式**: 混合模式（普通/JWT/API Key）

### 数据分布
- 总样本数：{total}
- 有效响应时间样本：{len(response_times)}
- 数据覆盖率：{len(response_times)/total*100:.2f}%

---

## 💡 建议和改进

### 性能优化建议
1. **缓存层**: 考虑添加 Redis 缓存高频数据
2. **数据库**: 如需持久化，建议使用 PostgreSQL 或 MongoDB
3. **负载均衡**: 高并发场景可使用 Nginx 进行负载均衡
4. **异步处理**: 考虑使用 Celery 处理耗时任务

### 安全加固建议
1. **HTTPS**: 生产环境必须启用 HTTPS
2. **密钥轮换**: 定期更换加密密钥
3. **监控告警**: 添加异常检测和告警系统
4. **日志审计**: 完善安全审计日志

---

## 📊 图表数据（可选）

### 响应时间分布
```
0-50ms:     {'█' * sum(1 for t in response_times if t < 50)}
50-100ms:   {'█' * sum(1 for t in response_times if 50 <= t < 100)}
100-200ms:  {'█' * sum(1 for t in response_times if 100 <= t < 200)}
200-500ms:  {'█' * sum(1 for t in response_times if 200 <= t < 500)}
500ms+:     {'█' * sum(1 for t in response_times if t >= 500)}
```

---

*报告生成工具：generate_report.py*
*数据源：{csv_file}*
"""
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 测试报告已生成：{output_file}")
    print(f"📊 总请求数：{total}")
    print(f"✅ 成功率：{successful/total*100:.2f}%")
    print(f"⏱️ 平均响应时间：{statistics.mean(response_times):.2f}ms")
    
    # 同时生成简化的 HTML 版本
    generate_html_report(results, output_file.replace('.md', '.html'))


def generate_html_report(results, output_file):
    """生成 HTML 格式报告"""
    
    total = len(results)
    successful = sum(1 for r in results if r['是否成功'] == '是')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>压力测试报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .stats {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>📊 压力测试报告</h1>
    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <h2>总体统计</h2>
        <table>
            <tr><th>总请求数</th><td>{total}</td></tr>
            <tr><th>成功请求</th><td class="success">{successful}</td></tr>
            <tr><th>失败请求</th><td class="error">{total - successful}</td></tr>
            <tr><th>成功率</th><td>{successful/total*100:.2f}%</td></tr>
        </table>
    </div>
    
    <h2>说明</h2>
    <p>详细报告请查看 Markdown 版本：test_report.md</p>
    
    <footer style="margin-top: 40px; color: #666; font-size: 12px;">
        <p>生成工具：generate_report.py</p>
    </footer>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"📄 HTML 报告已生成：{output_file}")


if __name__ == '__main__':
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'stress_test_results.csv'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'test_report.md'
    
    generate_report(csv_file, output_file)
