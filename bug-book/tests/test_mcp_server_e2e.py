#!/usr/bin/env python3
"""MCP Server 端到端测试 - 通过 stdio 协议真实通信"""

import json
import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


# ============================================================================
# 测试数据准备
# ============================================================================

def prepare_test_data():
    """准备测试用的数据文件（使用系统临时目录）"""
    temp_dir = tempfile.mkdtemp(prefix='bugbook_test_')
    transcript_path = Path(temp_dir) / 'test_transcript.json'
    transcript_path.write_text(json.dumps({
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮你的？"}
        ]
    }, ensure_ascii=False))
    return str(transcript_path), temp_dir


def cleanup_test_data(temp_dir: str):
    """清理测试数据"""
    if temp_dir and Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


# ============================================================================
# MCP Server 测试
# ============================================================================

def run_mcp_test(storage_type: str, temp_dir: str):
    """通过子进程运行 MCP Server 并测试"""
    print(f"\n{'='*60}")
    print(f"测试 {storage_type.upper()} 后端 (MCP stdio)")
    print('='*60)

    # 启动 MCP Server 子进程
    env = os.environ.copy()

    creationflags = 0
    if sys.platform == 'win32':
        import subprocess as sp
        creationflags = sp.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).parent.parent / 'mcp' / 'mcp_server.py')],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1,
        creationflags=creationflags
    )

    errors = []
    request_id = 0

    def send_request(method: str, params: dict = None):
        """发送 MCP 请求"""
        nonlocal request_id
        request_id += 1

        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params or {}
        }

        proc.stdin.write(json.dumps(request) + '\n')
        proc.stdin.flush()

        response_line = proc.stdout.readline()
        if not response_line:
            raise Exception("MCP Server 未响应")

        response = json.loads(response_line)

        if 'error' in response:
            raise Exception(response['error'].get('message', 'Unknown error'))

        return response.get('result')

    def call_tool(tool_name: str, arguments: dict = None):
        """调用 MCP tool"""
        result = send_request('tools/call', {
            'name': f'mcp__bug_book__{tool_name}',
            'arguments': arguments or {}
        })

        if isinstance(result, dict) and 'content' in result:
            content = result['content'][0]['text']
            if not content or content.strip() == '':
                return []
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 返回非 JSON 格式（如 organize_bugs 的报告）
                return content
        return result

    def test(name, func):
        """执行测试"""
        try:
            result = func()
            print(f"✓ {name}: {str(result)[:100] if isinstance(result, str) else str(result)[:100]}")
            return result
        except Exception as e:
            print(f"✗ {name}: {e}")
            errors.append((name, str(e)))
            return None

    try:
        # 初始化
        test("initialize", lambda: send_request('initialize'))
        test("tools/list", lambda: send_request('tools/list'))

        # ============================================================
        # 1. save_bugs - add 模式
        # ============================================================
        add_result = test("save_bugs/add (最小字段)", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'add',
                'title': '测试Bug',
                'phenomenon': '测试现象'
            }]
        }))

        if add_result is None or (isinstance(add_result, dict) and add_result.get('error')):
            print(f"\n{storage_type.upper()} 后端基础功能失败")
            return errors

        # 解析 add 结果获取 bug_id
        if isinstance(add_result, dict) and 'results' in add_result:
            bug_id = add_result['results'][0]['id']
        else:
            bug_id = add_result['id']

        # ============================================================
        # 2. save_bugs - update_fields 模式
        # ============================================================
        test("save_bugs/update_fields", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'update_fields',
                'id': bug_id,
                'title': '更新后的标题'
            }]
        }))

        # ============================================================
        # 3. get_bug_detail
        # ============================================================
        test("get_bug_detail", lambda: call_tool('get_bug_detail', {'bug_id': bug_id}))

        # ============================================================
        # 4. search_bugs - 各种模式
        # ============================================================
        test("search_bugs/keyword", lambda: call_tool('search_bugs', {
            'mode': 'keyword',
            'keyword': '测试'
        }))

        test("search_bugs/recent", lambda: call_tool('search_bugs', {
            'mode': 'recent',
            'days': 7
        }))

        test("search_bugs/high_score", lambda: call_tool('search_bugs', {
            'mode': 'high_score',
            'min_score': 0
        }))

        test("search_bugs/critical", lambda: call_tool('search_bugs', {
            'mode': 'critical',
            'limit': 5
        }))

        test("search_bugs/custom", lambda: call_tool('search_bugs', {
            'mode': 'custom',
            'status': 'active',
            'min_score': 0
        }))

        # ============================================================
        # 5. save_bugs - add_paths 模式
        # ============================================================
        test("save_bugs/add_paths", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'add_paths',
                'id': bug_id,
                'paths': [{'file': 'test.py', 'functions': ['f1', 'f2']}]
            }]
        }))

        # ============================================================
        # 6. save_bugs - increment_scores 模式
        # ============================================================
        test("save_bugs/increment_scores", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'increment_scores',
                'id': bug_id,
                'scores': {'occurrences': 1.0}
            }]
        }))

        # ============================================================
        # 7. save_bugs - add_impacts 模式
        # ============================================================
        test("save_bugs/add_impacts", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'add_impacts',
                'id': bug_id,
                'impacts': [{
                    'solution_change': '修改了session处理',
                    'impact_description': '导致购物车失效',
                    'impact_type': 'regression',
                    'severity': 8
                }]
            }]
        }))

        # ============================================================
        # 8. save_bugs - delete 模式（软删除）
        # ============================================================
        test("save_bugs/delete", lambda: call_tool('save_bugs', {
            'bugs': [{
                'mode': 'delete',
                'id': bug_id
            }]
        }))

        # ============================================================
        # 9. organize_bugs
        # ============================================================
        test("organize_bugs", lambda: call_tool('organize_bugs', {}))

    finally:
        proc.terminate()
        proc.wait(timeout=5)
        cleanup_test_data(temp_dir)

    print(f"\n{storage_type.upper()} 后端测试结果: {len(errors)} 个错误")
    for name, error in errors:
        print(f"  - {name}: {error}")

    return errors


def main():
    print("="*60)
    print("MCP Server 端到端测试")
    print("="*60)

    # 准备测试数据
    print("\n[准备测试数据]")
    transcript_path, temp_dir = prepare_test_data()
    print(f"✓ 测试目录: {temp_dir}")

    # 测试 JSONL 后端
    jsonl_errors = run_mcp_test("jsonl", temp_dir)

    # 总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    print(f"JSONL 后端: {len(jsonl_errors)} 个错误")

    if jsonl_errors:
        print("\nJSONL 错误详情:")
        for name, error in jsonl_errors:
            print(f"  - {name}: {error}")

    total_errors = len(jsonl_errors)
    if total_errors == 0:
        print("\n✓ 所有测试通过！MCP Server 完全兼容")
    else:
        print(f"\n✗ 共 {total_errors} 个错误需要修复")

    return total_errors


if __name__ == '__main__':
    sys.exit(main())