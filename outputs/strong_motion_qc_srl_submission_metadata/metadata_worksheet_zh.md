# 投稿元数据中英双语工作表

这个工作表把 SRL 投稿前需要人工确认的信息拆成可填写字段。
它不会替代 `docs/strong_motion_qc_srl_submission_metadata_template.csv`；最终仍应把确认后的值写回该 CSV。

- 字段总数：28
- 投稿前必填但未完成：0
- 可选择或可推迟：0

## 字段清单

| 字段 ID | 中文标签 | 英文标签 | 必填 | 当前状态 | 当前值 | 需要确认/填写 | 建议格式 | 出现位置 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `journal_target` | 目标期刊与文章类型 | Target journal and article type | yes | complete | Seismological Research Letters regular article | 确认本轮投稿目标和文章类型。 | Seismological Research Letters regular article | submission system; cover letter |
| `submission_issue_choice` | 投稿栏目选择 | Submission issue choice | yes | complete | Regular issue | 确认 Editorial Manager 中选择普通栏目还是当前专题栏目。 | Regular issue / Special issue name | submission system |
| `srl_classification_terms` | SRL 分类词 | SRL classification terms | yes | complete | Strong-motion records; ground-motion data processing; engineering seismology; seismic waveform analysis | 选择最多四个投稿系统分类词，帮助编辑分配审稿方向。 | strong-motion records; ground-motion data processing; engineering seismology; seismic waveform analysis | submission system |
| `flinn_engdahl_region` | Flinn-Engdahl 区域 | Flinn-Engdahl region | yes | not_applicable | [blank] | 选择投稿系统要求的区域项；若论文不针对单一地震或区域，按系统可选项填写最合适的通用/不适用选项。 | Global / Not event-specific / system-selected region | submission system |
| `major_earthquake_name` | 主要地震名称 | Major earthquake name | yes | not_applicable | [blank] | 确认论文是否聚焦某个命名地震；当前稿件为方法与数据集评估，通常可填不适用。 | Not applicable / earthquake name | submission system |
| `license_choice` | 出版许可选择 | Publication license choice | yes | complete | Standard publication route | 和所有作者确认采用普通 page-charge/copyright transfer 路线还是开放获取 CC-BY 路线。 | Page Charges / Open Access CC-BY | submission system; publication forms |
| `editor_background_information` | 给编辑的背景说明 | Background information for editor | yes | complete | This manuscript evaluates auditable offline processing-window selection for strong-motion records using InstanceGM and K-NET, with product-retention checks for PGA, energy, peak time, and response spectra. | 填写投稿系统中给编辑、责任编辑和审稿人分配有帮助的简短背景说明。 | One short paragraph emphasizing offline product-window selection, auditability, cross-archive evidence, and scope limits | submission system |
| `potential_referees` | 建议审稿人 | Potential referees | no | deferred | [blank] | 如提供建议审稿人，列出姓名、邮箱、单位和无利益冲突理由。 | Name, email, affiliation, rationale | submission system |
| `opposed_referees` | 回避审稿人 | Opposed referees | no | not_applicable | [blank] | 如存在利益冲突或竞争关系，列出应回避审稿人及理由；没有则注明不适用。 | Not applicable / Name, affiliation, reason | submission system |
| `author_order` | 作者顺序 | Author order | yes | complete | Haoyu Zhou; Qiang Ma | 按最终投稿顺序填写所有作者姓名。 | First Author; Second Author; Third Author | title page; submission system |
| `author_emails` | Author email addresses | Author email addresses | yes | complete | Haoyu Zhou: zhouhaoyiu@gmail.com; Qiang Ma: maqiang@iem.ac.cn | Author email addresses used on the SRL title page. | [blank] | submission metadata |
| `author_orcid` | 作者 ORCID | Author ORCID | no | complete | Haoyu Zhou: https://orcid.org/0009-0003-8817-1209; Qiang Ma: https://orcid.org/0000-0002-9768-5223 | 填写作者 ORCID，用于题名页、投稿系统或作者信息页。 | https://orcid.org/0000-0000-0000-0000 | title page; submission system |
| `author_affiliations` | 作者单位 | Author affiliations | yes | complete | Haoyu Zhou: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China; Qiang Ma: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China | 填写每位作者的机构、城市、国家和邮编；多单位作者请编号对应。 | 1 Department, Institution, City, Country; 2 Department, Institution, City, Country | title page |
| `corresponding_author_name` | 通讯作者姓名 | Corresponding author name | no | complete | Qiang Ma | 核对负责投稿、修回和校样联系的通讯作者姓名。 | Full Name | title page; submission system |
| `corresponding_author_email` | 通讯作者邮箱 | Corresponding author email | no | complete | maqiang@iem.ac.cn | 核对通讯作者可长期接收投稿系统邮件的邮箱。 | name@example.edu | title page; submission system |
| `corresponding_author_mailing_address` | 通讯作者邮寄地址 | Corresponding author mailing address | no | complete | Institute of Engineering Mechanics, China Earthquake Administration, 29 Xuefu Road, Nangang District, Harbin, Heilongjiang, China | 核对通讯作者的完整邮寄地址。 | Department, Institution, Street, City, Postal Code, Country | title page |
| `funding_statement` | 基金声明 | Funding statement | yes | complete | This research received no external funding. | 填写基金来源和项目号；没有外部基金时也要明确说明。 | This work was supported by ... grant ... / This research received no external funding. | Acknowledgments; submission system |
| `data_provider_acknowledgments` | 数据提供方致谢 | Data-provider acknowledgments | yes | complete | The authors thank the data providers of the InstanceGM/INSTANCE data family and the National Research Institute for Earth Science and Disaster Resilience (NIED) K-NET program for making waveform data available. | 按数据使用条款确认 InstanceGM/INSTANCE 和 NIED K-NET 的致谢表述。 | Acknowledge InstanceGM/INSTANCE and NIED K-NET according to their citation and usage terms. | Acknowledgments; Data and Resources |
| `competing_interests` | 利益冲突声明 | Declaration of competing interests | yes | complete | The authors declare no competing interests. | 确认没有利益冲突，或列出需要披露的关系。 | The authors declare no competing interests. | Declaration of Competing Interests |
| `author_approval` | 全体作者同意 | All-author approval | yes | complete | Author approval confirmed before final packaging. | 确认所有作者已审阅并同意最终投稿版本。 | All authors have approved the final submitted version. | cover letter; submission system |
| `code_archive_url` | 代码归档链接 | Public code archive URL | yes | complete | https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0 | 填写公开仓库、版本归档或 DOI 链接。 | https://github.com/... or https://doi.org/... | Data and Resources |
| `data_access_dates` | 数据访问日期 | Data and resource access dates | yes | complete | InstanceGM/INSTANCE accessed 2026-06-16; K-NET/NIED accessed 2026-06-16; PNWAccelerometers accessed 2026-06-18; public code archive accessed 2026-07-10. | 填写 InstanceGM/INSTANCE、K-NET/NIED 和公开仓库的最终访问日期。 | InstanceGM/INSTANCE accessed YYYY-MM-DD; K-NET/NIED accessed YYYY-MM-DD; repository accessed YYYY-MM-DD | Data and Resources |
| `software_release_doi` | 软件 DOI 或推迟决定 | Software DOI or archive decision | no | complete | GitHub release URL: https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0 | 决定是否提供软件归档 DOI；如暂不提供，写明推迟原因。 | Zenodo DOI ... / deferred until acceptance with repository URL provided | Data and Resources; repository release notes |
| `public_release_license` | 公开归档许可 | Public release license | yes | complete | Code and focused tests: MIT License; derived summary tables, figures, manuscript-support metadata, and documentation: CC BY 4.0; raw InstanceGM/INSTANCE, K-NET, and PNWAccelerometers waveforms are excluded and remain subject to provider terms. | 确认代码和派生复现材料采用的公开许可。 | MIT / BSD-3-Clause / CC-BY-4.0 for derived tables, as appropriate | Data and Resources; repository release notes |
| `ai_tool_disclosure` | AI tool disclosure | AI tool disclosure | yes | complete | OpenAI Codex desktop application version 26.707.31428 assisted with code editing, consistency checks, and language editing. Reported values were generated by the archived scripts. The authors inspected the code and compared the manuscript values with the archived outputs, then reviewed the figures, scientific interpretation, and final text. | SSA AI guidelines require the tool name and version plus the authors' validation steps in the manuscript's Data and Resources section. | [blank] | submission metadata |
| `supplemental_material_decision` | 补充材料决定 | Supplemental-material decision | yes | complete | Detailed CSV evidence tables will be repository/archive artifacts; no separate electronic supplement is planned for the initial upload unless the journal requests it. | 决定 QC 审阅包、复现清单和表格作为补充材料还是仓库材料。 | Supplemental material: figures/tables/QC packet; repository: reproducibility manifests | Data and Resources; supplemental upload |
| `qc_review_decision` | 人工 QC 或人工审阅声明决定 | Human QC review claim decision | no | deferred | [blank] | 决定是否加入人工 QC/人工审阅相关声明；如果正文不主张人工耗时减少，应明确推迟该声明。 | complete after review_summary generated / deferred; no measured human-workload claim | Discussion; Data and Resources; submission metadata |
| `knet_scope_decision` | K-NET 范围决定 | K-NET scope decision | yes | complete | K-NET is treated as a second strong-motion archive in the product-window audit; no real-time or regional-generalization claim is made. | 确认 K-NET 在当前稿件中作为第二个强震动档案参与产品窗口审计，不外推为实时或区域泛化结论。 | Use K-NET as a second strong-motion archive in the product-window audit; no real-time or regional-generalization claim. | Results; Discussion |

## 回填规则

- 填完后，把确认值写入 `docs/strong_motion_qc_srl_submission_metadata_template.csv` 的 `value` 列。
- 必填项确认后把 `status` 改为 `complete`。
- 可推迟项如果决定暂不完成，把 `status` 改为 `deferred`，并在 `notes` 写明原因。
- 改完后运行 `conda run -n zhy python scripts/check_submission_metadata.py --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv --outdir outputs/strong_motion_qc_srl_submission_metadata`。
