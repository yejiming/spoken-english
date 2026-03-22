#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path("/Users/kc/Desktop/项目资料/其他/测试")
EXAMPLES_DIR = ROOT / "examples"
AUDIO_DIR = ROOT / "audios"
SCRIPTS_DIR = ROOT / "scripts"

SITE_NAME = "Spoken English Patterns"
SITE_DESCRIPTION = "100 natural American sentence patterns across 5 daily speaking scenes."
AUDIO_VOICE = "Samantha"
AUDIO_RATE = "170"
AUDIO_PITCH_SHIFT = 4


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def ensure_dirs() -> None:
    for path in [EXAMPLES_DIR, AUDIO_DIR, SCRIPTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


SCENES = [
    {
        "id": "daily-life",
        "name_en": "Daily Life",
        "name_cn": "日常生活",
        "slots": [
            ("make coffee", "泡咖啡"),
            ("check my phone", "看手机"),
            ("take a shower", "洗个澡"),
            ("get dressed", "穿好衣服"),
            ("pack my bag", "收拾书包"),
            ("do a quick stretch", "简单拉伸一下"),
            ("water the plants", "给植物浇水"),
            ("tidy up the kitchen", "收拾厨房"),
            ("grab breakfast", "吃早餐"),
            ("walk the dog", "遛狗"),
            ("call my parents", "给父母打电话"),
            ("pay a few bills", "付几笔账单"),
            ("take out the trash", "倒垃圾"),
            ("open the windows", "打开窗户"),
            ("turn on some music", "放点音乐"),
            ("read a few pages", "读几页书"),
            ("make the bed", "整理床铺"),
            ("head out early", "早点出门"),
            ("heat up leftovers", "热一下剩菜"),
            ("wind down", "放松一下"),
        ],
        "lessons": [
            ("Morning Routine", "I usually ... before breakfast.", "我通常会在早餐前{slot_cn}。", "早晨固定习惯。", "用于描述每天早上的固定动作。"),
            ("About to Start", "I'm about to ...", "我正要{slot_cn}。", "马上就要开始做。", "用于说你马上要做某事。"),
            ("Just Need To", "I just need to ...", "我只是需要{slot_cn}。", "还差最后一步。", "用于轻松表达“我还差这个”。"),
            ("Been Meaning To", "I've been meaning to ...", "我一直想要{slot_cn}。", "想做很久但还没做。", "用于说你惦记了很久。"),
            ("Always Forget", "I always forget to ...", "我总是忘记{slot_cn}。", "总会忘掉的小事。", "用于说常常忘记的习惯。"),
            ("Morning Habit", "I try to ... every morning.", "我尽量每天早上都{slot_cn}。", "固定的晨间习惯。", "用于讲你每天早上的例行动作。"),
            ("After Dinner", "I like to ... after dinner.", "我喜欢晚饭后{slot_cn}。", "晚饭后的放松动作。", "用于说晚饭后爱做的事。"),
            ("Can’t Start", "I can't start my day without ...", "没有{slot_cn}，我就没法开始新的一天。", "生活里离不开的东西。", "用于强调某个习惯必不可少。"),
            ("In A Bit", "I'm going to ... in a bit.", "我过一会儿要{slot_cn}。", "稍后就要做。", "用于说自己等会儿要去做什么。"),
            ("Heading Out", "I'm heading out to ...", "我正要出去{slot_cn}。", "出门去办事。", "用于说你要出门做某事。"),
            ("Already Done", "I've already ...", "我已经{slot_cn}了。", "已经完成了。", "用于说明事情已经做完。"),
            ("Just Finished", "I just finished ...", "我刚刚完成了{slot_cn}。", "刚做完的事。", "用于说你刚结束某件事。"),
            ("Need A Minute", "I need a minute to ...", "我需要一点时间先{slot_cn}。", "先缓一下。", "用于表示你想先处理一点别的事。"),
            ("Still Trying", "I'm still trying to ...", "我还在努力{slot_cn}。", "还在适应或练习。", "用于说你还没完全搞定。"),
            ("Gotten Used To", "I've gotten used to ...", "我已经习惯了{slot_cn}。", "已经适应了。", "用于表达适应某种生活方式。"),
            ("Planning Later", "I'm planning to ... later.", "我打算待会儿{slot_cn}。", "稍后安排。", "用于说你晚点的计划。"),
            ("In The Habit", "I'm in the habit of ...", "我有{slot_cn}的习惯。", "固定习惯表达。", "用于描述长期养成的习惯。"),
            ("Rather Than Nothing", "I'd rather ... than do nothing.", "我宁愿{slot_cn}，也不想什么都不做。", "表达个人偏好。", "用于对比两种选择。"),
            ("Before I Leave", "I have to ... before I leave.", "我离开前得先{slot_cn}。", "出门前必须做。", "用于说离开前的必要动作。"),
            ("Winding Down", "I'm winding down by ...", "我靠{slot_cn}来放松收尾。", "晚上收尾放松。", "用于说你晚上怎么放松下来。"),
        ],
    },
    {
        "id": "work-school",
        "name_en": "Work & School",
        "name_cn": "工作学习",
        "slots": [
            ("finishing this report", "完成这份报告"),
            ("replying to those emails", "回复那些邮件"),
            ("the meeting prep", "会议准备"),
            ("taking notes", "做笔记"),
            ("the slides", "这些幻灯片"),
            ("asking for feedback", "征求反馈"),
            ("the spreadsheet", "这个表格"),
            ("the draft", "草稿"),
            ("the call setup", "电话会议安排"),
            ("the client follow-up", "客户跟进"),
            ("the deadline", "截止时间"),
            ("my files", "我的文件"),
            ("the typo", "这个错字"),
            ("class prep", "备课"),
            ("the comments", "这些批注"),
            ("the handout", "讲义"),
            ("the summary", "总结"),
            ("my notes", "我的笔记"),
            ("the assignment", "作业"),
            ("the presentation", "演示稿"),
        ],
        "lessons": [
            ("Working On", "I'm working on ... right now.", "我现在正在处理{slot_cn}。", "正在进行中的工作。", "用于说你此刻正在忙什么。"),
            ("Turn In", "I need to turn in ... today.", "我今天得交{slot_cn}。", "交作业/交材料。", "用于说今天必须提交的东西。"),
            ("Behind On", "I'm behind on ...", "我在{slot_cn}上落后了。", "进度有点拖后。", "用于表达进度落后。"),
            ("Help Me With", "Could you help me with ...?", "你能帮我处理{slot_cn}吗？", "需要别人搭把手。", "用于礼貌请求帮助。"),
            ("Waiting For", "I'm waiting for ...", "我在等{slot_cn}。", "在等回复或结果。", "用于说你正在等待。"),
            ("Follow Up", "I have to follow up on ...", "我得跟进{slot_cn}。", "后续跟进。", "用于说需要继续推进。"),
            ("Stay On Top", "I'm trying to stay on top of ...", "我想把{slot_cn}都跟上。", "不想漏掉进度。", "用于说你要保持掌控。"),
            ("Double Check", "I'm double-checking ...", "我在再次确认{slot_cn}。", "复核细节。", "用于说你在检查细节。"),
            ("Taking Care", "I'm taking care of ...", "我在处理{slot_cn}。", "正在收拾/处理事情。", "用于说你在办某件事。"),
            ("Meeting About", "I've got to prepare ... for the meeting.", "我得为了会议准备{slot_cn}。", "会议前要准备。", "用于说会前准备内容。"),
            ("Get This Done", "I need to get this ...", "我得把这个{slot_cn}弄好。", "把事情处理完。", "用于说要把事情做完。"),
            ("Supposed To", "I'm supposed to ... by noon.", "我应该在中午前{slot_cn}。", "按时完成。", "用于说你按计划应该做什么。"),
            ("Putting Together", "I'm putting together ...", "我在整理/准备{slot_cn}。", "拼装材料或内容。", "用于说你在组合资料。"),
            ("Sorting Out", "I'm still sorting out ...", "我还在理清{slot_cn}。", "还没完全确定。", "用于说你在处理复杂情况。"),
            ("Run This By", "I'm running this by ...", "我把这个先给{slot_cn}过目。", "先让别人看一下。", "用于征求意见。"),
            ("Make Sure", "I need to make sure I ...", "我得确保我{slot_cn}。", "必须确认没问题。", "用于强调你要确认。"),
            ("Setting Up", "I'm setting up ... now.", "我现在在安排{slot_cn}。", "正在搭建安排。", "用于说你在设置流程。"),
            ("Checking In", "I'm checking in on ...", "我在确认{slot_cn}的进展。", "看进度如何。", "用于跟进状态。"),
            ("Ask About", "I'd like to ask about ...", "我想问一下{slot_cn}。", "想礼貌询问。", "用于正式一点地发问。"),
            ("Pushing To Finish", "I'm pushing to finish ...", "我在加紧完成{slot_cn}。", "赶进度。", "用于说你在冲刺完成。"),
        ],
    },
    {
        "id": "social-plans",
        "name_en": "Social Plans",
        "name_cn": "社交安排",
        "slots": [
            ("grab dinner", "吃晚饭"),
            ("catch a movie", "看电影"),
            ("meet for coffee", "见面喝咖啡"),
            ("go for a walk", "散步"),
            ("check out the new place", "去看看那家新店"),
            ("hang out", "一起待着"),
            ("celebrate a little", "小小庆祝一下"),
            ("have a quick chat", "聊几句"),
            ("stop by later", "待会儿顺路过去"),
            ("pick you up", "接你"),
            ("swing by the cafe", "顺路去咖啡馆"),
            ("make a reservation", "订座位"),
            ("bring something to share", "带点吃的分享"),
            ("take a rain check", "改天再约"),
            ("stay in tonight", "今晚待在家"),
            ("head to the airport", "去机场"),
            ("join us after work", "下班后加入我们"),
            ("split the bill", "平摊账单"),
            ("grab drinks", "喝点东西"),
            ("plan something low-key", "计划轻松一点的活动"),
        ],
        "lessons": [
            ("Free Later", "Are you free to ... later?", "你晚点有空{slot_cn}吗？", "问对方是否有空。", "用于询问晚上或稍后能不能一起安排。"),
            ("Want To Tonight", "Do you want to ... tonight?", "你今晚想{slot_cn}吗？", "轻松邀约。", "用于直接发出邀请。"),
            ("Thinking Of", "I was thinking we could ...", "我在想我们可以{slot_cn}。", "一起商量计划。", "用于提出一个建议。"),
            ("After Work", "Let's ... after work.", "我们下班后{slot_cn}吧。", "下班后一起做。", "用于定一个简单计划。"),
            ("Meet You", "I can meet you at ...", "我可以在{slot_cn}见你。", "约好碰面地点。", "用于说明见面的时间地点。"),
            ("Figure Out When", "I'm trying to figure out when to ...", "我在想什么时候去{slot_cn}。", "还在定时间。", "用于安排时间。"),
            ("Should Probably", "We should probably ... first.", "我们最好先{slot_cn}。", "先做准备。", "用于建议先做某事。"),
            ("Let You Know", "I'll let you know if I can ...", "如果我能{slot_cn}，我会告诉你。", "先保留可能性。", "用于给对方一个答复。"),
            ("Confirm Whether", "I need to confirm whether we can ...", "我得确认我们能不能{slot_cn}。", "先确认安排。", "用于核实能否成行。"),
            ("Hoping To", "I'm hoping to ... this weekend.", "我希望这周末能{slot_cn}。", "周末愿望。", "用于说你很想做。"),
            ("Down To", "I'm down to ...", "我愿意{slot_cn}。", "口语里表示可以。", "用于表示你也愿意。"),
            ("Rather Than Stay In", "I'd rather ... than stay home.", "我宁愿{slot_cn}，也不想待在家。", "比较两个选择。", "用于表达更想出去。"),
            ("In The Mood For", "I'm in the mood for ...", "我现在想{slot_cn}。", "当下的兴趣。", "用于说你此刻想做什么。"),
            ("Making Plans", "I'm making plans to ...", "我在安排{slot_cn}的计划。", "正在计划。", "用于说你在组织安排。"),
            ("Waiting To Hear Back", "I'm waiting to hear back about ...", "我在等关于{slot_cn}的回复。", "等别人答复。", "用于说你在等消息。"),
            ("Can We Do", "Can we ... instead?", "我们能改成{slot_cn}吗？", "改方案。", "用于提出替代方案。"),
            ("Text You Later", "I'll text you when I'm done with ...", "我{slot_cn}做完后会发你消息。", "做完再联系。", "用于说结束后再通知。"),
            ("Keep Open", "I'm just trying to keep ... open.", "我只是想把{slot_cn}先留空。", "保留时间。", "用于先不要排满。"),
            ("Might Have To Cancel", "I might have to cancel if I can't make ...", "如果我不能赶上{slot_cn}，我可能得取消。", "有变数时说。", "用于保留取消可能。"),
            ("Don’t Forget", "Let's not forget to ...", "别忘了{slot_cn}。", "提醒彼此。", "用于温和提醒。"),
        ],
    },
    {
        "id": "problems-solutions",
        "name_en": "Problems & Solutions",
        "name_cn": "问题处理",
        "slots": [
            ("open the app", "打开应用"),
            ("log in", "登录"),
            ("send the file", "发送文件"),
            ("connect the printer", "连接打印机"),
            ("save the changes", "保存更改"),
            ("clear the cache", "清理缓存"),
            ("get the video to play", "让视频播放"),
            ("reset the password", "重设密码"),
            ("finish the upload", "完成上传"),
            ("charge the laptop", "给笔记本充电"),
            ("fix the microphone", "修好麦克风"),
            ("load the page", "加载页面"),
            ("open the attachment", "打开附件"),
            ("keep the meeting moving", "让会议继续推进"),
            ("use the old cable", "用那根旧电缆"),
            ("find a backup plan", "找备用方案"),
            ("the wifi to connect", "Wi-Fi 连接"),
            ("miss the deadline", "错过截止时间"),
            ("lose the progress", "丢掉进度"),
            ("get this sorted out", "把这件事处理好"),
        ],
        "lessons": [
            ("Can’t Seem To", "I can't seem to ...", "我就是没法{slot_cn}。", "怎么都不顺。", "用于说你反复失败。"),
            ("Went Wrong", "Something went wrong with ...", "{slot_cn}出了问题。", "事情出错了。", "用于说哪里出故障。"),
            ("Messed Up", "I think I messed up ...", "我觉得我把{slot_cn}搞砸了。", "承认失误。", "用于说自己可能弄错了。"),
            ("Figure Out Why", "Can you help me figure out why ...?", "你能帮我搞清楚为什么{slot_cn}吗？", "查原因。", "用于请别人帮你找问题。"),
            ("Trying To Fix", "I'm trying to fix ...", "我在尝试修好{slot_cn}。", "正在处理故障。", "用于说你正在修。"),
            ("Need To Restart", "I need to restart ...", "我得重启{slot_cn}。", "先重开试试。", "用于说需要重启。"),
            ("Keep Getting", "I keep getting an error when I ...", "每次我{slot_cn}的时候都会报错。", "反复出错。", "用于说总是遇到同样问题。"),
            ("Not Sure How", "I'm not sure how to ...", "我不太确定怎么{slot_cn}。", "还不清楚办法。", "用于说你不会操作。"),
            ("Working Around", "I'm working around ...", "我在绕开{slot_cn}。", "先用别的办法。", "用于临时解决。"),
            ("Need To Replace", "I need to replace ...", "我得换掉{slot_cn}。", "需要更换。", "用于说东西坏了要换。"),
            ("Have To Deal", "I have to deal with ...", "我得处理{slot_cn}。", "不得不处理麻烦。", "用于说你必须面对。"),
            ("Check Whether", "Let me check whether ...", "让我看看{slot_cn}是不是这样。", "先核实一下。", "用于先确认情况。"),
            ("Looking Into", "I'm looking into ...", "我在调查{slot_cn}。", "正在查找原因。", "用于说你在查。"),
            ("Trying Not To", "I'm trying not to ...", "我尽量不去{slot_cn}。", "避免更糟。", "用于克制自己。"),
            ("Better Way", "I need a better way to ...", "我需要一个更好的办法来{slot_cn}。", "想找更高效方法。", "用于说现在的方法不够好。"),
            ("Running Low", "I'm running low on ...", "我的{slot_cn}快不够了。", "资源不足。", "用于说东西快用完。"),
            ("Can’t Get", "I can't get ... to work.", "我没法让{slot_cn}正常工作。", "怎么都启动不了。", "用于说某物无法运行。"),
            ("Avoiding", "I'm trying to avoid ...", "我在尽量避免{slot_cn}。", "避免麻烦。", "用于说你想躲开问题。"),
            ("Just Want To Make Sure", "I just want to make sure ...", "我只是想确认{slot_cn}。", "先求稳。", "用于强调你要确认。"),
            ("See If We Can", "Let's see if we can ...", "我们看看能不能{slot_cn}。", "一起试试。", "用于一起找办法。"),
        ],
    },
    {
        "id": "feelings-opinions",
        "name_en": "Feelings & Opinions",
        "name_cn": "感受观点",
        "slots": [
            ("staying home tonight", "今晚待在家"),
            ("the new restaurant", "那家新餐厅"),
            ("working from home", "在家办公"),
            ("people being late", "别人迟到"),
            ("taking a break", "休息一下"),
            ("trying the spicy noodles", "尝试辣面"),
            ("having more time", "拥有更多时间"),
            ("moving to a new place", "搬去新地方"),
            ("keeping things simple", "保持简单"),
            ("a crowded room", "一个拥挤的房间"),
            ("the new layout", "新版布局"),
            ("getting up early", "早起"),
            ("sharing honest feedback", "给出坦诚反馈"),
            ("waiting too long", "等太久"),
            ("the weather today", "今天的天气"),
            ("speaking up in meetings", "在会议上发言"),
            ("spending money on that", "为那个花钱"),
            ("this kind of music", "这种音乐"),
            ("trying something new", "尝试新事物"),
            ("the way this feels", "这种感觉"),
        ],
        "lessons": [
            ("Feel Like", "I feel like ...", "我感觉{slot_cn}。", "带一点主观看法。", "用于说你的感觉或直觉。"),
            ("Kind Of Into", "I'm kind of into ...", "我有点喜欢{slot_cn}。", "不是特别强烈但喜欢。", "用于说你有点偏好。"),
            ("Not A Fan", "I'm not a fan of ...", "我不太喜欢{slot_cn}。", "明确不太喜欢。", "用于表达不喜欢。"),
            ("Rather Than", "I'd rather ... than ...", "我宁愿{slot_cn}，也不想……。", "比较偏好。", "用于表达“宁愿这样”。"),
            ("Really Into", "I'm really into ...", "我真的很喜欢{slot_cn}。", "强烈喜欢。", "用于说你很来电。"),
            ("Tired Of", "I'm honestly tired of ...", "说实话，我已经受够了{slot_cn}。", "开始厌倦。", "用于说你腻了。"),
            ("Pretty Sure", "I'm pretty sure ... is going to work.", "我很确定{slot_cn}会奏效。", "对结果有把握。", "用于表达很有信心。"),
            ("Don’t Mind", "I don't mind ...", "我不介意{slot_cn}。", "态度中性。", "用于说你不反感。"),
            ("Worth It", "I think it's worth ...", "我觉得{slot_cn}值得。", "值得一试。", "用于评价值不值得。"),
            ("Excited About", "I'm excited about ...", "我对{slot_cn}很兴奋。", "期待感很强。", "用于说你很期待。"),
            ("Worried About", "I'm worried about ...", "我担心{slot_cn}。", "有点担心。", "用于表达担忧。"),
            ("Agree With", "I'm not sure I agree with ...", "我不太确定我同不同意{slot_cn}。", "保留意见。", "用于表达不同看法。"),
            ("Can See Why", "I can see why people like ...", "我能理解为什么大家喜欢{slot_cn}。", "理解别人喜欢的原因。", "用于表示理解。"),
            ("Always Liked", "I've always liked ...", "我一直都喜欢{slot_cn}。", "长期偏好。", "用于说一直喜欢。"),
            ("Getting Used To", "I'm getting used to ...", "我正在慢慢习惯{slot_cn}。", "还在适应。", "用于说你在适应。"),
            ("Impressed By", "I'm impressed by ...", "我对{slot_cn}印象很深。", "觉得很厉害。", "用于表达赞叹。"),
            ("Not Convinced", "I'm not convinced that ...", "我还不太相信{slot_cn}。", "还没被说服。", "用于表达怀疑。"),
            ("I’d Say", "I'd say ...", "我会说{slot_cn}。", "给个大概判断。", "用于给出随口评价。"),
            ("Leaning Toward", "I'm leaning toward ...", "我更倾向于{slot_cn}。", "偏向某个选择。", "用于说你的倾向。"),
            ("Can’t Get Over", "I just can't get over ...", "我就是忘不掉{slot_cn}。", "很难释怀。", "用于说你一直惦记。"),
        ],
    },
]


def build_lessons():
    lessons = []
    for scene in SCENES:
        scene_lessons = []
        slots = scene["slots"]
        for idx, (title, pattern, cn_template, meaning, note) in enumerate(scene["lessons"]):
            start = (idx * 3) % len(slots)
            picks = [slots[(start + offset) % len(slots)] for offset in range(5)]
            lesson = {
                "scene_id": scene["id"],
                "scene_en": scene["name_en"],
                "scene_cn": scene["name_cn"],
                "title": title,
                "pattern": pattern,
                "meaning": meaning,
                "note": note,
                "cn_template": cn_template,
                "examples": [],
            }
            for ex_idx, (slot_en, slot_cn) in enumerate(picks, start=1):
                example_en = pattern.replace("...", slot_en, 1)
                example_cn = cn_template.format(slot_cn=slot_cn)
                lesson["examples"].append(
                    {
                        "index": ex_idx,
                        "slot_en": slot_en,
                        "slot_cn": slot_cn,
                        "english": example_en,
                        "chinese": example_cn,
                    }
                )
            lesson["slug"] = f"{len(lessons) + 1:02d}-{slugify(title)}"
            lessons.append(lesson)
            scene_lessons.append(lesson)
        scene["lesson_objects"] = scene_lessons
    return lessons


LESSONS = build_lessons()


def write_chunk_md():
    lines = ["# Spoken English Chunk", ""]
    for scene in SCENES:
        lines.append(f"## {scene['name_en']} / {scene['name_cn']}")
        lines.append("")
        for lesson in scene["lesson_objects"]:
            number = lesson["slug"].split("-", 1)[0]
            lines.append(f"{number}. {lesson['title']} - {lesson['pattern']}")
        lines.append("")
    (ROOT / "chunk.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_examples_md():
    for lesson in LESSONS:
        lines = [
            f"# {lesson['slug']} {lesson['title']}",
            "",
            f"- 场景: {lesson['scene_en']} / {lesson['scene_cn']}",
            f"- 句型: {lesson['pattern']}",
            f"- 意思: {lesson['meaning']}",
            f"- 用法: {lesson['note']}",
            "",
            "## 例句",
            "",
        ]
        for example in lesson["examples"]:
            lines.append(f"{example['index']}. {example['english']}")
            lines.append(f"   - {example['chinese']}")
            lines.append("")
        (EXAMPLES_DIR / f"{lesson['slug']}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run_command(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_spoken_text(pattern: str, slot_en: str) -> str:
    spoken = pattern.replace("...", slot_en, 1)
    return f"[[pbas +{AUDIO_PITCH_SHIFT}]] {spoken}"


def build_audio():
    if shutil.which("say") is None or shutil.which("afconvert") is None:
        raise RuntimeError("macOS say/afconvert not available")

    manifest = []
    temp_root = ROOT / ".tmp_audio"
    temp_root.mkdir(exist_ok=True)

    for lesson in LESSONS:
        lesson_audio_dir = AUDIO_DIR / lesson["slug"]
        lesson_audio_dir.mkdir(parents=True, exist_ok=True)
        for example in lesson["examples"]:
            out_path = lesson_audio_dir / f"{example['index']:02d}.wav"
            temp_aiff = temp_root / f"{lesson['slug']}-{example['index']:02d}.aiff"
            if out_path.exists():
                out_path.unlink()
            if temp_aiff.exists():
                temp_aiff.unlink()
            spoken_text = build_spoken_text(lesson["pattern"], example["slot_en"])
            run_command(["say", "-v", AUDIO_VOICE, "-r", AUDIO_RATE, "-o", str(temp_aiff), spoken_text])
            run_command(["afconvert", str(temp_aiff), str(out_path), "-f", "WAVE", "-d", "LEI16@22050"])
            if temp_aiff.exists():
                temp_aiff.unlink()
            manifest.append(
                {
                    "scene_id": lesson["scene_id"],
                    "lesson_slug": lesson["slug"],
                    "lesson_title": lesson["title"],
                    "example_index": example["index"],
                    "example_text": example["english"],
                    "audio_path": str(out_path.relative_to(ROOT)),
                }
            )

    if temp_root.exists():
        shutil.rmtree(temp_root)
    (SCRIPTS_DIR / "audio-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def write_data_js():
    payload = {
        "siteName": SITE_NAME,
        "siteDescription": SITE_DESCRIPTION,
        "scenes": [
            {
                "id": scene["id"],
                "nameEn": scene["name_en"],
                "nameCn": scene["name_cn"],
                "lessons": [
                    {
                        "slug": lesson["slug"],
                        "title": lesson["title"],
                        "pattern": lesson["pattern"],
                        "meaning": lesson["meaning"],
                        "note": lesson["note"],
                        "examples": [
                            {
                                "index": example["index"],
                                "english": example["english"],
                                "chinese": example["chinese"],
                                "slotEn": example["slot_en"],
                                "slotCn": example["slot_cn"],
                                "audio": f"audios/{lesson['slug']}/{example['index']:02d}.wav",
                            }
                            for example in lesson["examples"]
                        ],
                    }
                    for lesson in scene["lesson_objects"]
                ],
            }
            for scene in SCENES
        ],
    }
    (SCRIPTS_DIR / "data.js").write_text(
        "window.SPOKEN_ENGLISH_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )


def write_styles_css():
    css = """
:root {
  --bg: #F8FAF8;
  --text: #1F2937;
  --primary: #166534;
  --secondary: #A0AEC0;
  --accent: #C2410C;
  --card: rgba(255, 255, 255, 0.86);
  --border: rgba(22, 101, 52, 0.16);
  --shadow: 0 18px 40px rgba(31, 41, 55, 0.08);
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background:
    radial-gradient(circle at top left, rgba(194, 65, 12, 0.08), transparent 28%),
    radial-gradient(circle at bottom right, rgba(22, 101, 52, 0.10), transparent 24%),
    var(--bg);
  color: var(--text);
  font-family: "Avenir Next", "Gill Sans", "Noto Sans", "Helvetica Neue", Arial, sans-serif;
}

body {
  min-height: 100vh;
}

.shell {
  width: min(1500px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 18px 0 28px;
}

.hero {
  display: grid;
  gap: 10px;
  padding: 22px 24px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(248,250,248,0.82));
  box-shadow: var(--shadow);
}

.hero h1 {
  margin: 0;
  color: var(--primary);
  font-size: clamp(28px, 3vw, 44px);
  letter-spacing: -0.03em;
}

.hero p {
  margin: 0;
  color: rgba(31, 41, 55, 0.75);
  font-size: 15px;
  line-height: 1.6;
}

.scene-bar {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 14px 2px 4px;
  margin: 10px 0 16px;
  scrollbar-width: thin;
}

.scene-pill {
  appearance: none;
  border: 1px solid rgba(22, 101, 52, 0.18);
  background: rgba(255,255,255,0.75);
  color: var(--primary);
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: transform 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.scene-pill:hover { transform: translateY(-1px); }
.scene-pill.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.layout {
  display: grid;
  grid-template-columns: minmax(270px, 340px) 1fr;
  gap: 16px;
  align-items: start;
}

.panel {
  border: 1px solid var(--border);
  border-radius: 24px;
  background: var(--card);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow);
}

.sidebar {
  padding: 14px;
  position: sticky;
  top: 14px;
  max-height: calc(100vh - 28px);
  overflow: auto;
}

.sidebar h2, .detail h2 {
  margin: 4px 4px 10px;
  font-size: 18px;
  color: var(--primary);
}

.lesson-list {
  display: grid;
  gap: 8px;
}

.lesson-button {
  appearance: none;
  border: 1px solid transparent;
  text-align: left;
  width: 100%;
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.72);
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.lesson-button:hover {
  transform: translateY(-1px);
  border-color: rgba(194, 65, 12, 0.25);
}

.lesson-button.active {
  background: linear-gradient(135deg, rgba(22, 101, 52, 0.10), rgba(194, 65, 12, 0.08));
  border-color: rgba(22, 101, 52, 0.28);
}

.lesson-button .num {
  color: var(--accent);
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lesson-button .title {
  display: block;
  margin-top: 4px;
  font-weight: 700;
}

.lesson-button .pattern {
  display: block;
  margin-top: 4px;
  color: rgba(31, 41, 55, 0.7);
  font-size: 13px;
  line-height: 1.45;
}

.detail {
  padding: 18px 20px 22px;
}

.lesson-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.lesson-head h3 {
  margin: 0;
  font-size: clamp(24px, 2vw, 34px);
  line-height: 1.12;
  letter-spacing: -0.03em;
}

.lesson-head .scene-tag {
  color: var(--accent);
  font-weight: 700;
  white-space: nowrap;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.meta-card {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.76);
  border: 1px solid rgba(160, 174, 192, 0.18);
}

.meta-card .label {
  display: block;
  color: var(--secondary);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
  font-weight: 800;
}

.meta-card .value {
  font-size: 15px;
  line-height: 1.7;
}

.examples {
  display: grid;
  gap: 12px;
}

.example-card {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(22, 101, 52, 0.14);
}

.example-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.example-top .english {
  font-size: 16px;
  line-height: 1.5;
}

.example-top .english mark {
  background: rgba(194, 65, 12, 0.14);
  color: inherit;
  padding: 0 2px;
  border-radius: 4px;
}

.audio-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.audio-wrap audio {
  width: 240px;
  max-width: 45vw;
}

.duration {
  color: var(--secondary);
  font-size: 12px;
  min-width: 48px;
}

.example-cn {
  color: rgba(31, 41, 55, 0.86);
  font-size: 14px;
  line-height: 1.65;
}

.empty {
  padding: 22px;
  color: rgba(31, 41, 55, 0.68);
}

@media (max-width: 1080px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    max-height: none;
  }
}

@media (max-width: 720px) {
  .shell {
    width: min(100vw - 20px, 1000px);
  }

  .hero, .detail {
    padding-left: 16px;
    padding-right: 16px;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .lesson-head {
    flex-direction: column;
  }

  .example-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .audio-wrap audio {
    width: 100%;
    max-width: none;
  }
}
"""
    (SCRIPTS_DIR / "styles.css").write_text(css.strip() + "\n", encoding="utf-8")


def write_app_js():
    js = r"""
const data = window.SPOKEN_ENGLISH_DATA;

const state = {
  sceneIndex: 0,
  lessonIndex: 0,
  durations: new Map(),
};

const els = {};

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function highlightSentence(sentence, slot) {
  const safeSentence = escapeHtml(sentence);
  const safeSlot = escapeHtml(slot);
  if (!slot) return safeSentence;
  return safeSentence.replace(safeSlot, `<mark>${safeSlot}</mark>`);
}

function getCurrentScene() {
  return data.scenes[state.sceneIndex];
}

function getCurrentLesson() {
  return getCurrentScene().lessons[state.lessonIndex];
}

function renderScenes() {
  els.sceneBar.innerHTML = "";
  data.scenes.forEach((scene, idx) => {
    const button = document.createElement("button");
    button.className = `scene-pill ${idx === state.sceneIndex ? "active" : ""}`;
    button.textContent = `${scene.nameEn} / ${scene.nameCn}`;
    button.addEventListener("click", () => {
      state.sceneIndex = idx;
      state.lessonIndex = 0;
      renderAll();
    });
    els.sceneBar.appendChild(button);
  });
}

function renderLessons() {
  const scene = getCurrentScene();
  els.lessonList.innerHTML = "";
  scene.lessons.forEach((lesson, idx) => {
    const button = document.createElement("button");
    button.className = `lesson-button ${idx === state.lessonIndex ? "active" : ""}`;
    button.innerHTML = `
      <span class="num">${String(idx + 1).padStart(2, "0")} · ${escapeHtml(lesson.slug)}</span>
      <span class="title">${escapeHtml(lesson.title)}</span>
      <span class="pattern">${escapeHtml(lesson.pattern)}</span>
    `;
    button.addEventListener("click", () => {
      state.lessonIndex = idx;
      renderAll();
    });
    els.lessonList.appendChild(button);
  });
}

function renderLessonDetail() {
  const scene = getCurrentScene();
  const lesson = getCurrentLesson();
  els.detail.innerHTML = `
    <div class="lesson-head">
      <div>
        <div class="scene-tag">${escapeHtml(scene.nameEn)} / ${escapeHtml(scene.nameCn)}</div>
        <h3>${escapeHtml(lesson.title)}</h3>
      </div>
      <div class="scene-tag">#${String(state.lessonIndex + 1).padStart(2, "0")}</div>
    </div>
    <div class="meta-grid">
      <div class="meta-card">
        <span class="label">Sentence Pattern</span>
        <div class="value">${escapeHtml(lesson.pattern)}</div>
      </div>
      <div class="meta-card">
        <span class="label">Meaning / 意思</span>
        <div class="value">${escapeHtml(lesson.meaning)}</div>
      </div>
      <div class="meta-card" style="grid-column: 1 / -1;">
        <span class="label">Usage Note / 用法</span>
        <div class="value">${escapeHtml(lesson.note)}</div>
      </div>
    </div>
    <div class="examples">
      ${lesson.examples.map(renderExample).join("")}
    </div>
  `;
}

function renderExample(example) {
  const escaped = highlightSentence(example.english, example.slotEn);
  const duration = state.durations.get(example.audio);
  return `
    <article class="example-card">
      <div class="example-top">
        <div class="english">${escaped}</div>
        <div class="audio-wrap">
          <audio controls preload="metadata" data-audio="${escapeHtml(example.audio)}" src="${escapeHtml(example.audio)}"></audio>
          <div class="duration">${duration ? `${duration.toFixed(1)}s` : "..."}</div>
        </div>
      </div>
      <div class="example-cn">${escapeHtml(example.chinese)}</div>
    </article>
  `;
}

function preloadDurations() {
  document.querySelectorAll("audio[data-audio]").forEach((audioEl) => {
    audioEl.addEventListener("loadedmetadata", () => {
      const path = audioEl.dataset.audio;
      if (!path) return;
      state.durations.set(path, audioEl.duration);
      const card = audioEl.closest(".audio-wrap");
      if (card) {
        const durationEl = card.querySelector(".duration");
        if (durationEl) durationEl.textContent = `${audioEl.duration.toFixed(1)}s`;
      }
    }, { once: true });
  });
}

function renderAll() {
  renderScenes();
  renderLessons();
  renderLessonDetail();
  preloadDurations();
}

function init() {
  els.sceneBar = document.getElementById("sceneBar");
  els.lessonList = document.getElementById("lessonList");
  els.detail = document.getElementById("detail");
  renderAll();
}

document.addEventListener("DOMContentLoaded", init);
"""
    (SCRIPTS_DIR / "app.js").write_text(js.strip() + "\n", encoding="utf-8")


def write_index_html():
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{SITE_NAME}</title>
  <link rel="stylesheet" href="scripts/styles.css" />
</head>
<body>
  <div class="shell">
    <header class="hero">
      <h1>{SITE_NAME}</h1>
      <p>{SITE_DESCRIPTION}</p>
    </header>
    <nav class="scene-bar" id="sceneBar" aria-label="Scene selector"></nav>
    <main class="layout">
      <aside class="panel sidebar">
        <h2>Sentence List</h2>
        <div class="lesson-list" id="lessonList"></div>
      </aside>
      <section class="panel detail" id="detail" aria-live="polite"></section>
    </main>
  </div>
  <script src="scripts/data.js"></script>
  <script src="scripts/app.js"></script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html_doc, encoding="utf-8")


def main():
    ensure_dirs()
    write_chunk_md()
    write_examples_md()
    build_audio()
    write_data_js()
    write_styles_css()
    write_app_js()
    write_index_html()
    print(f"Generated {len(LESSONS)} lessons in {ROOT}")


if __name__ == "__main__":
    main()
