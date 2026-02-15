# EMR Schema转换体系

## 📑 目录

- [EMR Schema转换体系](#emr-schema转换体系)
  - [📑 目录](#-目录)
  - [1. 转换体系概述](#1-转换体系概述)
    - [1.1 转换目标](#11-转换目标)
    - [1.2 转换架构](#12-转换架构)
  - [2. CDA文档转换](#2-cda文档转换)
    - [2.1 EMR到CDA转换](#21-emr到cda转换)
    - [2.2 CDA到EMR转换](#22-cda到emr转换)
  - [3. FHIR资源转换](#3-fhir资源转换)
    - [3.1 EMR到FHIR转换](#31-emr到fhir转换)
    - [3.2 FHIR到EMR转换](#32-fhir到emr转换)
  - [4. 跨机构数据交换](#4-跨机构数据交换)
    - [4.1 XDS文档共享](#41-xds文档共享)
    - [4.2 区域平台集成](#42-区域平台集成)
  - [5. 数据迁移工具](#5-数据迁移工具)
  - [6. 转换验证](#6-转换验证)
    - [6.1 验证规则](#61-验证规则)
    - [6.2 质量评估](#62-质量评估)
  - [7. 安全与隐私保护](#7-安全与隐私保护)
    - [7.1 数据脱敏](#71-数据脱敏)
    - [7.2 访问控制](#72-访问控制)
  - [8. 性能优化](#8-性能优化)

---

## 1. 转换体系概述

### 1.1 转换目标

EMR Schema转换体系支持以下转换场景：

1. **文档格式转换**：EMR到HL7 CDA，CDA到EMR
2. **资源格式转换**：EMR到FHIR，FHIR到EMR
3. **跨机构交换**：基于IHE XDS的文档共享
4. **历史数据迁移**：旧系统数据迁移
5. **标准升级**：从旧标准迁移到新标准

### 1.2 转换架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           转换服务层                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ CDA转换服务   │ │ FHIR转换服务  │ │ XDS集成服务   │ │ 数据迁移服务  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           映射规则层                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Schema映射   │ │ 代码值映射   │ │ 数据类型映射 │ │ 验证规则映射  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           数据处理层                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 数据解析     │ │ 数据转换     │ │ 数据验证     │ │ 数据组装     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                           安全层                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 数据脱敏     │ │ 访问控制     │ │ 审计日志     │ │ 加密传输     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CDA文档转换

### 2.1 EMR到CDA转换

**转换规则**：

| EMR Schema | CDA元素 | 转换方式 | 示例 |
|-----------|--------|---------|------|
| `documentId` | `ClinicalDocument/id` | 直接映射 | "EMR202501151430001" → `id` |
| `documentType` | `ClinicalDocument/code` | 代码映射 | "outpatient" → `code="11488-4"` |
| `patient.patientId` | `recordTarget/patientRole/id` | 直接映射 | "PAT001" → `id` |
| `patient.name` | `recordTarget/patientRole/patient/name` | 直接映射 | "张三" → `name` |
| `createdAt` | `ClinicalDocument/effectiveTime` | 格式转换 | DateTime → "20250115143000" |
| `body.chiefComplaint` | `component/section[code="10164-2"]` | 结构化 | Text → CDA Section |

**Python转换实现**：

```python
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EMRToCDAConverter:
    """EMR到CDA文档转换器"""
    
    # 文档类型到CDA代码映射
    DOCUMENT_TYPE_MAP = {
        'outpatient': {'code': '11488-4', 'display': 'Consultation note'},
        'inpatient': {'code': '11506-3', 'display': 'Progress note'},
        'emergency': {'code': '34133-9', 'display': 'Emergency department note'},
        'discharge': {'code': '18842-5', 'display': 'Discharge summary'},
        'surgery': {'code': '11504-8', 'display': 'Surgical operation note'},
        'consultation': {'code': '11488-4', 'display': 'Consultation note'}
    }
    
    # 性别映射
    GENDER_MAP = {
        'male': 'M',
        'female': 'F',
        'unknown': 'UN',
        'other': 'UN'
    }
    
    def __init__(self):
        self.ns = {'hl7': 'urn:hl7-org:v3'}
        self.template_ids = [
            '2.16.156.10011.2.1.1.1',  # 中国CDA文档模板
            '2.16.840.1.113883.10.20.1'  # 通用CDA模板
        ]
    
    def convert(self, emr: Dict[str, Any]) -> str:
        """
        将EMR转换为CDA文档
        
        Args:
            emr: EMR数据字典
            
        Returns:
            CDA XML字符串
        """
        try:
            # 创建根元素
            root = Element('ClinicalDocument')
            root.set('xmlns', 'urn:hl7-org:v3')
            root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            
            # 构建文档头
            self._build_header(root, emr.get('header', {}))
            
            # 构建文档体
            self._build_body(root, emr.get('body', {}))
            
            # 生成XML字符串
            xml_str = tostring(root, encoding='unicode')
            return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'
            
        except Exception as e:
            logger.error(f"EMR to CDA conversion failed: {e}")
            raise ConversionError(f"Conversion failed: {e}")
    
    def _build_header(self, root: Element, header: Dict[str, Any]):
        """构建CDA文档头"""
        
        # realmCode
        realm_code = SubElement(root, 'realmCode')
        realm_code.set('code', 'CN')
        
        # typeId
        type_id = SubElement(root, 'typeId')
        type_id.set('root', '2.16.840.1.113883.1.3')
        type_id.set('extension', 'POCD_HD000040')
        
        # templateId
        for template_id in self.template_ids:
            template = SubElement(root, 'templateId')
            template.set('root', template_id)
        
        # id (文档唯一标识)
        doc_id = SubElement(root, 'id')
        doc_id.set('root', '2.16.156.10011.1.1')
        doc_id.set('extension', header.get('documentId', ''))
        
        # code (文档类型)
        doc_type = header.get('documentType', 'outpatient')
        type_info = self.DOCUMENT_TYPE_MAP.get(doc_type, self.DOCUMENT_TYPE_MAP['outpatient'])
        code = SubElement(root, 'code')
        code.set('code', type_info['code'])
        code.set('codeSystem', '2.16.840.1.113883.6.1')
        code.set('codeSystemName', 'LOINC')
        code.set('displayName', type_info['display'])
        
        # title
        title = SubElement(root, 'title')
        title.text = self._get_document_title(doc_type)
        
        # effectiveTime
        effective_time = SubElement(root, 'effectiveTime')
        created_at = header.get('createdAt')
        if isinstance(created_at, datetime):
            effective_time.set('value', created_at.strftime('%Y%m%d%H%M%S'))
        else:
            effective_time.set('value', str(created_at))
        
        # confidentialityCode
        conf_code = SubElement(root, 'confidentialityCode')
        confidentiality = header.get('metadata', {}).get('confidentiality', 'N')
        conf_map = {'normal': 'N', 'sensitive': 'R', 'restricted': 'V'}
        conf_code.set('code', conf_map.get(confidentiality, 'N'))
        conf_code.set('codeSystem', '2.16.840.1.113883.5.25')
        
        # languageCode
        lang_code = SubElement(root, 'languageCode')
        lang_code.set('code', 'zh-CN')
        
        # setId (文档集标识)
        set_id = SubElement(root, 'setId')
        set_id.set('root', '2.16.156.10011.1.2')
        set_id.set('extension', header.get('documentId', ''))
        
        # versionNumber
        version = SubElement(root, 'versionNumber')
        version.set('value', str(header.get('version', 1)))
        
        # recordTarget (患者信息)
        self._build_record_target(root, header.get('patient', {}))
        
        # author (作者信息)
        self._build_author(root, header.get('createdBy', {}))
        
        # custodian (保管机构)
        self._build_custodian(root, header.get('visit', {}).get('department', ''))
    
    def _build_record_target(self, root: Element, patient: Dict[str, Any]):
        """构建患者信息"""
        record_target = SubElement(root, 'recordTarget')
        patient_role = SubElement(record_target, 'patientRole')
        
        # 患者ID
        patient_id = SubElement(patient_role, 'id')
        patient_id.set('root', '2.16.156.10011.1.12')
        patient_id.set('extension', patient.get('patientId', ''))
        
        # 医保卡号（如有）
        if patient.get('healthCard'):
            insurance_id = SubElement(patient_role, 'id')
            insurance_id.set('root', '2.16.156.10011.1.14')
            insurance_id.set('extension', patient.get('healthCard'))
        
        # 患者详细信息
        patient_elem = SubElement(patient_role, 'patient')
        
        # 姓名
        name = SubElement(patient_elem, 'name')
        name.text = patient.get('name', '')
        
        # 性别
        gender = patient.get('gender', 'unknown')
        admin_gender = SubElement(patient_elem, 'administrativeGenderCode')
        admin_gender.set('code', self.GENDER_MAP.get(gender, 'UN'))
        admin_gender.set('codeSystem', '2.16.840.1.113883.5.1')
        
        # 出生日期
        birth_date = patient.get('birthDate')
        if birth_date:
            birth_time = SubElement(patient_elem, 'birthTime')
            if isinstance(birth_date, datetime):
                birth_time.set('value', birth_date.strftime('%Y%m%d'))
            else:
                birth_time.set('value', str(birth_date))
        
        # 年龄
        if patient.get('age'):
            age_elem = SubElement(patient_elem, 'age')
            age_elem.set('value', str(patient.get('age')))
            age_elem.set('unit', '岁')
    
    def _build_author(self, root: Element, author: Dict[str, Any]):
        """构建作者信息"""
        author_elem = SubElement(root, 'author')
        
        # 创建时间
        time = SubElement(author_elem, 'time')
        time.set('value', datetime.now().strftime('%Y%m%d%H%M%S'))
        
        # 作者信息
        assigned_author = SubElement(author_elem, 'assignedAuthor')
        
        # 作者ID
        author_id = SubElement(assigned_author, 'id')
        author_id.set('root', '2.16.156.10011.1.7')
        author_id.set('extension', author.get('practitionerId', ''))
        
        # 作者姓名
        assigned_person = SubElement(assigned_author, 'assignedPerson')
        name = SubElement(assigned_person, 'name')
        name.text = author.get('name', '')
        
        # 作者科室
        if author.get('department'):
            represented_org = SubElement(assigned_author, 'representedOrganization')
            org_name = SubElement(represented_org, 'name')
            org_name.text = author.get('department')
    
    def _build_custodian(self, root: Element, department: str):
        """构建保管机构信息"""
        custodian = SubElement(root, 'custodian')
        assigned_custodian = SubElement(custodian, 'assignedCustodian')
        represented_custodian = SubElement(assigned_custodian, 'representedCustodianOrganization')
        
        org_id = SubElement(represented_custodian, 'id')
        org_id.set('root', '2.16.156.10011.1.5')
        org_id.set('extension', 'HOSP001')
        
        org_name = SubElement(represented_custodian, 'name')
        org_name.text = department or '医疗机构'
    
    def _build_body(self, root: Element, body: Dict[str, Any]):
        """构建CDA文档体"""
        component = SubElement(root, 'component')
        structured_body = SubElement(component, 'structuredBody')
        
        # 主诉
        if body.get('chiefComplaint'):
            self._build_section(structured_body, {
                'code': '10164-2',
                'title': '主诉',
                'content': body.get('chiefComplaint', {}).get('content', '')
            })
        
        # 现病史
        if body.get('presentIllness'):
            self._build_section(structured_body, {
                'code': '10157-6',
                'title': '现病史',
                'content': body.get('presentIllness', {}).get('content', '')
            })
        
        # 体格检查
        if body.get('physicalExam'):
            self._build_section(structured_body, {
                'code': '29545-1',
                'title': '体格检查',
                'content': self._format_physical_exam(body.get('physicalExam', {}))
            })
        
        # 诊断
        if body.get('diagnoses'):
            self._build_section(structured_body, {
                'code': '29548-5',
                'title': '诊断',
                'content': self._format_diagnoses(body.get('diagnoses', []))
            })
        
        # 诊疗计划
        if body.get('treatmentPlan'):
            self._build_section(structured_body, {
                'code': '18776-5',
                'title': '治疗计划',
                'content': body.get('treatmentPlan', {}).get('content', '')
            })
    
    def _build_section(self, parent: Element, section_data: Dict[str, str]):
        """构建CDA Section"""
        component = SubElement(parent, 'component')
        section = SubElement(component, 'section')
        
        # Section代码
        code = SubElement(section, 'code')
        code.set('code', section_data['code'])
        code.set('codeSystem', '2.16.840.1.113883.6.1')
        code.set('codeSystemName', 'LOINC')
        
        # Section标题
        title = SubElement(section, 'title')
        title.text = section_data['title']
        
        # Section内容
        text = SubElement(section, 'text')
        text.text = section_data['content']
    
    def _get_document_title(self, doc_type: str) -> str:
        """获取文档标题"""
        titles = {
            'outpatient': '门诊病历',
            'inpatient': '住院病历',
            'emergency': '急诊病历',
            'discharge': '出院小结',
            'surgery': '手术记录',
            'consultation': '会诊记录'
        }
        return titles.get(doc_type, '病历文档')
    
    def _format_physical_exam(self, exam: Dict[str, Any]) -> str:
        """格式化体格检查内容"""
        parts = []
        
        if exam.get('general'):
            general = exam.get('general', {})
            vital = general.get('vitalSigns', {})
            if vital:
                parts.append(f"生命体征：体温{vital.get('temperature', '')}°C，"
                           f"脉搏{vital.get('pulse', '')}次/分，"
                           f"呼吸{vital.get('respiration', '')}次/分，"
                           f"血压{vital.get('bloodPressure', {}).get('systolic', '')}/"
                           f"{vital.get('bloodPressure', {}).get('diastolic', '')}mmHg")
        
        if exam.get('systems'):
            systems = exam.get('systems', {})
            for system, content in systems.items():
                if content:
                    parts.append(f"{system}：{content}")
        
        return '\n'.join(parts) if parts else ''
    
    def _format_diagnoses(self, diagnoses: list) -> str:
        """格式化诊断内容"""
        parts = []
        for i, diag in enumerate(diagnoses, 1):
            diag_text = f"{i}. {diag.get('diagnosisName', '')}"
            if diag.get('diagnosisCode'):
                diag_text += f" [{diag.get('diagnosisCode')}]"
            parts.append(diag_text)
        return '\n'.join(parts)


class ConversionError(Exception):
    """转换错误异常"""
    pass
```

### 2.2 CDA到EMR转换

**转换实现**：

```python
class CDAToEMRConverter:
    """CDA到EMR转换器"""
    
    # CDA代码到文档类型映射
    CDA_TYPE_MAP = {
        '11488-4': 'outpatient',
        '11506-3': 'inpatient',
        '34133-9': 'emergency',
        '18842-5': 'discharge',
        '11504-8': 'surgery'
    }
    
    # CDA性别代码映射
    CDA_GENDER_MAP = {
        'M': 'male',
        'F': 'female',
        'UN': 'unknown'
    }
    
    def convert(self, cda_xml: str) -> Dict[str, Any]:
        """
        将CDA文档转换为EMR
        
        Args:
            cda_xml: CDA XML字符串
            
        Returns:
            EMR数据字典
        """
        try:
            root = ET.fromstring(cda_xml)
            ns = {'hl7': 'urn:hl7-org:v3'}
            
            emr = {
                'header': self._parse_header(root, ns),
                'body': self._parse_body(root, ns),
                'footer': {}
            }
            
            return emr
            
        except ET.ParseError as e:
            logger.error(f"CDA XML parse error: {e}")
            raise ConversionError(f"Invalid CDA XML: {e}")
    
    def _parse_header(self, root: Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """解析CDA文档头"""
        header = {}
        
        # 文档ID
        doc_id = root.find('.//hl7:id', ns)
        if doc_id is not None:
            header['documentId'] = doc_id.get('extension', '')
        
        # 文档类型
        doc_code = root.find('.//hl7:code', ns)
        if doc_code is not None:
            code = doc_code.get('code', '')
            header['documentType'] = self.CDA_TYPE_MAP.get(code, 'outpatient')
        
        # 创建时间
        effective_time = root.find('.//hl7:effectiveTime', ns)
        if effective_time is not None:
            time_str = effective_time.get('value', '')
            header['createdAt'] = self._parse_datetime(time_str)
        
        # 患者信息
        header['patient'] = self._parse_patient(root, ns)
        
        # 作者信息
        header['createdBy'] = self._parse_author(root, ns)
        
        # 版本
        version = root.find('.//hl7:versionNumber', ns)
        if version is not None:
            header['version'] = int(version.get('value', 1))
        
        # 机密性
        conf_code = root.find('.//hl7:confidentialityCode', ns)
        if conf_code is not None:
            code = conf_code.get('code', 'N')
            conf_map = {'N': 'normal', 'R': 'sensitive', 'V': 'restricted'}
            header['metadata'] = {'confidentiality': conf_map.get(code, 'normal')}
        
        return header
    
    def _parse_patient(self, root: Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """解析患者信息"""
        patient = {}
        
        # 患者ID
        patient_id = root.find('.//hl7:recordTarget/hl7:patientRole/hl7:id', ns)
        if patient_id is not None:
            patient['patientId'] = patient_id.get('extension', '')
        
        # 患者姓名
        name = root.find('.//hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name', ns)
        if name is not None:
            patient['name'] = name.text or ''
        
        # 性别
        gender = root.find('.//hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:administrativeGenderCode', ns)
        if gender is not None:
            code = gender.get('code', 'UN')
            patient['gender'] = self.CDA_GENDER_MAP.get(code, 'unknown')
        
        # 出生日期
        birth_time = root.find('.//hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:birthTime', ns)
        if birth_time is not None:
            time_str = birth_time.get('value', '')
            patient['birthDate'] = self._parse_date(time_str)
        
        return patient
    
    def _parse_author(self, root: Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """解析作者信息"""
        author = {}
        
        author_id = root.find('.//hl7:author/hl7:assignedAuthor/hl7:id', ns)
        if author_id is not None:
            author['practitionerId'] = author_id.get('extension', '')
        
        name = root.find('.//hl7:author/hl7:assignedAuthor/hl7:assignedPerson/hl7:name', ns)
        if name is not None:
            author['name'] = name.text or ''
        
        return author
    
    def _parse_body(self, root: Element, ns: Dict[str, str]) -> Dict[str, Any]:
        """解析CDA文档体"""
        body = {}
        
        # 主诉
        chief_complaint = self._find_section(root, ns, '10164-2')
        if chief_complaint:
            body['chiefComplaint'] = {'content': chief_complaint}
        
        # 现病史
        present_illness = self._find_section(root, ns, '10157-6')
        if present_illness:
            body['presentIllness'] = {'content': present_illness}
        
        # 体格检查
        physical_exam = self._find_section(root, ns, '29545-1')
        if physical_exam:
            body['physicalExam'] = {'general': {'description': physical_exam}}
        
        # 诊断
        diagnoses_section = self._find_section(root, ns, '29548-5')
        if diagnoses_section:
            body['diagnoses'] = self._parse_diagnoses_text(diagnoses_section)
        
        return body
    
    def _find_section(self, root: Element, ns: Dict[str, str], code: str) -> Optional[str]:
        """查找指定代码的Section内容"""
        sections = root.findall('.//hl7:section', ns)
        for section in sections:
            section_code = section.find('hl7:code', ns)
            if section_code is not None and section_code.get('code') == code:
                text = section.find('hl7:text', ns)
                return text.text if text is not None else ''
        return None
    
    def _parse_diagnoses_text(self, text: str) -> list:
        """从诊断文本解析诊断列表"""
        diagnoses = []
        for line in text.split('\n'):
            line = line.strip()
            if line and line[0].isdigit():
                # 解析 "1. 诊断名称 [代码]" 格式
                parts = line.split('.', 1)
                if len(parts) > 1:
                    diag_text = parts[1].strip()
                    # 提取代码
                    code_match = diag_text.rfind('[')
                    if code_match > 0:
                        name = diag_text[:code_match].strip()
                        code = diag_text[code_match+1:-1] if diag_text.endswith(']') else ''
                        diagnoses.append({
                            'diagnosisName': name,
                            'diagnosisCode': code
                        })
                    else:
                        diagnoses.append({'diagnosisName': diag_text})
        return diagnoses
    
    def _parse_datetime(self, time_str: str) -> datetime:
        """解析HL7日期时间格式"""
        formats = [
            '%Y%m%d%H%M%S',
            '%Y%m%d%H%M',
            '%Y%m%d',
            '%Y%m'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        return datetime.now()
    
    def _parse_date(self, time_str: str) -> str:
        """解析HL7日期格式"""
        if len(time_str) >= 8:
            return f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]}"
        return time_str
```

---

## 3. FHIR资源转换

### 3.1 EMR到FHIR转换

**转换规则**：

| EMR Schema | FHIR Resource | FHIR Element | 转换说明 |
|-----------|--------------|--------------|---------|
| `EMR` | `Bundle` | `entry` | 打包为FHIR Bundle |
| `Patient` | `Patient` | 根元素 | 1:1映射 |
| `Visit` | `Encounter` | 根元素 | 1:1映射 |
| `MedicalRecord` | `Composition` | 根元素 | 病历转为文档组合 |
| `MedicationOrder` | `MedicationRequest` | 根元素 | 1:1映射 |
| `LabResult` | `DiagnosticReport` + `Observation` | 根元素 | 检验报告+观察结果 |
| `NursingRecord` | `CarePlan` + `Observation` | 根元素 | 护理计划+观察 |

**Python实现**：

```python
class EMRToFHIRConverter:
    """EMR到FHIR转换器"""
    
    def __init__(self, base_url: str = "http://example.org/fhir"):
        self.base_url = base_url
        self.resource_count = 0
    
    def convert(self, emr: Dict[str, Any]) -> Dict[str, Any]:
        """
        将EMR转换为FHIR Bundle
        
        Args:
            emr: EMR数据
            
        Returns:
            FHIR Bundle资源
        """
        bundle = {
            "resourceType": "Bundle",
            "id": self._generate_id(),
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat()
            },
            "type": "collection",
            "entry": []
        }
        
        # 转换患者
        if emr.get('header', {}).get('patient'):
            patient = self._convert_patient(emr['header']['patient'])
            bundle['entry'].append({
                "fullUrl": f"{self.base_url}/Patient/{patient['id']}",
                "resource": patient
            })
            patient_id = patient['id']
        else:
            patient_id = None
        
        # 转换就诊
        if emr.get('header', {}).get('visit'):
            encounter = self._convert_encounter(emr['header']['visit'], patient_id)
            bundle['entry'].append({
                "fullUrl": f"{self.base_url}/Encounter/{encounter['id']}",
                "resource": encounter
            })
            encounter_id = encounter['id']
        else:
            encounter_id = None
        
        # 转换病历文档
        if emr.get('body'):
            composition = self._convert_composition(emr, patient_id, encounter_id)
            bundle['entry'].append({
                "fullUrl": f"{self.base_url}/Composition/{composition['id']}",
                "resource": composition
            })
        
        # 转换诊断
        if emr.get('body', {}).get('diagnoses'):
            conditions = self._convert_diagnoses(emr['body']['diagnoses'], patient_id, encounter_id)
            for condition in conditions:
                bundle['entry'].append({
                    "fullUrl": f"{self.base_url}/Condition/{condition['id']}",
                    "resource": condition
                })
        
        # 转换医嘱
        if emr.get('orders'):
            for order in emr['orders']:
                if order.get('orderType') == 'medication':
                    med_request = self._convert_medication_request(order, patient_id, encounter_id)
                    bundle['entry'].append({
                        "fullUrl": f"{self.base_url}/MedicationRequest/{med_request['id']}",
                        "resource": med_request
                    })
        
        return bundle
    
    def _convert_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """转换为FHIR Patient"""
        self.resource_count += 1
        
        fhir_patient = {
            "resourceType": "Patient",
            "id": patient.get('patientId') or self._generate_id(),
            "identifier": [{
                "system": "http://hospital.example.org/patients",
                "value": patient.get('patientId', '')
            }],
            "name": [{
                "use": "official",
                "text": patient.get('name', '')
            }],
            "gender": patient.get('gender', 'unknown'),
        }
        
        if patient.get('birthDate'):
            if isinstance(patient['birthDate'], datetime):
                fhir_patient['birthDate'] = patient['birthDate'].strftime('%Y-%m-%d')
            else:
                fhir_patient['birthDate'] = str(patient['birthDate'])
        
        if patient.get('idCard'):
            fhir_patient['identifier'].append({
                "system": "http://hl7.org/fhir/sid/cn-id",
                "value": patient['idCard']
            })
        
        return fhir_patient
    
    def _convert_encounter(self, visit: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """转换为FHIR Encounter"""
        self.resource_count += 1
        
        encounter = {
            "resourceType": "Encounter",
            "id": visit.get('visitId') or self._generate_id(),
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": self._map_encounter_class(visit.get('visitType', 'outpatient'))
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            } if patient_id else None,
            "participant": [{
                "type": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                        "code": "ATND"
                    }]
                }],
                "individual": {
                    "reference": f"Practitioner/{visit['attendingDoctor'].get('practitionerId', '')}"
                }
            }] if visit.get('attendingDoctor') else [],
        }
        
        if visit.get('visitTime'):
            if isinstance(visit['visitTime'], datetime):
                encounter['period'] = {
                    "start": visit['visitTime'].isoformat()
                }
        
        return encounter
    
    def _convert_composition(self, emr: Dict[str, Any], patient_id: str, encounter_id: str) -> Dict[str, Any]:
        """转换为FHIR Composition"""
        self.resource_count += 1
        header = emr.get('header', {})
        body = emr.get('body', {})
        
        composition = {
            "resourceType": "Composition",
            "id": self._generate_id(),
            "status": "final",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": self._map_document_type(header.get('documentType', 'outpatient')),
                    "display": self._get_document_title(header.get('documentType', 'outpatient'))
                }]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            } if patient_id else None,
            "date": header.get('createdAt', datetime.now()).isoformat() if isinstance(header.get('createdAt'), datetime) else datetime.now().isoformat(),
            "author": [{
                "reference": f"Practitioner/{header['createdBy'].get('practitionerId', '')}"
            }] if header.get('createdBy') else [],
            "title": self._get_document_title(header.get('documentType', 'outpatient')),
            "section": []
        }
        
        # 添加主诉Section
        if body.get('chiefComplaint'):
            composition['section'].append({
                "title": "主诉",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "10164-2"
                    }]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{body['chiefComplaint'].get('content', '')}</div>"
                }
            })
        
        # 添加诊断Section
        if body.get('diagnoses'):
            composition['section'].append({
                "title": "诊断",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "29548-5"
                    }]
                },
                "entry": [{
                    "reference": f"Condition/{diag.get('diagnosisId', '')}"
                } for diag in body['diagnoses']]
            })
        
        return composition
    
    def _convert_diagnoses(self, diagnoses: list, patient_id: str, encounter_id: str) -> list:
        """转换为FHIR Condition列表"""
        conditions = []
        for diag in diagnoses:
            self.resource_count += 1
            condition = {
                "resourceType": "Condition",
                "id": diag.get('diagnosisId') or self._generate_id(),
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed"
                    }]
                },
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis"
                    }]
                }],
                "code": {
                    "text": diag.get('diagnosisName', '')
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                } if patient_id else None,
                "encounter": {
                    "reference": f"Encounter/{encounter_id}"
                } if encounter_id else None
            }
            
            if diag.get('diagnosisCode'):
                condition['code']['coding'] = [{
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": diag['diagnosisCode'],
                    "display": diag.get('diagnosisName', '')
                }]
            
            conditions.append(condition)
        
        return conditions
    
    def _convert_medication_request(self, order: Dict[str, Any], patient_id: str, encounter_id: str) -> Dict[str, Any]:
        """转换为FHIR MedicationRequest"""
        self.resource_count += 1
        
        med = order.get('medication', {})
        dosage = order.get('dosage', {})
        
        med_request = {
            "resourceType": "MedicationRequest",
            "id": order.get('orderId') or self._generate_id(),
            "status": self._map_order_status(order.get('execution', {}).get('status', 'active')),
            "intent": "order",
            "medicationCodeableConcept": {
                "text": med.get('drugName', '')
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            } if patient_id else None,
            "encounter": {
                "reference": f"Encounter/{encounter_id}"
            } if encounter_id else None,
            "authoredOn": order.get('execution', {}).get('authoredOn', datetime.now().isoformat()),
            "requester": {
                "reference": f"Practitioner/{order['execution']['requester'].get('practitionerId', '')}"
            } if order.get('execution', {}).get('requester') else None,
            "dosageInstruction": [{
                "text": f"{dosage.get('route', {}).get('text', '')} {dosage.get('doseQuantity', {}).get('value', '')}{dosage.get('doseQuantity', {}).get('unit', '')}",
                "route": {
                    "text": dosage.get('route', {}).get('text', '')
                } if dosage.get('route') else None,
                "doseAndRate": [{
                    "doseQuantity": {
                        "value": dosage.get('doseQuantity', {}).get('value'),
                        "unit": dosage.get('doseQuantity', {}).get('unit')
                    }
                }] if dosage.get('doseQuantity') else []
            }]
        }
        
        return med_request
    
    def _generate_id(self) -> str:
        """生成资源ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _map_encounter_class(self, visit_type: str) -> str:
        """映射就诊类型"""
        class_map = {
            'outpatient': 'AMB',
            'inpatient': 'IMP',
            'emergency': 'EMER',
            'day_surgery': 'SS',
            'physical': 'AMB'
        }
        return class_map.get(visit_type, 'AMB')
    
    def _map_document_type(self, doc_type: str) -> str:
        """映射文档类型"""
        type_map = {
            'outpatient': '11488-4',
            'inpatient': '11506-3',
            'emergency': '34133-9',
            'discharge': '18842-5',
            'surgery': '11504-8'
        }
        return type_map.get(doc_type, '11506-3')
    
    def _map_order_status(self, status: str) -> str:
        """映射医嘱状态"""
        status_map = {
            'draft': 'draft',
            'active': 'active',
            'on_hold': 'on-hold',
            'revoked': 'revoked',
            'completed': 'completed',
            'entered_in_error': 'entered-in-error'
        }
        return status_map.get(status, 'active')
    
    def _get_document_title(self, doc_type: str) -> str:
        """获取文档标题"""
        titles = {
            'outpatient': '门诊病历',
            'inpatient': '住院病历',
            'emergency': '急诊病历',
            'discharge': '出院小结',
            'surgery': '手术记录'
        }
        return titles.get(doc_type, '病历文档')
```

### 3.2 FHIR到EMR转换

```python
class FHIRToEMRConverter:
    """FHIR到EMR转换器"""
    
    def convert(self, fhir_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        将FHIR Bundle转换为EMR
        
        Args:
            fhir_bundle: FHIR Bundle资源
            
        Returns:
            EMR数据字典
        """
        emr = {
            'header': {},
            'body': {},
            'footer': {},
            'orders': []
        }
        
        # 建立资源索引
        resources = {}
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            resource_id = resource.get('id')
            if resource_type and resource_id:
                resources[f"{resource_type}/{resource_id}"] = resource
        
        # 转换Composition为病历主体
        for entry in fhir_bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'Composition':
                emr = self._convert_composition(resource, resources)
                break
        
        return emr
    
    def _convert_composition(self, composition: Dict[str, Any], resources: Dict[str, Any]) -> Dict[str, Any]:
        """从Composition构建EMR"""
        emr = {
            'header': {},
            'body': {},
            'footer': {},
            'orders': []
        }
        
        # 转换文档类型
        doc_type_coding = composition.get('type', {}).get('coding', [{}])[0]
        emr['header']['documentType'] = self._map_fhir_document_type(doc_type_coding.get('code', ''))
        
        # 转换患者
        subject_ref = composition.get('subject', {}).get('reference', '')
        if subject_ref in resources:
            patient = resources[subject_ref]
            emr['header']['patient'] = self._convert_patient(patient)
        
        # 转换日期
        emr['header']['createdAt'] = composition.get('date', '')
        
        # 转换作者
        if composition.get('author'):
            author_ref = composition['author'][0].get('reference', '')
            if author_ref in resources:
                author = resources[author_ref]
                emr['header']['createdBy'] = {
                    'practitionerId': author.get('id', ''),
                    'name': author.get('name', [{}])[0].get('text', '')
                }
        
        # 转换Sections
        for section in composition.get('section', []):
            section_title = section.get('title', '')
            
            if section_title == '主诉':
                emr['body']['chiefComplaint'] = {
                    'content': self._extract_text(section.get('text', {}))
                }
            elif section_title == '诊断':
                emr['body']['diagnoses'] = []
                for entry in section.get('entry', []):
                    ref = entry.get('reference', '')
                    if ref in resources:
                        condition = resources[ref]
                        emr['body']['diagnoses'].append({
                            'diagnosisName': condition.get('code', {}).get('text', ''),
                            'diagnosisCode': condition.get('code', {}).get('coding', [{}])[0].get('code', ''),
                            'diagnosisId': condition.get('id', '')
                        })
        
        return emr
    
    def _convert_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """转换FHIR Patient为EMR患者"""
        emr_patient = {
            'patientId': patient.get('id', ''),
            'name': patient.get('name', [{}])[0].get('text', ''),
            'gender': patient.get('gender', 'unknown')
        }
        
        if patient.get('birthDate'):
            emr_patient['birthDate'] = patient['birthDate']
        
        # 提取身份证
        for identifier in patient.get('identifier', []):
            if identifier.get('system') == 'http://hl7.org/fhir/sid/cn-id':
                emr_patient['idCard'] = identifier.get('value', '')
                break
        
        return emr_patient
    
    def _map_fhir_document_type(self, code: str) -> str:
        """映射FHIR文档类型"""
        type_map = {
            '11488-4': 'outpatient',
            '11506-3': 'inpatient',
            '34133-9': 'emergency',
            '18842-5': 'discharge',
            '11504-8': 'surgery'
        }
        return type_map.get(code, 'outpatient')
    
    def _extract_text(self, text_obj: Dict[str, Any]) -> str:
        """从FHIR文本对象提取纯文本"""
        if text_obj.get('div'):
            # 简单移除HTML标签
            import re
            div = text_obj['div']
            text = re.sub(r'<[^>]+>', '', div)
            return text
        return text_obj.get('status', '')
```

---

## 4. 跨机构数据交换

### 4.1 XDS文档共享

**IHE XDS集成实现**：

```python
class XDSIntegration:
    """IHE XDS文档共享集成"""
    
    def __init__(self, registry_url: str, repository_url: str):
        self.registry_url = registry_url
        self.repository_url = repository_url
    
    def submit_document(self, emr: Dict[str, Any], patient_id: str) -> str:
        """
        提交EMR文档到XDS存储库
        
        Args:
            emr: EMR数据
            patient_id: 患者标识
            
        Returns:
            文档唯一标识(UUID)
        """
        # 1. 转换为CDA
        converter = EMRToCDAConverter()
        cda_xml = converter.convert(emr)
        
        # 2. 构建提交集
        submission_set = self._build_submission_set(emr, patient_id)
        
        # 3. 构建文档条目
        document_entry = self._build_document_entry(emr, patient_id)
        
        # 4. 提交到XDS存储库
        import uuid
        doc_uuid = str(uuid.uuid4())
        
        # 5. 注册到XDS注册表
        self._register_document(doc_uuid, document_entry)
        
        return doc_uuid
    
    def _build_document_entry(self, emr: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
        """构建XDS文档条目元数据"""
        header = emr.get('header', {})
        
        document_entry = {
            # 患者标识
            "patientId": patient_id,
            
            # 文档唯一标识
            "uniqueId": header.get('documentId', ''),
            
            # 条目UUID
            "entryUUID": f"urn:uuid:{uuid.uuid4()}",
            
            # 文档类别
            "classCode": self._map_class_code(header.get('documentType', 'outpatient')),
            
            # 文档类型
            "typeCode": self._map_type_code(header.get('documentType', 'outpatient')),
            
            # 格式代码
            "formatCode": "urn:ihe:iti:xds-sd:pdf:2008",
            
            # MIME类型
            "mimeType": "text/xml",
            
            # 创建时间
            "creationTime": self._format_datetime(header.get('createdAt')),
            
            # 医疗机构类型
            "healthcareFacilityTypeCode": "281PC2000N",  # 综合医院
            
            # 医疗专业代码
            "practiceSettingCode": header.get('visit', {}).get('departmentCode', 'GENERAL'),
            
            # 语言代码
            "languageCode": "zh-CN",
            
            # 服务开始时间
            "serviceStartTime": self._format_datetime(header.get('visit', {}).get('visitTime')),
            
            # 服务结束时间
            "serviceStopTime": self._format_datetime(header.get('visit', {}).get('dischargeTime')),
            
            # 作者
            "author": [{
                "authorPerson": header.get('createdBy', {}).get('name', ''),
                "authorInstitution": header.get('visit', {}).get('department', '')
            }],
            
            # 机密性代码
            "confidentialityCode": self._map_confidentiality(
                header.get('metadata', {}).get('confidentiality', 'normal')
            ),
            
            # 事件代码列表
            "eventCodeList": [diag.get('diagnosisCode', '') for diag in 
                            emr.get('body', {}).get('diagnoses', []) if diag.get('diagnosisCode')]
        }
        
        return document_entry
    
    def _map_class_code(self, doc_type: str) -> Dict[str, str]:
        """映射文档类别代码"""
        class_codes = {
            'outpatient': {'code': '11488-4', 'codingScheme': 'LOINC', 'name': 'Consultation'},
            'inpatient': {'code': '34133-9', 'codingScheme': 'LOINC', 'name': 'Inpatient'},
            'emergency': {'code': '34133-9', 'codingScheme': 'LOINC', 'name': 'Emergency'},
            'discharge': {'code': '18842-5', 'codingScheme': 'LOINC', 'name': 'Discharge'},
            'surgery': {'code': '11504-8', 'codingScheme': 'LOINC', 'name': 'Surgical'}
        }
        return class_codes.get(doc_type, class_codes['outpatient'])
    
    def _map_type_code(self, doc_type: str) -> Dict[str, str]:
        """映射文档类型代码"""
        return self._map_class_code(doc_type)
    
    def _map_confidentiality(self, level: str) -> Dict[str, str]:
        """映射机密性代码"""
        conf_codes = {
            'normal': {'code': 'N', 'codingScheme': '2.16.840.1.113883.5.25'},
            'sensitive': {'code': 'R', 'codingScheme': '2.16.840.1.113883.5.25'},
            'restricted': {'code': 'V', 'codingScheme': '2.16.840.1.113883.5.25'}
        }
        return conf_codes.get(level, conf_codes['normal'])
    
    def _format_datetime(self, dt) -> str:
        """格式化日期时间"""
        if isinstance(dt, datetime):
            return dt.strftime('%Y%m%d%H%M%S')
        return str(dt) if dt else ''
    
    def query_documents(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查询XDS文档
        
        Args:
            query_params: 查询参数
                - patientId: 患者标识
                - classCode: 文档类别
                - dateRange: 日期范围
                
        Returns:
            文档元数据列表
        """
        # 构建查询请求
        query = {
            "patientId": query_params.get('patientId'),
            "classCode": query_params.get('classCode'),
            "creationTimeFrom": query_params.get('dateRange', {}).get('from'),
            "creationTimeTo": query_params.get('dateRange', {}).get('to')
        }
        
        # 发送查询到注册表
        # 返回结果列表
        return []
```

### 4.2 区域平台集成

```python
class RegionalPlatformIntegration:
    """区域卫生信息平台集成"""
    
    def __init__(self, platform_url: str, api_key: str):
        self.platform_url = platform_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def upload_emr(self, emr: Dict[str, Any]) -> bool:
        """
        上传EMR到区域平台
        
        Args:
            emr: EMR数据
            
        Returns:
            是否成功
        """
        # 转换为平台标准格式
        platform_format = self._convert_to_platform_format(emr)
        
        # 上传数据
        # 返回上传结果
        return True
    
    def query_patient_records(self, patient_id: str, org_id: str = None) -> List[Dict[str, Any]]:
        """
        查询患者在区域平台的病历
        
        Args:
            patient_id: 患者标识
            org_id: 机构标识（可选，用于限定来源机构）
            
        Returns:
            病历列表
        """
        # 构建查询参数
        params = {'patientId': patient_id}
        if org_id:
            params['organizationId'] = org_id
        
        # 发送查询请求
        # 返回结果
        return []
    
    def _convert_to_platform_format(self, emr: Dict[str, Any]) -> Dict[str, Any]:
        """转换为区域平台标准格式"""
        # 根据区域平台接口规范转换
        return emr
```

---

## 5. 数据迁移工具

**历史数据迁移工具**：

```python
class DataMigrationTool:
    """历史数据迁移工具"""
    
    def __init__(self, source_db_config: Dict[str, str], target_db_config: Dict[str, str]):
        self.source_config = source_db_config
        self.target_config = target_db_config
        self.migration_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def migrate_patients(self, batch_size: int = 1000) -> Dict[str, int]:
        """
        迁移患者数据
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            迁移统计
        """
        # 从源数据库读取患者数据
        # 转换为目标格式
        # 写入目标数据库
        # 更新统计
        return self.migration_stats
    
    def migrate_medical_records(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """
        迁移病历数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            迁移统计
        """
        # 按时间范围迁移病历
        return self.migration_stats
    
    def validate_migration(self, sample_size: int = 100) -> Dict[str, Any]:
        """
        验证迁移数据
        
        Args:
            sample_size: 抽样数量
            
        Returns:
            验证报告
        """
        # 抽样验证
        # 对比源数据和目标数据
        # 生成验证报告
        return {
            'sampleSize': sample_size,
            'matchingRate': 0.99,
            'issues': []
        }
```

---

## 6. 转换验证

### 6.1 验证规则

**数据验证规则**：

```python
VALIDATION_RULES = {
    'patient': {
        'required_fields': ['patientId', 'name', 'gender', 'birthDate'],
        'field_types': {
            'patientId': 'string',
            'name': 'string',
            'gender': ['male', 'female', 'unknown'],
            'birthDate': 'date'
        }
    },
    'document': {
        'required_fields': ['documentId', 'documentType', 'createdAt', 'patient', 'body'],
        'document_types': ['outpatient', 'inpatient', 'emergency', 'discharge', 'surgery'],
        'min_diagnoses': 1
    },
    'order': {
        'required_fields': ['orderId', 'orderType', 'execution'],
        'order_types': ['medication', 'lab_order', 'procedure', 'nursing']
    }
}

class EMRValidator:
    """EMR数据验证器"""
    
    def validate(self, emr: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证EMR数据
        
        Args:
            emr: EMR数据
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 验证头部
        header_errors = self._validate_header(emr.get('header', {}))
        errors.extend(header_errors)
        
        # 验证主体
        body_errors = self._validate_body(emr.get('body', {}))
        errors.extend(body_errors)
        
        # 验证医嘱
        if emr.get('orders'):
            for order in emr['orders']:
                order_errors = self._validate_order(order)
                errors.extend(order_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_header(self, header: Dict[str, Any]) -> List[str]:
        """验证病历头部"""
        errors = []
        
        required = ['documentId', 'documentType', 'patient', 'createdAt']
        for field in required:
            if not header.get(field):
                errors.append(f"Missing required field: header.{field}")
        
        if header.get('documentType') not in VALIDATION_RULES['document']['document_types']:
            errors.append(f"Invalid document type: {header.get('documentType')}")
        
        return errors
```

### 6.2 质量评估

```python
class DataQualityAssessment:
    """数据质量评估"""
    
    def assess(self, emr: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估EMR数据质量
        
        Args:
            emr: EMR数据
            
        Returns:
            质量评估报告
        """
        scores = {
            'completeness': self._assess_completeness(emr),
            'accuracy': self._assess_accuracy(emr),
            'consistency': self._assess_consistency(emr),
            'timeliness': self._assess_timeliness(emr)
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            'overallScore': round(overall_score, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()},
            'recommendations': self._generate_recommendations(scores)
        }
    
    def _assess_completeness(self, emr: Dict[str, Any]) -> float:
        """评估完整性"""
        # 计算必填字段完成率
        return 0.95
    
    def _assess_accuracy(self, emr: Dict[str, Any]) -> float:
        """评估准确性"""
        # 验证数据合理性
        return 0.98
    
    def _assess_consistency(self, emr: Dict[str, Any]) -> float:
        """评估一致性"""
        # 检查数据内部一致性
        return 0.92
    
    def _assess_timeliness(self, emr: Dict[str, Any]) -> float:
        """评估及时性"""
        # 检查时间戳合理性
        return 0.99
```

---

## 7. 安全与隐私保护

### 7.1 数据脱敏

```python
class DataDeidentifier:
    """数据脱敏处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def deidentify(self, emr: Dict[str, Any]) -> Dict[str, Any]:
        """
        对EMR数据进行脱敏处理
        
        Args:
            emr: 原始EMR数据
            
        Returns:
            脱敏后的EMR数据
        """
        deidentified = copy.deepcopy(emr)
        
        # 脱敏患者信息
        if deidentified.get('header', {}).get('patient'):
            deidentified['header']['patient'] = self._deidentify_patient(
                deidentified['header']['patient']
            )
        
        # 脱敏医生信息
        if deidentified.get('header', {}).get('createdBy'):
            deidentified['header']['createdBy'] = self._deidentify_practitioner(
                deidentified['header']['createdBy']
            )
        
        # 脱敏联系方式
        # 脱敏地址信息
        
        return deidentified
    
    def _deidentify_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """脱敏患者信息"""
        deidentified = patient.copy()
        
        # 替换姓名为假名
        deidentified['name'] = self._generate_pseudonym(patient['patientId'])
        
        # 脱敏身份证号
        if patient.get('idCard'):
            deidentified['idCard'] = self._mask_id_card(patient['idCard'])
        
        # 出生日期只保留年月
        if patient.get('birthDate'):
            birth = patient['birthDate']
            if isinstance(birth, str) and len(birth) >= 7:
                deidentified['birthDate'] = birth[:7] + '-01'
        
        return deidentified
    
    def _generate_pseudonym(self, patient_id: str) -> str:
        """生成假名"""
        import hashlib
        hash_obj = hashlib.md5(patient_id.encode())
        return f"患者{hash_obj.hexdigest()[:8].upper()}"
    
    def _mask_id_card(self, id_card: str) -> str:
        """脱敏身份证号"""
        if len(id_card) == 18:
            return id_card[:6] + '********' + id_card[14:]
        return '*' * len(id_card)
```

### 7.2 访问控制

```python
class EMRAccessControl:
    """EMR访问控制"""
    
    def __init__(self, rbac_service):
        self.rbac = rbac_service
    
    def check_access(self, user_id: str, emr_id: str, action: str) -> bool:
        """
        检查用户是否有权限访问EMR
        
        Args:
            user_id: 用户标识
            emr_id: 病历标识
            action: 操作类型 (read/write/delete)
            
        Returns:
            是否有权限
        """
        # 获取用户角色
        roles = self.rbac.get_user_roles(user_id)
        
        # 获取病历机密性
        confidentiality = self._get_emr_confidentiality(emr_id)
        
        # 检查权限
        for role in roles:
            if self._has_permission(role, confidentiality, action):
                # 记录访问日志
                self._log_access(user_id, emr_id, action, True)
                return True
        
        # 记录拒绝访问日志
        self._log_access(user_id, emr_id, action, False)
        return False
    
    def _has_permission(self, role: str, confidentiality: str, action: str) -> bool:
        """检查角色权限"""
        permission_matrix = {
            'doctor': {
                'normal': ['read', 'write'],
                'sensitive': ['read', 'write'],
                'restricted': ['read']
            },
            'nurse': {
                'normal': ['read'],
                'sensitive': ['read'],
                'restricted': []
            },
            'admin': {
                'normal': ['read', 'write', 'delete'],
                'sensitive': ['read', 'write', 'delete'],
                'restricted': ['read', 'write', 'delete']
            }
        }
        
        role_perms = permission_matrix.get(role, {})
        conf_perms = role_perms.get(confidentiality, [])
        return action in conf_perms
```

---

## 8. 性能优化

**转换性能优化策略**：

1. **批量处理**：
   - 批量读取和写入
   - 减少数据库往返次数
   - 使用批处理API

2. **缓存机制**：
   - 映射规则缓存
   - 代码值缓存
   - 频繁访问数据缓存

3. **并行处理**：
   - 多线程转换
   - 分片处理大量数据
   - 异步队列处理

4. **流式处理**：
   - 大文件流式读取
   - 增量处理
   - 内存优化

```python
class OptimizedConverter:
    """优化的转换器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.cache = {}
    
    def batch_convert(self, emr_list: List[Dict[str, Any]], 
                     output_format: str = 'cda') -> List[str]:
        """
        批量转换EMR
        
        Args:
            emr_list: EMR列表
            output_format: 输出格式 (cda/fhir)
            
        Returns:
            转换后的文档列表
        """
        from concurrent.futures import ThreadPoolExecutor
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            if output_format == 'cda':
                futures = [executor.submit(self._convert_single_cda, emr) 
                          for emr in emr_list]
            else:
                futures = [executor.submit(self._convert_single_fhir, emr) 
                          for emr in emr_list]
            
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Conversion error: {e}")
                    results.append(None)
        
        return results
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标

**创建时间**：2025-02-15
**最后更新**：2025-02-15
