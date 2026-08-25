# 测验定义与评测规格（Assessment Quizzes v1）

> 版本：v1
> 日期：2026-08-24
> 依据：`docs/development/plans/active/2026-08-learning-first-repositioning-plan.md` 阶段 3、`modules/*/assessment/README.md`（评估标准）
> 实现：`engine/optibench/content/quiz.py`、`engine/optibench/api/routers/content.py`、`apps/desktop/src/lab/QuizPanel.tsx`、`apps/desktop/src/components/LearningQuiz.tsx`

## 1. 定位

把四领域工作台章节内的 `LearningQuiz` 复用为通用测验组件，测验题以 YAML 并入 `modules/` 内容体系，成绩按阶段 2 的 `learning_records` 入库。题目内容以各模块 `assessment/README.md` 已写好的评估标准为依据。

设计取舍：

- **独立 quiz loader，不扩展概念索引**。概念索引只收 `learning/*.md`（frontmatter 合同）；测验是 YAML、schema 完全不同，独立 loader（`optibench/content/quiz.py`）比扩展内容合同更简单，二者扫描路径互不干扰。
- **客户端判分**。答案（`correct_index`）随 API 下发，与四领域现有 `LearningQuiz` 行为一致；本地单机学习应用，不做服务端判分（YAGNI）。

## 2. quiz.yaml 文件格式

位置：`modules/<module>/assessment/quiz.yaml`（每模块一个文件，可含多个测验）。顶层为映射，必含 `quizzes` 列表：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 测验 id，全局唯一（跨模块重复报错） |
| `title` | string | 是 | 测验标题 |
| `module` | string | 是 | 必须与所在模块目录名一致 |
| `concepts` | string[] | 否（默认 `[]`） | 联动概念 id 列表；教程视图在对应概念文末挂载本测验 |
| `pass_score` | int | 否（默认 `80`） | 通过线，0-100；对应评估标准的"正确率 ≥ 80%" |
| `questions` | list | 是 | 题目列表，至少 1 题 |

每题：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `question` | string | 是 | 题干 |
| `options` | string[] | 是 | 选项，至少 2 个非空字符串 |
| `correct_index` | int | 是 | 正确选项下标，0 ≤ i < len(options) |
| `explanation` | string | 否（默认 `""`） | 解析；建议联动相关实验 id/名称，方便学习者回沙盘验证 |

校验错误（非法 YAML、缺字段、`correct_index` 越界、`module` 与目录不一致、id 重复等）默认收集进索引 `errors` 并跳过该文件；`strict=True` 时抛 `QuizError`，信息含文件路径与字段位置。

## 3. API

内容 router（`/api/v1/content`）新增：

- `GET /quizzes`：返回 `{items: [...], errors: [...]}`，item 含完整题目（id/title/module/concepts/pass_score/questions）；`?concept=<id>` 按联动概念过滤（教程挂载点用）。
- `GET /quizzes/{quiz_id}`：单个测验；未知 id 返回 404。

## 4. 成绩入库语义

测验提交后前端按阶段 2 的 `PUT /api/v1/learning/progress` 上报：

```json
{ "item_kind": "assessment", "item_id": "<quiz id>", "status": "scored", "score": <0-100> }
```

- `score` 为百分制整数：`round(答对题数 / 总题数 × 100)`。
- `item_kind` 固定为 `assessment`，与 curriculum 节点 kind 对齐；`item_id` 即 quiz id（与 assessment 节点 id 一致），curriculum graph 合并时 `scored` 记为 `completed`。
- 重测会再次上报（upsert 更新分数）；`useReportProgress` 的去重键含分数，分数变化才重新上报。

## 5. 挂载点

| 挂载点 | 触发 | 行为 |
|---|---|---|
| 教程视图（`TutorialView`） | 概念正文加载成功 | 文末"配套测验"区渲染 `concepts` 含该概念的全部测验（`QuizPanel`） |
| 路径视图（`PathView`） | 点击 `kind=assessment` 节点 | 视图内嵌打开 `QuizPanel`（不切换视图），可关闭；受先修锁定约束 |

通用组件：`apps/desktop/src/components/LearningQuiz.tsx` 保持 prop 驱动（`title`/`questions`/`quizId`/`onComplete`），四领域工作台用法零改动；`QuizPanel`（`apps/desktop/src/lab/QuizPanel.tsx`）负责取数、字段映射（`correct_index` → `correctIndex`）与成绩上报。

## 6. curriculum 集成

`kind=assessment` 节点：`ref` 解析到 quiz 索引（`RefResolver.assessments`），先修、锁定、状态合并与其他 kind 一致。落地节点：`geo-optics-imaging-quiz`（20-geometric-optics，先修 `thin-lens`/`depth-of-field`/`chromatic-aberration`）。

## 7. 落地范围

阶段 3 只落地 20-geometric-optics 一个模块验证管道：

- `geo-optics-imaging-quiz`：8 题，覆盖评估标准 2.1（高斯公式/放大率计算）、2.2（像差识别）、2.3（F 数/NA/景深）与照度模型，解析联动 `thin-lens`、`magnification-scale`、`depth-of-field`、`illumination-geometry` 实验。
- `cmos-fundamentals-quiz`：4 题，联动概念 `cmos-fundamentals`（教程挂载点验证），解析联动 `angle-of-view`、`sensor-coverage` 实验。

其余模块的测验编写是内容工作，随教程正文补写逐批落地，不属于本阶段工程范围。

## 8. 验收标准

- quiz loader：真实 modules 扫描无错误；非法题目（缺字段/越界/重复 id/非法 YAML）报错信息含文件与字段（`engine/tests/test_content_quiz.py`）。
- API：列表、concept 过滤、详情、404（同上）。
- curriculum：assessment 节点解析并入图（`engine/tests/test_api_curriculum.py`）。
- 前端：QuizPanel 渲染/提交/成绩上报（`apps/desktop/src/lab/QuizPanel.test.tsx`）；路径视图 assessment 节点打开/关闭面板（`PathView.test.tsx`）；教程文末配套测验（`TutorialView.test.tsx`）。
