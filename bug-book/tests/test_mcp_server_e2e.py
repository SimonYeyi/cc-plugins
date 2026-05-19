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


def prepare_transcript_with_cache(file_path: str, temp_dir: str):
    """准备带有 recall 缓存标记的 transcript"""
    transcript_path = Path(temp_dir) / 'test_transcript.json'
    transcript_path.write_text(json.dumps({
        "messages": [
            {"role": "user", "content": "编辑 " + file_path},
            {"role": "assistant", "content": "已召回 1 个相关 bug [recall " + file_path + "]"}
        ]
    }, ensure_ascii=False))
    return str(transcript_path)


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

    # Windows 下需要特殊处理
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
        
        # 读取响应
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

        # Hook handler 返回 {content, additionalContext} 格式
        if isinstance(result, dict) and 'additionalContext' in result:
            # 返回 hook handler 的原始结果（不解析 JSON）
            return result

        # 普通 tool 返回 {content: [{text: JSON字符串}]} 格式
        if isinstance(result, dict) and 'content' in result:
            content = result['content'][0]['text']
            if not content or content.strip() == '':
                return []  # 空响应返回空列表
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                raise Exception(f"Invalid JSON response: {content[:100]}")
        return result
    
    def test(name, func):
        """执行测试"""
        try:
            result = func()
            print(f"✓ {name}: {str(result)[:100]}")
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
        # 1. CRUD 操作
        # ============================================================
        add_result = test("add_bug", lambda: call_tool('add_bug', {
            'title': '测试Bug',
            'phenomenon': '测试现象',
            'root_cause': '测试根因',
            'solution': '测试方案',
            'paths': ['test.py:10'],
            'tags': ['test'],
            'keywords': ['测试']
        }))
        
        if add_result is None or len(add_result) < 2:
            print(f"\n{storage_type.upper()} 后端基础功能失败")
            return errors
        
        bug_id = add_result[0]
        
        test("get_bug_detail", lambda: call_tool('get_bug_detail', {'bug_id': bug_id}))
        test("count_bugs", lambda: call_tool('count_bugs'))
        test("list_bugs", lambda: call_tool('list_bugs', {'limit': 5}))
        
        test("update_bug", lambda: call_tool('update_bug', {'bug_id': bug_id, 'title': '更新后的标题'}))
        test("increment_score", lambda: call_tool('increment_score', {'bug_id': bug_id, 'dimension': 'occurrences', 'delta': 1.0}))
        test("mark_invalid", lambda: call_tool('mark_invalid', {'bug_id': bug_id, 'reason': '测试标记失效'}))
        
        # ============================================================
        # 3. 影响关系管理
        # ============================================================
        impact_result = test("add_impact", lambda: call_tool('add_impact', {
            'source_bug_id': bug_id,
            'impacted_path': 'affected.py',
            'impact_type': 'regression',
            'description': '测试影响',
            'severity': 7
        }))
        
        test("get_bug_impacts", lambda: call_tool('get_bug_impacts', {'bug_id': bug_id}))
        test("get_impacted_bugs", lambda: call_tool('get_impacted_bugs', {'file_path': 'affected.py'}))
        
        if impact_result and isinstance(impact_result, (list, tuple)) and len(impact_result) > 0:
            impact_id = impact_result[0]
            test("delete_impact", lambda: call_tool('delete_impact', {'impact_id': impact_id, 'prevention_delta': 1.0}))
        elif impact_result and isinstance(impact_result, int):
            # add_impact 返回的是 impact_id（整数）
            test("delete_impact", lambda: call_tool('delete_impact', {'impact_id': impact_result, 'prevention_delta': 1.0}))
        
        # 重新添加影响用于后续测试
        test("add_impact_for_update", lambda: call_tool('add_impact', {
            'source_bug_id': bug_id,
            'impacted_path': 'old/path.py',
            'impact_type': 'side_effect',
            'severity': 5
        }))
        test("update_impacted_paths", lambda: call_tool('update_impacted_paths', {
            'old_path': 'old/path.py',
            'new_path': 'new/path.py'
        }))
        
        # ============================================================
        # 4. 搜索功能
        # ============================================================
        test("search_by_keyword", lambda: call_tool('search_by_keyword', {'keyword': '测试'}))
        test("search_by_tag", lambda: call_tool('search_by_tag', {'tag': 'test'}))
        test("search_recent", lambda: call_tool('search_recent', {'days': 7, 'limit': 10}))
        test("search_high_score", lambda: call_tool('search_high_score', {'min_score': 0, 'limit': 10}))
        test("search_top_critical", lambda: call_tool('search_top_critical', {'limit': 5}))
        test("search_recent_unverified", lambda: call_tool('search_recent_unverified', {'days': 7, 'limit': 10}))
        test("search_by_status_and_score", lambda: call_tool('search_by_status_and_score', {
            'status': 'active',
            'min_score': 0,
            'max_score': 100,
            'limit': 10
        }))
        
        # ============================================================
        # 5. 召回功能
        # ============================================================
        # recall_by_path 已改为内部使用
        # test("recall_by_path", lambda: call_tool('recall_by_path', {'file_path': 'test.py', 'limit': 10}))
        # recall_by_path_full 已改为内部使用，改为测试 recall_by_path_for_hook
        # test("recall_by_path_full", lambda: call_tool('recall_by_path_full', {'file_path': 'test.py', 'limit': 10}))
        test("recall_by_pattern", lambda: call_tool('recall_by_pattern', {'pattern': 'test/*', 'limit': 10}))

        # ============================================================
        # 6. 高级功能
        # ============================================================
        test("list_unverified_old", lambda: call_tool('list_unverified_old', {'days': 30, 'limit': 10}))
        test("check_path_valid", lambda: call_tool('check_path_valid', {'path': 'test.py'}))
        # migrate_bug_paths_after_refactor 已改为内部使用，改为测试 migrate_from_bash_command
        # test("migrate_bug_paths_after_refactor", lambda: call_tool('migrate_bug_paths_after_refactor', {
        #     'old_path': 'test.py',
        #     'new_path': 'migrated/test.py'
        # }))

        # ============================================================
        # 7. Hook 专用功能
        # ============================================================
        # TC-H01: recall_by_path_for_hook - 测试缓存机制

        # Step 1: 准备 bug 测试数据
        test("add_bug_for_hook", lambda: call_tool('add_bug', {
            'title': 'Hook测试Bug',
            'phenomenon': '测试现象',
            'root_cause': '测试根因',
            'solution': '测试方案',
            'paths': ['test.py:10'],
            'recalls': ['test.py'],
            'tags': ['test'],
            'keywords': ['测试']
        }))

        # Step 2: 第一次调用应返回 bug（transcript 无缓存标记）
        # 使用 prepare_test_data 创建的初始 transcript（无 recall 标记）
        transcript_path = str(Path(temp_dir) / 'test_transcript.json')
        result1 = test("recall_by_path_for_hook_1st", lambda: call_tool('recall_by_path_for_hook', {
            'file_path': 'test.py',
            'transcript_path': transcript_path,
            'limit': 10
        }))

        # Step 3: 写入带有 recall 标记的 transcript（模拟缓存生效）
        prepare_transcript_with_cache('test.py', temp_dir)

        # Step 4: 第二次调用应跳过（transcript 有缓存标记）
        result2 = test("recall_by_path_for_hook_2nd", lambda: call_tool('recall_by_path_for_hook', {
            'file_path': 'test.py',
            'transcript_path': transcript_path,
            'limit': 10
        }))

        # Step 5: 测试超过 10 轮缓存失效
        # 写入 12 轮对话 + recall 标记在第 1 轮（已超出 10 轮窗口）
        # lookback=10 检查最后 20 条消息，缓存标记在第 1 轮（更早），应该被忽略
        transcript_path_expired = Path(temp_dir) / 'test_transcript_expired.json'
        messages = [
            # 第 1 轮：Claude 回复中包含 recall 标记（但已超出 lookback 窗口）
            {"role": "user", "content": "编辑 test.py"},
            {"role": "assistant", "content": "已召回 1 个相关 bug [recall test.py]"},
        ]
        # 第 2-12 轮：正常对话（11 轮 x 2 = 22 条消息）
        for i in range(2, 13):
            messages.append({"role": "user", "content": f"轮次 {i}"})
            messages.append({"role": "assistant", "content": f"回复 {i}"})
        # 总共 2 + 22 = 24 条消息，lookback=10 检查最后 20 条，不包含第 1 轮的缓存
        transcript_path_expired.write_text(json.dumps({"messages": messages}, ensure_ascii=False))

        result3 = test("recall_by_path_for_hook_3rd_expired", lambda: call_tool('recall_by_path_for_hook', {
            'file_path': 'test.py',
            'transcript_path': str(transcript_path_expired),
            'limit': 10
        }))

        # TC-H02: migrate_from_bash_command - 测试从 bash 命令提取路径并迁移
        test("migrate_from_bash_command", lambda: call_tool('migrate_from_bash_command', {
            'command': 'mv old.py new.py'
        }))
        
        # ============================================================
        # 清理
        # ============================================================
        test("delete_bug", lambda: call_tool('delete_bug', {'bug_id': bug_id}))
        
    finally:
        # 关闭进程
        proc.terminate()
        proc.wait(timeout=5)
        # 清理临时目录
        cleanup_test_data(temp_dir)
    
    print(f"\n{storage_type.upper()} 后端测试结果: {len(errors)} 个错误")
    for name, error in errors:
        print(f"  - {name}: {error}")
    
    return errors


def main():
    print("="*60)
    print("MCP Server 端到端测试")
    print("="*60)

    # 准备测试数据（使用系统临时目录）
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
