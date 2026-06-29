### Phase 0: 外部数据源接入 🆕

> 目的：当数据来自外部医疗信息系统（FHIR/OMOP/EHR/CDISC SDTM）时，先抽取并转换为本地可处理的格式，再进入 Phase 0.5。

**检测规则**：
- 输入为 **FHIR Server URL**（如 `https://hapi.fhir.org/baseR4`）→ 走 FHIRServerClient
- 输入为 **OpenMRS REST URL**（含 `/openmrs/ws/`）→ 走 OpenMRSConnector
- 输入为 **OpenEHR/EHRbase URL**（含 `/rest/openehr/v1`）→ 走 OpenEHRConnector
- 输入为 **SDTM XPT 文件**（`.xpt` 后缀）→ 走 SDTMReader
- 输入为 **本地 CSV/Excel** → 跳过 Phase 0，直接进入 Phase 0.5

**子流程**：

#### 0.1 SDTM XPT 接入（CDISC 数据）

```python
from msra_modules.cdisc import SDTMReader

reader = SDTMReader()
domains = reader.read_xpt("path/to/sas.xpt")  # 返回 {domain_name: DataFrame}
# 后续走 Phase 1，但 CDISC 合规检查自动启用
```

**输出**：`{domain: DataFrame}` 字典，写入临时 CSV 后进入 Phase 0.5

#### 0.2 EHR 连接器接入（OpenMRS / OpenEHR）

```python
from msra_modules.ehr import OpenMRSConnector, OpenEHRConnector

# OpenMRS：优先用 FHIR 模块（/ws/fhir2/R4），降级走原生 REST + 转换
conn = OpenMRSConnector(base_url="http://host/openmrs/ws/rest/v1",
                       username="admin", password="Admin123")
# OpenEHR（EHRbase）：用 reference model + composition
conn = OpenEHRConnector(base_url="http://host/rest/openehr/v1",
                       username="admin", password="Admin123")
conn.connect()
patients = conn.search_patients(PatientQuery(family_name="Wang"))
obs = conn.get_observations(patient_id="p1")
# 所有连接器统一返回 FHIR R4 格式 dict
```

#### 0.3 FHIR Server 接入（HAPI / Microsoft FHIR Server）

```python
from msra_modules.fhir_server import FHIRServerClient

client = FHIRServerClient(base_url="https://hapi.fhir.org/baseR4",
                          bearer_token="optional-token")
if client.ping():
    bundle = client.search_patients(name="Wang", count=100)
    obs_bundle = client.search_observations(patient_id="p1", code="2339-0")
```

#### 0.4 批量 ETL 工作流（推荐：从 EHR 到 OMOP CSV 一站式）

```python
from msra_modules.ehr import OpenMRSConnector
from msra_modules.etl import ETLWorkflow

conn = OpenMRSConnector(base_url="...", username="...", password="...")
conn.connect()
wf = ETLWorkflow(ehr_connector=conn, batch_size=100)
result = wf.run(output_dir="./output_omop")
# 输出 OMOP CDM CSV: person.csv, visit_occurrence.csv,
#                    condition_occurrence.csv, measurement.csv
if result.success:
    print(f"提取 {result.stats.patients_extracted} 病人, "
          f"生成 {result.stats.omop_records_created} 条 OMOP 记录")
```

**输出**：本地 CSV/Parquet 目录 → 进入 Phase 0.5

**Checkpoint**：无（自动转换，不暂停）

**降级策略**：
- 连接器网络不可达 → 提示用户检查 URL/凭证，不重试
- FHIR 模块未启用 → OpenMRS 自动降级到原生 REST + 转换
- `requests` 未安装 → 抛 `EHRConnectionError`，提示 `pip install requests`

**与后续 Phase 的衔接**：
- 输出 CSV 进入 Phase 0.5（多数据集模式检测）
- Phase 1 自动检测来源（CDISC / OMOP）并启用相应合规检查
- Phase 1 ICD-10 编码可调用 `shared/terminology/ICD10Engine` 校验诊断码
- Phase 7 元数据血缘可调用 `shared/metadata_catalog/MetadataRegistry` + `shared/report_assembler/LineageMermaid`
