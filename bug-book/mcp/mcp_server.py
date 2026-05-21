#!/usr/bin/env python3
"""bug-book MCP Server：提供所有 bug 操作的 MCP tool"""

import json
import sys
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

# 导入
from bug_service import BugService
from config import find_project_root


# ---------------------------------------------------------------------------
# MCP Server 实现
# ---------------------------------------------------------------------------

class MCPServer:
    """bug-book MCP Server"""

    def __init__(self, storage_path=None):
        self.storage_path = storage_path
        self.service = BugService()

    def handle_request(self, request: dict) -> dict:
        """处理 MCP 请求"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')

        # MCP 初始化请求
        if method == 'initialize':
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {
                        'tools': { 'listChanged': False },
                    },
                    'serverInfo': {
                        'name': 'bug-book',
                        'version': '1.0.0'
                    }
                }
            }
        elif method == 'tools/list':
            return {'jsonrpc': '2.0', 'id': request_id, 'result': { 'tools': self.list_tools() }}
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            return {'jsonrpc': '2.0', 'id': request_id, 'result': self.call_tool(tool_name, arguments)}
        elif method == 'ping':
            # MCP ping 用于检测连通性，必须返回空 result
            return {'jsonrpc': '2.0', 'id': request_id, 'result': {}}
        elif method == 'notifications/initialized':
            # 客户端初始化完成确认，notification 不需要响应
            return None
        else:
            return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32601, 'message': f'Unknown method: {method}'}}

    def list_tools(self) -> list:
        """返回所有可用工具"""
        return [
            # 1. save_bugs - 统一保存接口（支持批量）
            self._tool('save_bugs', '保存 Bug（新增、更新或删除，支持批量）',
                '保存 Bug（新增、更新或删除），支持批量操作。\n\n'
                '触发场景：\n'
                '- 整理错题集时修正 bug 详情（如标记失效、更新路径、修改状态等）\n'
                '注意：日常新增 bug 由 skill 自动完成，无需手动调用此工具。'),

            # 2. search_bugs - 统一搜索
            self._tool('search_bugs', '统一搜索',
                '统一搜索接口，支持多种搜索模式和分页。\n\n'
                '触发场景：\n'
                '- 搜索/查找 bug（如"查一下 session 相关的 bug"）\n'
                '- 查询特定模块的问题（使用 module 模式）\n'
                '- 查看高分/未验证 bugs\n'),
                        
            # 3. organize_bugs - 整理错题集
            self._tool('organize_bugs', '整理错题集',
                '整理 bug-book 数据库，执行以下操作：\n'
                '1. 压缩文件（移除已删除记录，相同ID只保留最后一条）\n'
                '2. 检查路径有效性（标记失效路径）\n'
                '3. 检查长期未验证记录（超过30天）\n'
                '4. 生成整理报告和统计信息\n\n'
                '触发场景：\n'
                '- 用户明确要求整理（如"帮我整理一下错题集"）\n'
                '- 用户要求清理失效条目或归类重复问题\n'
                '- 定期检查维护（建议每周一次）\n\n'
                '注意：此操作不会自动修改数据，只返回整理报告和建议。'),

            # 4. get_bug_detail - 获取详情
            self._tool('get_bug_detail', '获取 bug 详情',
                '获取 bug 的完整信息，包括 scores、paths、tags、module_patterns、impacts 等。\n\n'
                '触发场景：\n'
                '- 需要获取 bug 的详细信息（如“bug #5 的解决方案是什么”）\n'
                '- 需要查看 bug 的具体字段信息\n'),

        ]

    def _tool(self, name: str, description: str, long_description: str = '') -> dict:
        """构建 tool 定义"""
        return {
            'name': f'mcp__bug_book__{name}',
            'description': long_description or description,
            'inputSchema': self._get_input_schema(name),
        }

    def _get_input_schema(self, tool_name: str) -> dict:
        """获取 tool 的输入 schema"""
        schemas = {
            'save_bugs': {
                'type': 'object',
                'description': '保存 Bug（新增、更新或删除），支持批量操作',
                'properties': {
                    'bugs': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'description': 'Bug ID（add 模式禁止传入，其他 mode 必填）'},
                                'mode': {
                                    'type': 'string',
                                    'enum': [
                                        'add', 'update_fields', 'delete',
                                        'add_impacts', 'remove_impacts', 'replace_impacts',
                                        'add_paths', 'remove_paths', 'replace_paths',
                                        'add_module_patterns', 'remove_module_patterns', 'replace_module_patterns',
                                        'add_keywords', 'remove_keywords', 'replace_keywords',
                                        'add_tags', 'remove_tags', 'replace_tags',
                                        'increment_scores', 'decrement_scores', 'replace_scores',
                                    ],
                                    'description': '操作模式：add(新增)/update_fields(更新字段)/delete(删除)/add_impacts(添加影响)/remove_impacts(移除影响)/replace_impacts(替换影响)/add_paths(添加路径)/remove_paths(移除路径)/replace_paths(替换路径)/add_module_patterns(添加模块)/remove_module_patterns(移除模块)/replace_module_patterns(替换模块)/add_keywords(添加关键词)/remove_keywords(移除关键词)/replace_keywords(替换关键词)/add_tags(添加标签)/remove_tags(移除标签)/replace_tags(替换标签)/increment_scores(累加分数)/decrement_scores(扣减分数)/replace_scores(替换分数)'
                                },
                                'title': {'type': 'string', 'description': '标题（add 模式必填）'},
                                'phenomenon': {'type': 'string', 'description': '现象描述（add 模式必填）'},
                                'root_cause': {'type': 'string', 'description': '根本原因（update_fields 模式可选）'},
                                'solution': {'type': 'string', 'description': '解决方案（update_fields 模式可选）'},
                                'test_case': {'type': 'string', 'description': '测试用例（update_fields 模式可选）'},
                                'status': {'type': 'string', 'enum': ['active', 'resolved', 'invalid'], 'description': '状态（update_fields 模式可选）'},
                                'verified': {'type': 'boolean', 'description': '是否验证（update_fields 模式可选）'},
                                'verified_at': {'type': 'string', 'description': '验证时间（update_fields 模式可选）'},
                                'verified_by': {'type': 'string', 'description': '验证人（update_fields 模式可选）'},

                                'impacts': {
                                    'type': 'array',
                                    'description': '影响关系数组（add_impacts/replace_impacts 模式必填）',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'solution_change': {'type': 'string', 'description': '产生影响的详细具体的方案'},
                                            'impact_description': {'type': 'string', 'description': '方案导致的具体影响描述'},
                                            'impact_type': {'type': 'string', 'enum': ['regression', 'side_effect', 'dependency'], 'description': '影响类型'},
                                            'severity': {'type': 'integer', 'minimum': 0, 'maximum': 10, 'description': '严重程度（0-10）'},
                                        },
                                        'required': ['solution_change', 'impact_description', 'impact_type', 'severity']
                                    }
                                },
                                'impact_ids': {'type': 'array', 'items': {'type': 'integer'}, 'description': '要移除的影响关系ID数组（remove_impacts 模式必填）'},

                                'paths': {
                                    'type': 'array',
                                    'description': 'Bug 出现的位置（add_paths/replace_paths/remove_paths 模式必填）。每个元素为对象 {file, functions?}，functions 可选；add_paths 时必须传 functions 精确到函数；remove_paths 时不传 functions 删除整个文件，传 functions 只删除指定函数',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'file': {'type': 'string', 'description': '文件路径'},
                                            'functions': {'type': 'array', 'items': {'type': 'string'}, 'description': '函数名列表（可选）'},
                                        },
                                        'required': ['file']
                                    }
                                },

                                'module_patterns': {'type': 'array', 'items': {'type': 'string'}, 'description': '模块模式数组（add_module_patterns/remove_module_patterns/replace_module_patterns 模式必填）'},

                                'keywords': {'type': 'array', 'items': {'type': 'string'}, 'description': '关键词数组（add_keywords/remove_keywords/replace_keywords 模式必填）'},

                                'tags': {'type': 'array', 'items': {'type': 'string'}, 'description': '标签数组（add_tags/remove_tags/replace_tags 模式必填）'},

                                'scores': {
                                    'type': 'object',
                                    'description': '分数字典（increment_scores/decrement_scores/replace_scores 模式必填）',
                                    'properties': {
                                        'importance': {'type': 'number', 'description': '重要性分数'},
                                        'complexity': {'type': 'number', 'description': '复杂度分数'},
                                        'scope': {'type': 'number', 'description': '影响范围分数'},
                                        'difficulty': {'type': 'number', 'description': '修复难度分数'},
                                        'occurrences': {'type': 'number', 'description': '出现次数分数'},
                                        'emotion': {'type': 'number', 'description': '情绪影响分数'},
                                        'prevention': {'type': 'number', 'description': '预防价值分数'},
                                    },
                                },
                            },
                            'required': ['mode'],
                        },
                    },
                },
            },

            'search_bugs': {
                'type': 'object',
                'description': '统一搜索接口，支持多种搜索模式和分页',
                'properties': {
                    'mode': {
                        'type': 'string',
                        'enum': ['keyword', 'tag', 'recent', 'high_score', 'critical', 'unverified', 'custom', 'module'],
                        'description': '搜索模式：keyword(关键词)/tag(标签)/recent(最近)/high_score(高分)/critical(严重)/unverified(未验证)/custom(自定义)/module(模块搜索)'
                    },
                    'keyword': {'type': 'string', 'description': '搜索关键词（keyword 模式必填）'},
                    'tag': {'type': 'string', 'description': '标签名称（tag 模式必填）'},
                    'days': {'type': 'integer', 'default': 7, 'description': '天数（recent/unverified 模式使用）'},
                    'min_score': {'type': 'number', 'description': '最低分数（high_score/custom 模式使用）'},
                    'max_score': {'type': 'number', 'description': '最高分数（custom 模式使用）'},
                    'status': {'type': 'string', 'enum': ['active', 'resolved', 'invalid'], 'description': '状态过滤（custom 模式使用）'},
                    'verified': {'type': 'boolean', 'description': '验证状态过滤（custom 模式使用）'},
                    'order_by': {'type': 'string', 'enum': ['score', 'created_at', 'updated_at'], 'default': 'score', 'description': '排序字段（custom 模式使用）'},
                    'pattern': {'type': 'string', 'description': '模块匹配（module 模式必填，如 src/utils/*.ts）'},
                    'limit': {'type': 'integer', 'default': 20, 'minimum': 1, 'maximum': 100, 'description': '每页数量'},
                    'offset': {'type': 'integer', 'default': 0, 'minimum': 0, 'description': '偏移量'},
                },
                'required': ['mode'],
            },

            'organize_bugs': {
                'type': 'object',
                'description': '整理错题集：压缩文件、检查路径有效性、检查长期未验证记录、生成统计报告',
                'properties': {},
            },
            
            'get_bug_detail': {
                'type': 'object',
                'description': '获取 Bug 详情，包含完整的现象、根因、解决方案等信息',
                'properties': {'bug_id': {'type': 'integer'}},
                'required': ['bug_id'],
            },
        }
        return schemas.get(tool_name, {'type': 'object', 'properties': {}})

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """调用工具"""
        # 移除前缀
        if tool_name.startswith('mcp__bug_book__'):
            tool_name = tool_name[15:]

        try:
            result = self._call(tool_name, arguments)

            # Hook 工具已返回 MCP 格式，直接返回
            if isinstance(result, dict) and 'content' in result:
                return result

            # 普通工具统一封装为 MCP 标准格式
            return {'content': [{'type': 'text', 'text': json.dumps(result, ensure_ascii=False)}]}
        except Exception as e:
            # 后端异常统一转换为 MCP 错误格式
            return {'content': [{'type': 'text', 'text': str(e)}], 'isError': True}

    def _call(self, tool_name: str, args):
        """实际调用函数（通过后端实例）"""
        functions = {
            'save_bugs': lambda: self.service.save_bugs(args),
            'search_bugs': lambda: self.service.search_bugs(**args),
            'organize_bugs': lambda: self.service.organize_bugs(),
            'get_bug_detail': lambda: self.service.get_bug_detail(args['bug_id']),
            'recall_for_hook': lambda: self._handle_recall_for_hook(args['file_path'], args['transcript_path'], args.get('limit', 10)),
            'migrate_path_for_hook': lambda: self._handle_migrate_path_for_hook(args['command']),
        }

        func = functions.get(tool_name)
        if not func:
            raise ValueError(f'Unknown tool: {tool_name}')

        return func()

    def _handle_recall_for_hook(self, file_path: str, transcript_path: str, limit: int = 10):
        """为Hook返回hookSpecificOutput格式"""
        # 将绝对路径转换为相对路径
        abs_file = Path(file_path).resolve()
        rel_file = str(abs_file.relative_to(find_project_root()))

        # 1. 检查是否在最近 10 轮内已召回
        if self._has_recent_recall(transcript_path, rel_file, lookback=10):
            return {
                "content": [{"type": "text", "text": json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": "最近对话中已召回过该文件相关 Bug，请参考历史 Bug 信息，防止产生回归问题"
                    }
                }, ensure_ascii=False)}]
            }

        # 2. 调用后端召回（使用相对路径）
        related_bugs = self.service.recall_by_path(rel_file, limit=limit)

        if not related_bugs:
            return {
                "content": [{"type": "text", "text": rel_file + " 文件下还没出现过 Bug" }]
            }

        recall_tag = "已召回 " + str(len(related_bugs)) + " 个相关 bug [recall " + rel_file + "]"
        return {
            "content": [{"type": "text", "text": json.dumps({
                "systemMessage": recall_tag,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": json.dumps(related_bugs, ensure_ascii=False)
                }
            }, ensure_ascii=False)}]
        }

    def _has_recent_recall(self, transcript_path: str, file_path: str, lookback: int = 10) -> bool:
        """检查 transcript 中最近 N 轮是否已有该 path 的 recall"""
        try:
            path = Path(transcript_path)
            if not path.exists():
                return False

            # 读取最后 N*3 行（预留足够上下文）
            lines = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    lines.append(line)
            
            # 只检查最近的记录
            recent_lines = lines[-lookback * 3:]
            
            # 查找 PostToolUse hook 的 system_message 或 additional_context
            for line in recent_lines:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    event = json.loads(line)
                    
                    # 检查 hook_system_message 类型
                    if event.get('type') == 'attachment' and event.get('attachment', {}).get('type') == 'hook_system_message':
                        content = event['attachment'].get('content', '')
                        if f'[recall {file_path}]' in content:
                            return True
                    
                    # 检查 hook_success 中的 stdout（JSON 字符串）
                    elif event.get('type') == 'attachment' and event.get('attachment', {}).get('type') == 'hook_success':
                        stdout = event['attachment'].get('stdout', '')
                        if stdout:
                            try:
                                hook_data = json.loads(stdout)
                                system_msg = hook_data.get('systemMessage', '')
                                if f'[recall {file_path}]' in system_msg:
                                    return True
                            except (json.JSONDecodeError, AttributeError):
                                pass
                
                except (json.JSONDecodeError, KeyError):
                    continue

            return False
        except Exception:
            return False

    def _handle_migrate_path_for_hook(self, command: str):
        """从Bash命令提取路径并迁移"""
        import re

        # 提取 mv 或 git mv 命令的路径
        match = re.search(r'(?:git\s+)?mv\s+(\S+)\s+(\S+)', command)
        if not match:
            return {
                "content": [{"type": "text", "text": "不是文件重命名指令，不涉及路径迁移"}]
            }

        old_path, new_path = match.groups()

        # 调用后端迁移
        migrated_bugs = self.service.migrate_paths(old_path, new_path)

        migrated_count = len(migrated_bugs)
        summary = f"🔄 路径迁移完成，影响 {migrated_count} 个 bug 记录"
        detail = f"路径 `{old_path}` → `{new_path}` 已更新，{migrated_count} 个 bug 的 paths 已同步迁移"

        return {
            "content": [{"type": "text", "text": json.dumps({
                "systemMessage": summary,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": detail
                }
            }, ensure_ascii=False)}]
        }


# ---------------------------------------------------------------------------
# MCP Server 入口点（stdio 协议）
# ---------------------------------------------------------------------------

def main():
    server = MCPServer()

    # MCP stdio 协议循环
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = server.handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({'error': {'code': -32700, 'message': 'Invalid JSON'}}), flush=True)
        except Exception as e:
            print(json.dumps({'error': {'code': -32603, 'message': str(e)}}), flush=True)


if __name__ == '__main__':
    main()
