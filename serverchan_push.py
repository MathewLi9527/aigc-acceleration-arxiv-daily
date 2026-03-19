"""
Server酱微信推送模块
文档: https://sct.ftqq.com/
"""
import requests
import logging
from typing import Optional, List, Dict

logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)


class ServerChanPush:
    """Server酱推送类"""

    def __init__(self, send_key: str):
        """
        初始化Server酱推送
        :param send_key: Server酱的SendKey
        """
        self.send_key = send_key
        self.api_url = f"https://sctapi.ftqq.com/{send_key}.send"

    def push_text(self, title: str, desp: str = "") -> bool:
        """
        推送文本消息到微信
        :param title: 消息标题（必填，最长256字节）
        :param desp: 消息内容（选填，最长64KB，支持Markdown）
        :return: 是否推送成功
        """
        try:
            data = {
                "title": title,
                "desp": desp
            }
            response = requests.post(self.api_url, data=data, timeout=10)
            result = response.json()

            if result.get('code') == 0:
                logging.info(f"Server酱推送成功: {title}")
                return True
            else:
                logging.error(f"Server酱推送失败: {result.get('message', '未知错误')}")
                return False
        except Exception as e:
            logging.error(f"Server酱推送异常: {str(e)}")
            return False

    def push_papers_summary(self, papers: Dict[str, List[Dict]], date: str) -> bool:
        """
        推送论文摘要到微信
        :param papers: 论文数据字典 {类别: [论文列表]}
        :param date: 更新日期
        :return: 是否推送成功
        """
        # 构建标题
        title = f"📄 AIGC论文更新 {date}"

        # 构建内容（Markdown格式）
        desp_parts = [f"## AIGC Acceleration 论文日报\n"]
        desp_parts.append(f"**更新时间**: {date}\n\n")

        total_papers = 0
        for category, paper_list in papers.items():
            if paper_list:
                total_papers += len(paper_list)
                desp_parts.append(f"### {category} ({len(paper_list)}篇)\n")
                # 只显示前5篇论文，避免消息过长
                for i, paper in enumerate(paper_list[:5], 1):
                    title_text = paper.get('title', 'Unknown')
                    arxiv_id = paper.get('arxiv_id', '')
                    authors = paper.get('authors', '')

                    desp_parts.append(f"{i}. **{title_text}**\n")
                    if arxiv_id:
                        desp_parts.append(f"   - 论文: [arxiv:{arxiv_id}](http://arxiv.org/abs/{arxiv_id})\n")
                    if authors:
                        desp_parts.append(f"   - 作者: {authors}\n")
                    desp_parts.append("\n")

                if len(paper_list) > 5:
                    desp_parts.append(f"   *还有 {len(paper_list) - 5} 篇论文...*\n\n")

        desp_parts.append(f"\n---\n**总计**: {total_papers} 篇新论文\n")
        desp_parts.append(f"\n[查看完整列表](https://MathewLi9527.github.io/aigc-acceleration-arxiv-daily/)")

        desp = "".join(desp_parts)

        # 推送消息
        return self.push_text(title, desp)

    def push_simple_update(self, date: str, total_count: int, categories: List[str]) -> bool:
        """
        推送简单更新通知
        :param date: 更新日期
        :param total_count: 论文总数
        :param categories: 类别列表
        :return: 是否推送成功
        """
        title = f"📄 AIGC论文更新 {date}"

        desp = f"""## AIGC Acceleration 论文日报

**更新时间**: {date}

**新增论文**: {total_count} 篇

**监控类别**:
"""
        for cat in categories:
            desp += f"- {cat}\n"

        desp += f"""
---
[查看完整列表](https://MathewLi9527.github.io/aigc-acceleration-arxiv-daily/)
"""

        return self.push_text(title, desp)


def test_push(send_key: str):
    """测试推送功能"""
    pusher = ServerChanPush(send_key)
    return pusher.push_text(
        title="测试推送 - AIGC论文监控",
        desp="这是一条测试消息，如果您收到此消息，说明Server酱配置成功！\n\n✅ 配置正常"
    )


if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        test_key = sys.argv[1]
        test_push(test_key)
    else:
        print("Usage: python serverchan_push.py <send_key>")
