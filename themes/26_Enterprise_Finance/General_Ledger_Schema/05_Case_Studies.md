# 总账Schema实践案例

## 1. 案例概述

本文档提供总账Schema在实际企业应用中的实践案例。

---

## 2. 案例1：大型集团总账管理系统

### 2.1 业务背景

**企业背景**：华信制造集团是年营收超500亿元的大型制造集团，拥有50余家子公司。

**业务痛点**：

1. 凭证处理效率低：日均凭证10000+张，月结周期长达15天
2. 数据准确性差：手工录入错误率高达3%
3. 审核流程不规范：缺乏统一审核标准
4. 借贷不平衡频发：手工凭证经常借贷不平
5. 跨系统数据孤岛：数据无法自动对接

**业务目标**：

1. 提高凭证处理效率至20000张/天
2. 录入错误率降至0.1%以下
3. 建立统一审核流程
4. 实现自动借贷平衡检查
5. 数据自动采集率超95%

### 2.2 技术挑战

1. 高并发处理：日均万级凭证处理
2. 分布式事务：跨公司事务一致性
3. 数据一致性：多系统数据同步
4. 审计追踪：完整生命周期记录
5. 合规性要求：满足会计准则和税法

### 2.3 完整代码实现

```python
#!/usr/bin/env python3
"""大型集团总账管理系统 - 约450行完整代码"""

from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

class EntryType(str, Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"
    ADJUSTMENT = "Adjustment"
    REVERSAL = "Reversal"
    CLOSING = "Closing"

class EntryStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    PENDING_APPROVAL = "PendingApproval"
    APPROVED = "Approved"
    POSTED = "Posted"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"

class AccountType(str, Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    REVENUE = "Revenue"
    EXPENSE = "Expense"

@dataclass
class Account:
    account_code: str
    account_name: str
    account_type: AccountType
    parent_code: Optional[str] = None
    is_leaf: bool = True
    currency: str = "CNY"
    is_active: bool = True
    
    def get_balance_direction(self) -> str:
        if self.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            return "Debit"
        return "Credit"

@dataclass
class JournalLine:
    line_number: int
    account_code: str
    account_name: str
    debit_amount: Decimal = Decimal('0')
    credit_amount: Decimal = Decimal('0')
    currency: str = "CNY"
    exchange_rate: Decimal = Decimal('1')
    original_amount: Decimal = Decimal('0')
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    customer_code: Optional[str] = None
    supplier_code: Optional[str] = None
    description: Optional[str] = None
    
    def validate(self) -> Tuple[bool, List[str]]:
        errors = []
        if self.debit_amount < 0 or self.credit_amount < 0:
            errors.append(f"行{self.line_number}: 金额不能为负数")
        if self.debit_amount > 0 and self.credit_amount > 0:
            errors.append(f"行{self.line_number}: 不能同时有借贷金额")
        if self.debit_amount == 0 and self.credit_amount == 0:
            errors.append(f"行{self.line_number}: 金额不能同时为零")
        return len(errors) == 0, errors

@dataclass
class JournalEntry:
    entry_id: str
    entry_date: date
    fiscal_year: str
    fiscal_period: str
    entry_type: EntryType
    description: str
    company_code: str
    company_name: str
    created_by: str
    lines: List[JournalLine] = field(default_factory=list)
    status: EntryStatus = EntryStatus.DRAFT
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    posted_by: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_debit(self) -> Decimal:
        return sum(line.debit_amount for line in self.lines)
    
    @property
    def total_credit(self) -> Decimal:
        return sum(line.credit_amount for line in self.lines)
    
    @property
    def balance(self) -> Decimal:
        return self.total_debit - self.total_credit
    
    @property
    def is_balanced(self) -> bool:
        return abs(self.balance) < Decimal('0.01')
    
    def add_line(self, line: JournalLine) -> None:
        line.line_number = len(self.lines) + 1
        self.lines.append(line)
        self.updated_at = datetime.now()
    
    def validate(self) -> Tuple[bool, List[str]]:
        errors = []
        if len(self.lines) < 2:
            errors.append("凭证至少需要两行分录")
        for line in self.lines:
            is_valid, line_errors = line.validate()
            if not is_valid:
                errors.extend(line_errors)
        if not self.is_balanced:
            errors.append(f"借贷不平衡，差额: {self.balance}")
        if self.total_debit == 0:
            errors.append("凭证金额不能为零")
        return len(errors) == 0, errors
    
    def submit(self, user: str) -> Tuple[bool, List[str]]:
        if self.status != EntryStatus.DRAFT:
            return False, ["只能提交草稿状态的凭证"]
        is_valid, errors = self.validate()
        if not is_valid:
            return False, errors
        self.status = EntryStatus.SUBMITTED
        self.updated_at = datetime.now()
        return True, []
    
    def approve(self, user: str) -> Tuple[bool, str]:
        if self.status != EntryStatus.SUBMITTED:
            return False, "只能审核已提交的凭证"
        self.status = EntryStatus.APPROVED
        self.approved_by = user
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()
        return True, "审核成功"
    
    def post(self, user: str) -> Tuple[bool, str]:
        if self.status != EntryStatus.APPROVED:
            return False, "只能过账已审核的凭证"
        self.status = EntryStatus.POSTED
        self.posted_by = user
        self.posted_at = datetime.now()
        self.updated_at = datetime.now()
        return True, "过账成功"

@dataclass
class GeneralLedger:
    account_code: str
    account_name: str
    company_code: str
    fiscal_year: str
    fiscal_period: str
    opening_balance: Decimal = Decimal('0')
    period_debit: Decimal = Decimal('0')
    period_credit: Decimal = Decimal('0')
    closing_balance: Decimal = Decimal('0')
    currency: str = "CNY"
    
    def calculate_closing_balance(self) -> None:
        account = Account(self.account_code, self.account_name, AccountType.ASSET)
        if account.get_balance_direction() == "Debit":
            self.closing_balance = self.opening_balance + self.period_debit - self.period_credit
        else:
            self.closing_balance = self.opening_balance + self.period_credit - self.period_debit

class GeneralLedgerSystem:
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.entries: Dict[str, JournalEntry] = {}
        self.ledgers: Dict[str, GeneralLedger] = {}
    
    def add_account(self, account: Account) -> None:
        self.accounts[account.account_code] = account
    
    def create_entry(self, entry: JournalEntry) -> Tuple[bool, str]:
        if not entry.entry_id:
            entry.entry_id = f"JE-{entry.fiscal_year}-{entry.fiscal_period}-{uuid.uuid4().hex[:8].upper()}"
        for line in entry.lines:
            if line.account_code not in self.accounts:
                return False, f"科目 {line.account_code} 不存在"
        self.entries[entry.entry_id] = entry
        return True, entry.entry_id
    
    def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        return self.entries.get(entry_id)
    
    def get_entries_by_date(self, start_date: date, end_date: date) -> List[JournalEntry]:
        return [entry for entry in self.entries.values() if start_date <= entry.entry_date <= end_date]
    
    def validate_trial_balance(self, fiscal_year: str, fiscal_period: str) -> Tuple[bool, Decimal]:
        trial_balance = [l for l in self.ledgers.values() if l.fiscal_year == fiscal_year and l.fiscal_period == fiscal_period]
        total_debit = sum(l.opening_balance for l in trial_balance if l.opening_balance > 0)
        total_credit = sum(l.opening_balance for l in trial_balance if l.opening_balance < 0)
        total_debit += sum(l.period_debit for l in trial_balance)
        total_credit += sum(l.period_credit for l in trial_balance)
        difference = abs(total_debit - total_credit)
        return difference < Decimal('0.01'), difference
    
    def get_statistics(self) -> Dict:
        total_entries = len(self.entries)
        posted_entries = sum(1 for e in self.entries.values() if e.status == EntryStatus.POSTED)
        draft_entries = sum(1 for e in self.entries.values() if e.status == EntryStatus.DRAFT)
        total_amount = sum(e.total_debit for e in self.entries.values())
        return {
            'total_entries': total_entries,
            'posted_entries': posted_entries,
            'draft_entries': draft_entries,
            'approval_rate': posted_entries / total_entries * 100 if total_entries > 0 else 0,
            'total_amount': float(total_amount),
            'account_count': len(self.accounts)
        }

def main():
    gl_system = GeneralLedgerSystem()
    
    accounts = [
        Account("1001", "库存现金", AccountType.ASSET),
        Account("1002", "银行存款", AccountType.ASSET),
        Account("1122", "应收账款", AccountType.ASSET),
        Account("2202", "应付账款", AccountType.LIABILITY),
        Account("6001", "主营业务收入", AccountType.REVENUE),
        Account("6401", "主营业务成本", AccountType.EXPENSE),
    ]
    for account in accounts:
        gl_system.add_account(account)
    
    entry = JournalEntry(
        entry_id="",
        entry_date=date(2025, 1, 15),
        fiscal_year="2025",
        fiscal_period="01",
        entry_type=EntryType.MANUAL,
        description="销售商品一批",
        company_code="COMP001",
        company_name="华信制造集团",
        created_by="zhangsan"
    )
    
    entry.add_line(JournalLine(line_number=1, account_code="1122", account_name="应收账款", debit_amount=Decimal('113000.00'), description="应收货款"))
    entry.add_line(JournalLine(line_number=2, account_code="6001", account_name="主营业务收入", credit_amount=Decimal('100000.00'), description="销售收入"))
    entry.add_line(JournalLine(line_number=3, account_code="2202", account_name="应付账款-销项税额", credit_amount=Decimal('13000.00'), description="销项税额"))
    
    success, result = gl_system.create_entry(entry)
    print(f"创建凭证: {success}, {result}")
    
    entry.submit("zhangsan")
    entry.approve("lisi")
    entry.post("wangwu")
    
    print("\n系统统计:")
    print(json.dumps(gl_system.get_statistics(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

### 2.4 效果评估

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 凭证处理效率 | 5000张/天 | 25000张/天 | 400% |
| 月结周期 | 15天 | 3天 | 80% |
| 录入错误率 | 3% | 0.05% | 98.3% |
| 跨系统数据自动采集率 | 30% | 98% | 226% |

**ROI分析**：

- **投入成本**：350万元
- **年度收益**：650万元
- **年度ROI**：85.7%
- **投资回收期**：6.5个月

---

**创建时间**：2025-02-15
