# 重构与上游打包设计

- 日期：2026-07-14
- 分支：重构在新建 branch 上进行（见「实施注意事项」）
- 编码规范：所有 Python 改动遵循 `python-script-conventions` skill

## 背景与目标

本项目（DIT_HAP_streamlit）所需数据全部来自上游 DIT_HAP 各子项目的输出。当前
数据获取靠手工从上游带编号的阶段目录（`13_/14_/16_/17_`）拷贝并重命名到本项目
`data/raw/` 的扁平结构，映射关系散落、不可复现；本项目 `src/` 下 10 个模块平铺、
`data_config.py` 用三个硬编码函数描述数据集，扩展性差。

两个交付物：

1. **上游打包**：在 DIT_HAP 每个子项目下产出一个干净的、可分发的结果文件夹，
   下游整份拷贝即可使用。参考数据（pombase_data）单独版本化打包。
2. **下游重构**：数据层配置驱动化、`src/` 按职责分包、pages 统一调用约定去重、
   资源来源文档化。

## 边界划分（关键决策）

- **项目结果**：每个上游子项目只打包**自己特有**的耗竭分析结果，放进
  `projects/{项目}/release/`（与 `config/` `reports/` `results/` 同级）。
- **参考数据**：`resources/pombase_data/{version}/` 跨所有项目共享、按版本组织，
  **单独打包**，不塞进任何单个项目目录。
- **非流程资源**（kegg / gocam / verification xlsx / Hayles_2013 /
  collected_pombe_gene_features）：**下游自有**，上游不管；本次仅在下游文档化其
  来源与归属，不改动其生成方式。
- **契约**：release 的子路径命名（如 `insertion_level/LFC.tsv`）是上下游之间唯一
  的映射约定——上游 packaging 映射表的 key 即它，下游 `datasets.yaml` 按它拼路径。

## 交付物一：上游打包（DIT_HAP）

### release 目录结构

```
projects/{项目}/
├── config/          （现有）
├── reports/         （现有）
├── results/         （现有；13_/14_/16_/17_ 编号阶段目录 = 中间产物，保留不动）
└── release/  ★新增  （给下游用的干净结果，只放本项目产物）
    ├── insertion_level/
    │   ├── LFC.tsv
    │   ├── fitting_LFCs.tsv
    │   ├── fitting_results.tsv
    │   ├── baseMean.tsv          # 辅助文件，本项目在用
    │   ├── transformed_weights.tsv
    │   ├── annotations.tsv.gz
    │   └── imputation_statistics.tsv  # 有副本的数据集才有
    └── gene_level/
        ├── LFC.tsv
        ├── fitting_LFCs.tsv
        └── fitting_results.tsv
```

### 映射表（packaging.smk 顶部，显式、可复现）

| release 目标 | 上游源 |
|---|---|
| `insertion_level/LFC.tsv` | `14_insertion_level_depletion_analysis/LFC.tsv` |
| `insertion_level/fitting_LFCs.tsv` | `15_insertion_level_curve_fitting/insertions_LFC_fitted_with_r_square_as_weights.tsv` |
| `insertion_level/fitting_results.tsv` | `15_insertion_level_curve_fitting/insertion_level_fitting_statistics.tsv` |
| `gene_level/LFC.tsv` | `16_gene_level_depletion_analysis/LFC.tsv` |
| `gene_level/fitting_results.tsv` | `16_gene_level_depletion_analysis/gene_level_statistics.tsv` |
| `gene_level/fitting_LFCs.tsv` | `17_gene_level_curve_fitting/gene_level_fitting_statistics.tsv` |

**待核实项**（实现时追脚本副产物确定其上游确切产出）：
`baseMean.tsv`、`transformed_weights.tsv`、`imputation_statistics.tsv`、
`annotations.tsv.gz` 在当前上游规则 `output:` 块中未显式声明，需追到具体脚本。

### 打包规则

- `workflow/rules/packaging.smk`，新增：
  - `rule package_release`：以映射表为准，把源文件拷贝重命名到
    `projects/{project}/release/`。用 Snakemake `input`(源)→`output`(release 目标)
    声明，保证增量、可追溯、依赖正确。
  - `rule package_reference`：把 `resources/pombase_data/{version}/` 中下游需要的
    子集按 version 归档（可选打 tar）。
- 汇入 `rule all` 或单独 target：`snakemake package_release` 打包当前 `project`。
- 若打包逻辑需要独立 Python 脚本，该脚本按 `python-script-conventions` 的
  **独立脚本**规范（完整 7 段布局 + `parse_args()` + `sys.exit(main())`）。

### 下游取数

一条简单脚本/文档：`cp -r projects/{项目}/release/*` → 下游 `data/raw/{数据集}/`；
参考数据 `cp -r` → 下游 `data/resource/pombase_data/{version}/`。不引入额外工具依赖。

## 交付物二：下游重构（DIT_HAP_streamlit）

### 2.1 数据层配置驱动化

新增 `config/datasets.yaml` 注册表，取代 `data_config.py` 里三个硬编码函数
（`get_default_config` / `get_long_timecourse_config` / `get_haploid_config`）：

```yaml
datasets:
  HD_DIT_HAP:
    label: "HD DIT-HAP (default)"
    data_dir: data/raw/HD_DIT_HAP
    has_imputation: true
  Long_timecourse:
    label: "Long timecourse"
    data_dir: data/raw/Long_timecourse_data
    has_imputation: false
  Haploid:
    label: "Haploid"
    data_dir: data/raw/haploid_data
    has_imputation: false
reference:
  pombase_version: "2025-10-01"
  pombase_dir: data/resource/pombase_data
resources:
  kegg_pathways: data/resource/kegg_pathways
  gocam_cx2: data/resource/pombe_gocam_cx2
```

改造 `data_config.py`（→ `src/data/config.py`）：

- 保留 dataclass（`InsertionLevelConfig` 等）作为**类型化路径容器**，改为
  `@dataclass(kw_only=True, slots=True, frozen=True)`（skill §2.2），不再硬编码路径。
- 新增 `load_dataset_config(name: str) -> DataConfig`：读 `datasets.yaml`，按
  `data_dir` + 固定子路径规则（与 release 结构一致）拼出所有路径。
- 数据集差异（如 `has_imputation`）用配置字段表达，取代手工 `imputation = None`。
- 新增数据集 = 改 yaml + 拷贝 release 数据，**零代码改动**。

### 2.2 src/ 按职责分包

当前 10 个平铺模块 → 4 个子包（均为**库模块**，按 skill §1.1 省略
LOGGING/CONFIG/MAIN 段，无 `parse_args()`/`main()`/`setup_logger()`）：

```
src/
├── data/                    # 取数与配置
│   ├── config.py            ← data_config.py（改为配置驱动）
│   ├── loader.py            ← data_manager.py
│   ├── gene_query.py        ← get_gene_data.py
│   └── ontology_format.py   ← preparation.py: format_phaf_file/format_mondo_gaf_file/assign_term_name
├── analysis/                # 分析算法
│   ├── enrichment.py        ← enrichment_functions.py
│   ├── go_cam.py            ← go_cam_functions.py
│   ├── kegg.py              ← kegg_pathway_functions.py
│   └── network.py           ← network_functions.py（go_cam/kegg 共用）
├── viz/
│   └── gene_display.py      ← display_gene_data.py
└── ui/                      # Streamlit 交互组件
    └── inputs.py            ← preparation.py: sidebar_gene_input/gene_input_form/validate_gene_ids
```

关键：`preparation.py` 现在混了两种职责（本体格式化 + 侧栏 UI），拆到
`data/ontology_format.py` 与 `ui/inputs.py`。各子包提供 `__init__.py` 暴露公共入口。

### 2.3 pages 统一调用约定 / 去重

- 每个 page 现在手写 `config = get_default_config()` + 一串 `load_*`。抽一个
  `src/data` 的统一入口（如 `get_data(dataset_name, parts=[...])`），按需加载并
  复用 `@st.cache_data`。
- 数据集选择统一成一个侧栏组件（`ui/inputs.py`），读 `datasets.yaml` 列出可选项，
  取代 `depletion_data.py` 里手工 new 三个 config 的写法。
- 保持 `DIT_HAP_app.py` 导航入口不变，仅调整各 page 内部对 src 的 import 路径。

### 2.4 资源来源文档化（不改生成方式）

在 `data/README.md`（或数据清单）明确每类资源来源与归属：

| 资源 | 来源 | 归属 |
|---|---|---|
| `raw/{数据集}/` | 上游 `release/`（package_release 产出） | 上游 |
| `resource/pombase_data/{version}/` | 上游 `package_reference` | 上游 |
| `resource/kegg_pathways`、`pombe_gocam*`、verification xlsx、`Hayles_2013`、`collected_pombe_gene_features` | 下游自有（gocam 转换脚本 `yaml2cx2.sh` 归入 `scripts/`） | 下游 |

## 实施注意事项

1. **分支**：下游重构在新建 branch 上进行（如 `refactor/config-driven-and-repackage`），
   不直接改 `main`。上游打包改动同理在上游仓库新建分支。
2. **编码规范**：所有 Python 改动遵循 `python-script-conventions`——
   - 库模块（src/ 下被 import 的模块）：省略 LOGGING/CONFIG/MAIN 段。
   - 独立脚本（打包/转换脚本）：完整 7 段布局 + `parse_args()` + `sys.exit(main())`。
   - 通用：native `list/dict`、`X | None`、`pathlib.Path`、`loguru`（非 print）、
     frozen dataclass 配置、单行 docstring、公开仓库文档用英文。
3. **验证**：重构后逐 page 启动 Streamlit 冒烟测试；上游打包后校验 release 文件
   与本项目 `data_config` 期望路径一致；追平「待核实」的辅助文件来源。

## 开放/待核实项

- 辅助文件（baseMean / transformed_weights / imputation_statistics / annotations）
  的上游确切产出脚本——实现时追。
- release 是否打 tar 分发，或仅目录拷贝——实现时依使用便利决定。
