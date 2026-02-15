# GS1 Schema 形式语法与语义

## 📑 目录

- [GS1 Schema 形式语法与语义](#gs1-schema-形式语法与语义)
  - [📑 目录](#-目录)
  - [1. 形式语法 (EBNF)](#1-形式语法-ebnf)
    - [1.1 GTIN 语法](#11-gtin-语法)
    - [1.2 SSCC 语法](#12-sscc-语法)
    - [1.3 GLN 语法](#13-gln-语法)
    - [1.4 应用标识符 (AI) 语法](#14-应用标识符-ai-语法)
    - [1.5 EPCIS 事件结构语法](#15-epcis-事件结构语法)
    - [1.6 条码符号语法](#16-条码符号语法)
  - [2. 类型系统](#2-类型系统)
    - [2.1 基本类型](#21-基本类型)
    - [2.2 复合类型](#22-复合类型)
    - [2.3 类型约束](#23-类型约束)
    - [2.4 类型推导规则](#24-类型推导规则)
  - [3. 操作语义](#3-操作语义)
    - [3.1 条码解析语义](#31-条码解析语义)
    - [3.2 RFID 解析语义](#32-rfid-解析语义)
    - [3.3 EPCIS 事件处理语义](#33-epcis-事件处理语义)
    - [3.4 状态转换语义](#34-状态转换语义)
  - [4. 指称语义](#4-指称语义)
    - [4.1 GS1 标识系统的数学模型](#41-gs1-标识系统的数学模型)
    - [4.2 语义函数定义](#42-语义函数定义)
    - [4.3 域方程](#43-域方程)
  - [5. 公理语义](#5-公理语义)
    - [5.1 标识符唯一性公理](#51-标识符唯一性公理)
    - [5.2 校验位正确性公理](#52-校验位正确性公理)
    - [5.3 EPCIS 事件完整性公理](#53-epcis-事件完整性公理)
    - [5.4 复合公理与推理规则](#54-复合公理与推理规则)

---

## 1. 形式语法 (EBNF)

### 1.1 GTIN 语法

**定义 1.1 (GTIN)**：

```ebnf
(* GTIN 顶层定义 *)
GTIN ::= GTIN8 | GTIN12 | GTIN13 | GTIN14 ;

(* GTIN-8: 8位数字，用于小包装 *)
GTIN8 ::= GS1CompanyPrefix ItemReference CheckDigit ;
GS1CompanyPrefix ::= Digit{4,7} ;
ItemReference ::= Digit{1,4} ;

(* GTIN-12: 12位数字，UPC 兼容 *)
GTIN12 ::= GS1CompanyPrefix ItemReference CheckDigit ;
GS1CompanyPrefix ::= Digit{6,10} ;
ItemReference ::= Digit{1,5} ;

(* GTIN-13: 13位数字，EAN-13 兼容 *)
GTIN13 ::= GS1CompanyPrefix ItemReference CheckDigit ;
GS1CompanyPrefix ::= Digit{7,9} ;
ItemReference ::= Digit{1,5} ;

(* GTIN-14: 14位数字，用于包装层级 *)
GTIN14 ::= IndicatorDigit GS1CompanyPrefix ItemReference CheckDigit ;
IndicatorDigit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
GS1CompanyPrefix ::= Digit{7,9} ;
ItemReference ::= Digit{1,5} ;

(* 基础元素 *)
CheckDigit ::= Digit ;
Digit ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
```

**校验位计算规则**：

```ebnf
(* 模 10 校验算法 *)
CheckDigitCalculation ::=
  "SUM" "("
    "FOR" "i" "=" "1" "TO" "n-1"
    "DO" "digit[i]" "*" Weight[i]
  ")" "MOD" "10" "COMPLEMENT" ;

Weight ::= "3" | "1" ;  (* 交替权重 3, 1, 3, 1, ... *)
```

### 1.2 SSCC 语法

**定义 1.2 (SSCC)**：

```ebnf
(* SSCC: 系列货运包装箱代码，18位数字 *)
SSCC ::= ExtensionDigit GS1CompanyPrefix SerialReference CheckDigit ;

ExtensionDigit ::= Digit ;
GS1CompanyPrefix ::= Digit{7,9} ;
SerialReference ::= Digit{1,9} ;
CheckDigit ::= Digit ;

(* SSCC 总长度约束 *)
SSCC_Length ::= 18 ;
```

### 1.3 GLN 语法

**定义 1.3 (GLN)**：

```ebnf
(* GLN: 全球位置编码，13位数字 *)
GLN ::= GS1CompanyPrefix LocationReference CheckDigit ;

GS1CompanyPrefix ::= Digit{7,9} ;
LocationReference ::= Digit{1,5} ;
CheckDigit ::= Digit ;

(* GLN 总长度约束 *)
GLN_Length ::= 13 ;

(* 位置类型扩展 *)
GLN_Type ::= "PhysicalLocation" | "LegalEntity" | "FunctionalLocation" ;
```

### 1.4 应用标识符 (AI) 语法

**定义 1.4 (应用标识符)**：

```ebnf
(* 应用标识符通用结构 *)
AI_Element ::= AI_Code AI_Data ;
AI_Code ::= "(" Digit{2,4} ")" | Digit{2,4} ;

(* 标准应用标识符 *)
ApplicationIdentifier ::=
    AI_GTIN           (* (01) 全球贸易项目代码 *)
  | AI_GTIN_Quantity  (* (02) 包含物流单元的GTIN *)
  | AI_SerialNumber   (* (21) 序列号 *)
  | AI_LotNumber      (* (10) 批号 *)
  | AI_ExpiryDate     (* (17) 失效日期 *)
  | AI_ProductionDate (* (11) 生产日期 *)
  | AI_SSCC           (* (00) 系列货运包装箱代码 *)
  | AI_GLN            (* (414) 全球位置编码 *)
  | AI_GRAI           (* (8003) 全球可回收资产标识符 *)
  | AI_GIAI           (* (8004) 全球个人资产标识符 *)
  | AI_GSRN           (* (8018) 全球服务关系编号 *)
  | AI_GDTI           (* (253) 全球单据类型标识符 *)
  | AI_CPIN           (* (8010) 部件/组件标识号 *)
  | AI_Quantity       (* (37) 物流单元内贸易项目数量 *)
  | AI_NetWeight      (* (310n) 净重 *)
  | AI_Length         (* (311n) 长度 *)
  | AI_Width          (* (312n) 宽度 *)
  | AI_Height         (* (313n) 高度 *)
  | AI_Volume         (* (315n) 体积 *)
  ;

(* 具体 AI 定义 *)
AI_GTIN           ::= "(01)" Digit{14} ;
AI_GTIN_Quantity  ::= "(02)" Digit{14} ;
AI_SerialNumber   ::= "(21)" Alphanumeric{1,20} ;
AI_LotNumber      ::= "(10)" Alphanumeric{1,20} ;
AI_ExpiryDate     ::= "(17)" Year Month Day ;
AI_ProductionDate ::= "(11)" Year Month Day ;
AI_SSCC           ::= "(00)" Digit{18} ;
AI_GLN            ::= "(414)" Digit{13} ;
AI_GRAI           ::= "(8003)" Digit{14} OptionalSerial ;
AI_GIAI           ::= "(8004)" GS1CompanyPrefix Alphanumeric{1,16} ;
AI_GSRN           ::= "(8018)" Digit{18} ;
AI_GDTI           ::= "(253)" Digit{13} OptionalSerial ;
AI_CPIN           ::= "(8010)" Alphanumeric{1,30} ;
AI_Quantity       ::= "(37)" Digit{1,8} ;

(* 日期格式 *)
Year  ::= Digit{2} ;
Month ::= "01" | "02" | "03" | "04" | "05" | "06"
        | "07" | "08" | "09" | "10" | "11" | "12" ;
Day   ::= "01" | "02" | ... | "31" ;  (* 根据月份有效性验证 *)

(* 可变长度元素分隔符 *)
FNC1 ::= "<GS>" ;  (* Group Separator ASCII 29 *)

(* 字符集 *)
Alphanumeric ::= Digit | UpperCase | LowerCase | Special ;
UpperCase    ::= "A" | "B" | ... | "Z" ;
LowerCase    ::= "a" | "b" | ... | "z" ;
Special      ::= "!" | "\"" | "%" | "&" | "'" | "(" | ")" |
                 "*" | "+" | "," | "-" | "." | "/" | ":" |
                 ";" | "<" | "=" | ">" | "?" | "_" | " " ;
```

**GRAI/GIAI/GSRN 详细语法**：

```ebnf
(* GRAI: 全球可回收资产标识符 *)
GRAI ::= AI_Code "8003" AssetTypeOwner SerialNumber ;
AssetTypeOwner ::= Digit{14} ;  (* GS1 Company Prefix + Asset Type *)
OptionalSerial ::= Alphanumeric{1,16} | "" ;

(* GIAI: 全球个人资产标识符 *)
GIAI ::= AI_Code "8004" CompanyPrefix IndividualAssetReference ;
CompanyPrefix ::= Digit{7,9} ;
IndividualAssetReference ::= Alphanumeric{1,16} ;

(* GSRN: 全球服务关系编号 *)
GSRN ::= AI_Code "8018" ServiceRelationIdentifier ;
ServiceRelationIdentifier ::= Digit{18} ;
GSRN_Type ::= "Recipient" | "Provider" ;

(* GDTI: 全球单据类型标识符 *)
GDTI ::= AI_Code "253" DocumentType Serial ;
DocumentType ::= Digit{13} ;
Serial ::= Alphanumeric{1,17} | "" ;
```

### 1.5 EPCIS 事件结构语法

**定义 1.5 (EPCIS 事件)**：

```ebnf
(* EPCIS 文档结构 *)
EPCISDocument ::= EPCISHeader EPCISBody ;

EPCISHeader ::= "<?xml version='1.0' encoding='UTF-8'?>"
                "<epcis:EPCISDocument"
                " xmlns:epcis='urn:epcglobal:epcis:xsd:1'"
                " xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'"
                " creationDate='" DateTime "'"
                " schemaVersion='" Version "'>" ;

EPCISBody ::= "<EPCISBody>" EventList "</EPCISBody>" "</epcis:EPCISDocument>" ;

(* 事件列表 *)
EventList ::= "<EventList>" Event* "</EventList>" ;

(* 事件类型 *)
Event ::= ObjectEvent | AggregationEvent | TransactionEvent | TransformationEvent ;

(* 对象事件 *)
ObjectEvent ::= "<ObjectEvent>"
                  EventTime
                  EventTimeZoneOffset
                  EPCList
                  Action
                  (BizStep)?
                  (Disposition)?
                  (ReadPoint)?
                  (BizLocation)?
                  (BizTransactionList)?
                  (SourceList)?
                  (DestinationList)?
                  (ILMD)?
                  (QuantityList)?
                  (SensorElementList)?
                "</ObjectEvent>" ;

(* 聚合事件 *)
AggregationEvent ::= "<AggregationEvent>"
                       EventTime
                       EventTimeZoneOffset
                       ParentID
                       ChildEPCs
                       Action
                       (BizStep)?
                       (Disposition)?
                       (ReadPoint)?
                       (BizLocation)?
                       (BizTransactionList)?
                       (SourceList)?
                       (DestinationList)?
                       (SensorElementList)?
                     "</AggregationEvent>" ;

(* 交易事件 *)
TransactionEvent ::= "<TransactionEvent>"
                       EventTime
                       EventTimeZoneOffset
                       EPCList
                       Action
                       BizTransactionList
                       (BizStep)?
                       (Disposition)?
                       (ReadPoint)?
                       (BizLocation)?
                       (SourceList)?
                       (DestinationList)?
                       (QuantityList)?
                     "</TransactionEvent>" ;

(* 转换事件 *)
TransformationEvent ::= "<TransformationEvent>"
                          EventTime
                          EventTimeZoneOffset
                          TransformationID
                          (InputEPCList)?
                          (InputQuantityList)?
                          (OutputEPCList)?
                          (OutputQuantityList)?
                          (BizStep)?
                          (Disposition)?
                          (ReadPoint)?
                          (BizLocation)?
                          (BizTransactionList)?
                          (SourceList)?
                          (DestinationList)?
                          (ILMD)?
                        "</TransformationEvent>" ;

(* 事件元素 *)
EventTime ::= "<eventTime>" DateTime "</eventTime>" ;
EventTimeZoneOffset ::= "<eventTimeZoneOffset>" TimeZone "</eventTimeZoneOffset>" ;
EPCList ::= "<epcList>" EPC+ "</epcList>" ;
ParentID ::= "<parentID>" EPC "</parentID>" ;
ChildEPCs ::= "<childEPCs>" EPC* "</childEPCs>" ;
Action ::= "<action>" ("ADD" | "OBSERVE" | "DELETE") "</action>" ;
BizStep ::= "<bizStep>" URI "</bizStep>" ;
Disposition ::= "<disposition>" URI "</disposition>" ;
ReadPoint ::= "<readPoint>" "<id>" EPC_URI "</id>" "</readPoint>" ;
BizLocation ::= "<bizLocation>" "<id>" EPC_URI "</id>" "</bizLocation>" ;
TransformationID ::= "<transformationID>" URI "</transformationID>" ;

(* EPC URI 格式 *)
EPC_URI ::= "urn:epc:id:sgtin:" GS1CompanyPrefix "." ItemReference "." Serial
          | "urn:epc:id:sscc:" GS1CompanyPrefix "." SerialReference
          | "urn:epc:id:sgln:" GS1CompanyPrefix "." LocationReference "." Extension
          | "urn:epc:id:grai:" GS1CompanyPrefix "." AssetType "." Serial
          | "urn:epc:id:giai:" GS1CompanyPrefix "." IndividualAssetReference
          | "urn:epc:id:gsrn:" GS1CompanyPrefix "." ServiceReference
          | "urn:epc:id:sgtin:" GS1CompanyPrefix "." ItemReference ;

(* 时间和版本 *)
DateTime ::= Year4 "-" Month "-" Day "T" Hour ":" Minute ":" Second ("." Millisecond)? (TimeZone)? ;
Year4 ::= Digit{4} ;
Hour ::= Digit{2} ;
Minute ::= Digit{2} ;
Second ::= Digit{2} ;
Millisecond ::= Digit{1,3} ;
TimeZone ::= "Z" | ("+" | "-") Hour ":" Minute ;
Version ::= "1.2" | "2.0" ;

(* 交易列表 *)
BizTransactionList ::= "<bizTransactionList>" BizTransaction+ "</bizTransactionList>" ;
BizTransaction ::= "<bizTransaction type='" URI "'>" URI "</bizTransaction>" ;

(* 源/目的列表 *)
SourceList ::= "<sourceList>" Source+ "</sourceList>" ;
DestinationList ::= "<destinationList>" Destination+ "</destinationList>" ;
Source ::= "<source type='" URI "'>" EPC_URI "</source>" ;
Destination ::= "<destination type='" URI "'>" EPC_URI "</destination>" ;

(* 数量列表 *)
QuantityList ::= "<quantityList>" QuantityElement+ "</quantityList>" ;
InputQuantityList ::= "<inputQuantityList>" QuantityElement+ "</inputQuantityList>" ;
OutputQuantityList ::= "<outputQuantityList>" QuantityElement+ "</outputQuantityList>" ;
QuantityElement ::= "<quantityElement>"
                      "<epcClass>" EPCClass "</epcClass>"
                      "<quantity>" Decimal "</quantity>"
                      ("<uom>" UOM "</uom>")?
                    "</quantityElement>" ;
EPCClass ::= "urn:epc:class:lgtin:" GS1CompanyPrefix "." ItemReference "." Lot ;
UOM ::= "KGM" | "LTR" | "MTR" | "MTQ" | ... ;  (* UN/CEFACT 推荐标准 20 单位 *)

(* 传感器元素 *)
SensorElementList ::= "<sensorElementList>" SensorElement+ "</sensorElementList>" ;
SensorElement ::= "<sensorElement>"
                    (SensorMetadata)?
                    SensorReport+
                  "</sensorElement>" ;
SensorMetadata ::= "<sensorMetadata"
                     (" startTime='" DateTime "'")?
                     (" endTime='" DateTime "'")?
                     (" deviceID='" URI "'")?
                     (" deviceMetadata='" URI "'")?
                     (" rawData='" URI "'")?
                     (" dataProcessingMethod='" URI "'")?
                     (" bizRules='" URI "'")?
                   "/>" ;
SensorReport ::= "<sensorReport"
                   " type='" MeasurementType "'"
                   (" value='" Decimal "'")?
                   (" stringValue='" String "'")?
                   (" booleanValue='" Boolean "'")?
                   (" hexBinaryValue='" HexBinary "'")?
                   (" uriValue='" URI "'")?
                   (" uom='" UOM "'")?
                   (" minValue='" Decimal "'")?
                   (" maxValue='" Decimal "'")?
                   (" sDev='" Decimal "'")?
                   (" chemicalSubstance='" URI "'")?
                   (" microorganism='" URI "'")?
                 "/>" ;
MeasurementType ::= "Temperature" | "Humidity" | "Pressure" | "Speed"
                  | "Illuminance" | "UV" | "Battery" | "Angle"
                  | "Length" | "Mass" | "Force" | "Time" | ... ;
```

### 1.6 条码符号语法

**定义 1.6 (条码符号)**：

```ebnf
(* GS1 条码符号类型 *)
BarcodeSymbology ::=
    GS1_128          (* 应用最广泛的 GS1 条码 *)
  | GS1_DataMatrix   (* 二维矩阵码 *)
  | GS1_QRCode       (* 快速响应码 *)
  | GS1_Databar      (* 缩减空间符号体系 *)
  | EAN_13           (* 欧洲商品编号 *)
  | EAN_8            (* 缩短版 EAN *)
  | UPC_A            (* 通用产品代码 A 版 *)
  | UPC_E            (* 缩短版 UPC *)
  | ITF_14           (* 14 位交错 2 of 5 *)
  ;

(* GS1-128 结构 *)
GS1_128 ::= FNC1 AI_Element (FNC1 AI_Element)* ;

(* GS1 DataMatrix 结构 *)
GS1_DataMatrix ::= FNC1 AI_Element (FNC1 AI_Element)* ;

(* 编码字符集 *)
CodeSetA ::= "ASCII 控制字符 + 大写字母 + 数字" ;
CodeSetB ::= "ASCII 控制字符 + 大小写字母 + 数字 + 特殊字符" ;
CodeSetC ::= "双密度数字 (00-99)" ;

(* 功能字符 *)
FNC1 ::= ASCII_29 ;  (* 分隔不同 AI 的可变长度数据 *)
FNC2 ::= "消息追加" ;
FNC3 ::= "初始化/读者编程" ;
FNC4 ::= "扩展 ASCII 指示" ;

(* 起始字符和模式 *)
StartA ::= "START Code Set A" ;
StartB ::= "START Code Set B" ;
StartC ::= "START Code Set C" ;

(* 校验字符 *)
CheckSymbol ::= "MOD 103 校验" ;
StopSymbol ::= "STOP 字符" ;
```

---

## 2. 类型系统

### 2.1 基本类型

**定义 2.1 (基本类型)**：

```haskell
-- 数字类型
data Numeric = N8 GTIN8      -- 8位GTIN
             | N12 GTIN12    -- 12位GTIN (UPC)
             | N13 GTIN13    -- 13位GTIN (EAN-13)
             | N14 GTIN14    -- 14位GTIN (ITF-14)
             | N18 SSCC      -- 18位SSCC
             | N13' GLN      -- 13位GLN
             | N18' GSRN     -- 18位GSRN
             deriving (Eq, Show)

-- 字符串类型 (受长度约束)
data GS1String = GS1Str { content :: String
                         , minLen  :: Int
                         , maxLen  :: Int
                         } deriving (Eq, Show)

-- 日期类型
data GS1Date = GS1Date { year  :: Int   -- 00-99 或 2000-2099
                        , month :: Int   -- 01-12
                        , day   :: Int   -- 01-31
                        } deriving (Eq, Show)

-- 日期时间类型
data GS1DateTime = GS1DateTime { date     :: GS1Date
                                , time     :: TimeOfDay
                                , timezone :: TimeZone
                                } deriving (Eq, Show)

-- 布尔类型
data GS1Bool = GS1True | GS1False deriving (Eq, Show)

-- 枚举类型
data Action = ADD | OBSERVE | DELETE deriving (Eq, Show)
data EventType = Object | Aggregation | Transaction | Transformation deriving (Eq, Show)
data Disposition = Active | Inactive | Destroyed | Reserved deriving (Eq, Show)
```

### 2.2 复合类型

**定义 2.2 (复合类型)**：

```haskell
-- 产品标识类型
data ProductIdentifier = ProductId {
    gtin        :: GTIN,
    serial      :: Maybe GS1String,      -- AI (21)
    lot         :: Maybe GS1String,      -- AI (10)
    expiryDate  :: Maybe GS1Date,        -- AI (17)
    prodDate    :: Maybe GS1Date,        -- AI (11)
    quantity    :: Maybe Int             -- AI (37)
} deriving (Eq, Show)

-- 位置标识类型
data LocationIdentifier = LocationId {
    gln         :: GLN,
    glnType     :: GLN_Type,
    name        :: GS1String,
    address     :: Address,
    coordinates :: Maybe Coordinates
} deriving (Eq, Show)

data Address = Address {
    street      :: GS1String,
    city        :: GS1String,
    state       :: Maybe GS1String,
    postalCode  :: GS1String,
    country     :: GS1String    -- ISO 3166-1 alpha-2
} deriving (Eq, Show)

data Coordinates = Coordinates {
    latitude    :: Double,      -- -90.0 到 90.0
    longitude   :: Double       -- -180.0 到 180.0
} deriving (Eq, Show)

-- 物流单元类型
data LogisticUnit = LogisticUnit {
    sscc        :: SSCC,
    contents    :: [ProductIdentifier],
    grossWeight :: Maybe Double,
    dimensions  :: Maybe Dimensions
} deriving (Eq, Show)

data Dimensions = Dimensions {
    length      :: Double,
    width       :: Double,
    height      :: Double,
    unit        :: LengthUnit
} deriving (Eq, Show)

data LengthUnit = MM | CM | M | IN | FT deriving (Eq, Show)

-- EPCIS 事件类型
data EPCISEvent = ObjectEvent' ObjectEvent
                | AggregationEvent' AggregationEvent
                | TransactionEvent' TransactionEvent
                | TransformationEvent' TransformationEvent
                deriving (Eq, Show)

data ObjectEvent = ObjectEvt {
    eventTime       :: GS1DateTime,
    eventTimezone   :: TimeZone,
    epcList         :: [EPC_URI],
    action          :: Action,
    bizStep         :: Maybe URI,
    disposition     :: Maybe Disposition,
    readPoint       :: Maybe GLN,
    bizLocation     :: Maybe GLN,
    transactions    :: Maybe [BizTransaction],
    sources         :: Maybe [Source],
    destinations    :: Maybe [Destination],
    quantities      :: Maybe [Quantity]
} deriving (Eq, Show)

data AggregationEvent = AggregationEvt {
    aggEventTime    :: GS1DateTime,
    aggEventTimezone:: TimeZone,
    parentID        :: EPC_URI,
    childEPCs       :: [EPC_URI],
    aggAction       :: Action,
    aggBizStep      :: Maybe URI,
    aggDisposition  :: Maybe Disposition,
    aggReadPoint    :: Maybe GLN,
    aggBizLocation  :: Maybe GLN
} deriving (Eq, Show)

data BizTransaction = BizTrans {
    transType       :: URI,
    transValue      :: URI
} deriving (Eq, Show)

data Quantity = Quantity {
    epcClass        :: EPC_Class,
    qty             :: Double,
    uom             :: Maybe UOM
} deriving (Eq, Show)

data EPC_URI = SGTIN GS1CompanyPrefix ItemReference Serial
             | SSCC' GS1CompanyPrefix SerialReference
             | SGLN GS1CompanyPrefix LocationReference Extension
             | GRAI' GS1CompanyPrefix AssetType Serial
             | GIAI' GS1CompanyPrefix IndividualAssetReference
             | GSRN' GS1CompanyPrefix ServiceReference
             deriving (Eq, Show)
```

### 2.3 类型约束

**定义 2.3 (类型约束)**：

```haskell
-- 类型约束类
class Validatable a where
    validate :: a -> ValidationResult
    isValid  :: a -> Bool

data ValidationResult = Valid | Invalid [ValidationError]
    deriving (Eq, Show)

data ValidationError = LengthError String
                     | PatternError String
                     | CheckDigitError String
                     | RangeError String
                     | FormatError String
                     deriving (Eq, Show)

-- GTIN 约束
instance Validatable GTIN where
    validate gtin =
        let len = length (digits gtin)
            check = checkDigit gtin
            computed = computeCheckDigit (init $ digits gtin)
        in case len of
            8  -> if check == computed then Valid else Invalid [CheckDigitError "GTIN-8"]
            12 -> if check == computed then Valid else Invalid [CheckDigitError "GTIN-12"]
            13 -> if check == computed then Valid else Invalid [CheckDigitError "GTIN-13"]
            14 -> if check == computed then Valid else Invalid [CheckDigitError "GTIN-14"]
            _  -> Invalid [LengthError $ "Invalid GTIN length: " ++ show len]

-- SSCC 约束
instance Validatable SSCC where
    validate sscc =
        let len = length (ssccDigits sscc)
            check = ssccCheckDigit sscc
            computed = computeCheckDigit (init $ ssccDigits sscc)
        in if len /= 18
           then Invalid [LengthError "SSCC must be 18 digits"]
           else if check /= computed
                then Invalid [CheckDigitError "SSCC check digit invalid"]
                else Valid

-- GLN 约束
instance Validatable GLN where
    validate gln =
        let len = length (glnDigits gln)
            check = glnCheckDigit gln
            computed = computeCheckDigit (init $ glnDigits gln)
        in if len /= 13
           then Invalid [LengthError "GLN must be 13 digits"]
           else if check /= computed
                then Invalid [CheckDigitError "GLN check digit invalid"]
                else Valid

-- 日期约束
instance Validatable GS1Date where
    validate (GS1Date y m d) =
        let daysInMonth = [31, if isLeap y then 29 else 28, 31, 30, 31, 30,
                          31, 31, 30, 31, 30, 31]
            isLeap year = year `mod` 4 == 0 && (year `mod` 100 /= 0 || year `mod` 400 == 0)
        in if m < 1 || m > 12
           then Invalid [RangeError "Month must be 1-12"]
           else if d < 1 || d > (daysInMonth !! (m - 1))
                then Invalid [RangeError $ "Day invalid for month " ++ show m]
                else Valid

-- 坐标约束
instance Validatable Coordinates where
    validate (Coordinates lat lon) =
        let errors = catMaybes [
                if lat < -90 || lat > 90 then Just (RangeError "Latitude must be -90 to 90") else Nothing,
                if lon < -180 || lon > 180 then Just (RangeError "Longitude must be -180 to 180") else Nothing
            ]
        in if null errors then Valid else Invalid errors
```

### 2.4 类型推导规则

**定义 2.4 (类型推导)**：

```haskell
-- 类型环境
type TypeEnv = Map String Type

-- 推导规则
class Inferrable a where
    infer :: TypeEnv -> a -> Either TypeError Type
    check :: TypeEnv -> a -> Type -> Either TypeError ()

-- 标识符类型推导
deriveIdentifierType :: String -> Either TypeError Type
deriveIdentifierType s
    | length s == 8  = Right (T_GTIN GTIN8)
    | length s == 12 = Right (T_GTIN GTIN12)
    | length s == 13 && isGIN s = Right (T_GLN)
    | length s == 13 = Right (T_GTIN GTIN13)
    | length s == 14 = Right (T_GTIN GTIN14)
    | length s == 18 = Right (T_SSCC)
    | otherwise = Left (TypeError $ "Cannot infer type for: " ++ s)
  where
    isGIN str = head str `elem` ['0'..'9']  -- 位置码通常以特定前缀开头

-- AI 数据类型推导
deriveAIType :: String -> String -> Either TypeError Type
deriveAIType aiCode aiData = case aiCode of
    "(01)" | length aiData == 14 -> Right (T_GTIN GTIN14)
    "(00)" | length aiData == 18 -> Right (T_SSCC)
    "(414)" | length aiData == 13 -> Right (T_GLN)
    "(21)" -> Right (T_String 1 20)
    "(10)" -> Right (T_String 1 20)
    "(17)" | length aiData == 6 -> Right (T_Date)
    "(11)" | length aiData == 6 -> Right (T_Date)
    "(37)" -> Right (T_Integer 1 8)
    "(310n)" -> Right (T_Decimal)
    "(8003)" -> Right (T_GRAI)
    "(8004)" -> Right (T_GIAI)
    "(8018)" | length aiData == 18 -> Right (T_GSRN)
    "(253)" -> Right (T_GDTI)
    _ -> Left (TypeError $ "Unknown AI code: " ++ aiCode)

-- 事件类型推导
deriveEventType :: EPCISEvent -> Type
deriveEventType (ObjectEvent' _)       = T_Event Object
deriveEventType (AggregationEvent' _) = T_Event Aggregation
deriveEventType (TransactionEvent' _)  = T_Event Transaction
deriveEventType (TransformationEvent' _) = T_Event Transformation

-- 子类型关系
class Subtype a where
    (<:) :: a -> a -> Bool

instance Subtype Type where
    (<:) (T_GTIN GTIN8) (T_GTIN _)     = True  -- GTIN-8 可提升为任意 GTIN
    (<:) (T_GTIN GTIN12) (T_GTIN _)    = True
    (<:) (T_GTIN GTIN13) (T_GTIN _)    = True
    (<:) (T_GTIN GTIN14) (T_GTIN _)    = True
    (<:) (T_String min1 max1) (T_String min2 max2) = min1 >= min2 && max1 <= max2
    (<:) t1 t2 = t1 == t2
```

---

## 3. 操作语义

### 3.1 条码解析语义

**定义 3.1 (条码解析)**：

```haskell
-- 解析状态机
data ScanState = Start
               | ReadingAI AI_Code String
               | ReadingData String
               | Separator
               | End
               deriving (Eq, Show)

-- 条码扫描配置
data ScannerConfig = ScannerConfig {
    symbology       :: BarcodeSymbology,
    supportFNC1     :: Bool,
    codeSets        :: [CodeSet],
    validateCheck   :: Bool
} deriving (Eq, Show)

-- 解析函数语义
scan :: ScannerConfig -> [Char] -> Either ScanError [AI_Element]
scan config input = evalState (parseElements input) Start

-- 状态转换规则
parseElements :: [Char] -> State ScanState (Either ScanError [AI_Element])
parseElements [] = return (Right [])
parseElements (c:cs) = do
    state <- get
    case state of
        Start | c == '\x1d' -> do  -- FNC1
            put Start
            parseElements cs
              | isDigit c -> do
            put (ReadingAI [c] "")
            parseElements cs
        ReadingAI code data_
            | c == '\x1d' -> do  -- FNC1 分隔符
                let aiElement = createAIElement code data_
                put Start
                rest <- parseElements cs
                return $ fmap (aiElement :) rest
            | c == '(' -> do  -- 括号格式 AI
                put (ReadingAI [c] "")
                parseElements cs
            | c == ')' -> do  -- 结束 AI 码，开始数据
                put (ReadingData data_)
                parseElements cs
            | isDigit c && length code < 4 -> do
                put (ReadingAI (code ++ [c]) data_)
                parseElements cs
            | otherwise -> do
                put (ReadingData (data_ ++ [c]))
                parseElements cs
        ReadingData data_
            | c == '\x1d' || isAIEndMarker c -> do
                state' <- get
                let aiElement = createAIElement (getAICode state') data_
                put Start
                rest <- parseElements cs
                return $ fmap (aiElement :) rest
            | otherwise -> do
                put (ReadingData (data_ ++ [c]))
                parseElements cs

-- 语义规则：AI 元素创建
createAIElement :: AI_Code -> AI_Data -> Either ScanError AI_Element
createAIElement code data_ =
    case validateAIData code data_ of
        Valid -> Right $ AI_Element code data_
        Invalid errors -> Left $ ScanError errors

-- 语义规则：数据验证
validateAIData :: AI_Code -> AI_Data -> ValidationResult
validateAIData code data_ = case lookup code aiDefinitions of
    Just def -> validateAgainstDef def data_
    Nothing -> Invalid [FormatError $ "Unknown AI code: " ++ code]

-- 校验位验证语义
validateCheckDigit :: [Int] -> Int -> Bool
validateCheckDigit digits check =
    let weighted = zipWith (*) (reverse digits) (cycle [3, 1])
        sum_ = sum weighted
        computed = (10 - (sum_ `mod` 10)) `mod` 10
    in check == computed

-- 条码解析的大步语义（Big-step）
parseBarcode :: BarcodeSymbology -> [Char] -> Either ParseError BarcodeData
parseBarcode sym chars = case sym of
    GS1_128 ->
        let fnc1Positions = findIndices (== '\x1d') chars
            segments = splitAtPositions fnc1Positions chars
            aiElements = mapM parseSegment segments
        in BarcodeData GS1_128 <$> aiElements
    GS1_DataMatrix -> parseBarcode GS1_128 chars  -- 内部编码相同
    EAN_13 ->
        if length chars == 13
        then Right $ BarcodeData EAN_13 [AI_Element "(01)" (pad14 chars)]
        else Left $ ParseError "EAN-13 must be 13 digits"
    ITF_14 ->
        if length chars == 14
        then Right $ BarcodeData ITF_14 [AI_Element "(01)" chars]
        else Left $ ParseError "ITF-14 must be 14 digits"
```

### 3.2 RFID 解析语义

**定义 3.2 (RFID 解析)**：

```haskell
-- RFID 标签状态
data RFIDState = RFIDState {
    tagMemory       :: TagMemory,
    lockStatus      :: LockStatus,
    killStatus      :: KillStatus,
    accessPassword  :: Maybe Password,
    killPassword    :: Maybe Password
} deriving (Eq, Show)

data TagMemory = TagMemory {
    epcMemory       :: [Word8],     -- EPC 存储体 (Bank 01)
    tidMemory       :: [Word8],     -- TID 存储体 (Bank 10)
    userMemory      :: [Word8],     -- 用户存储体 (Bank 11)
    reservedMemory  :: [Word8]      -- 保留存储体 (Bank 00)
} deriving (Eq, Show)

data LockStatus = Unlocked | Locked | Permalocked deriving (Eq, Show)
data KillStatus = Alive | Killed deriving (Eq, Show)
type Password = [Word8]  -- 32位密码

-- RFID 读取语义
readRFID :: ReaderConfig -> RFIDTag -> IO (Either RFIDError EPCData)
readRFID config tag = do
    -- 选择标签
    selectResult <- selectTag config tag
    case selectResult of
        Left err -> return $ Left err
        Right _  -> do
            -- 读取 EPC 存储体
            epcData <- readBank config 1 0 128  -- 读取 128 位 EPC
            -- 解码 EPC
            return $ decodeEPC epcData

-- EPC 解码语义
decodeEPC :: [Word8] -> Either RFIDError EPCData
decodeEPC bytes = do
    let header = bytes !! 0
    case header of
        0x30 -> decodeSGTIN96 bytes      -- SGTIN-96
        0x31 -> decodeSSCC96 bytes       -- SSCC-96
        0x32 -> decodeSGLN96 bytes       -- SGLN-96
        0x33 -> decodeGRAI96 bytes       -- GRAI-96
        0x34 -> decodeGIAI96 bytes       -- GIAI-96
        0x35 -> decodeGSRN96 bytes       -- GSRN-96
        0x36 -> decodeGDTI96 bytes       -- GDTI-96
        0x38 -> decodeSGTIN198 bytes     -- SGTIN-198
        _    -> Left $ UnknownEPCHeader header

-- SGTIN-96 解码语义
decodeSGTIN96 :: [Word8] -> Either RFIDError EPCData
decodeSGTIN96 bytes =
    let bits = bytesToBits bytes
        -- 解析字段
        header      = take 8 bits
        filter      = take 3 (drop 8 bits)
        partition   = take 3 (drop 11 bits)
        (m, l)      = getPartitionSizes (bitsToInt partition)
        companyPrefix = bitsToBCD (take m (drop 14 bits))
        itemReference = bitsToBCD (take l (drop (14 + m) bits))
        serial      = bitsToHex (drop (14 + m + l) bits)
        -- 构建 GTIN
        indicator   = "0"  -- SGTIN-96 不包含指示符
        checkDigit  = computeCheckDigit (indicator ++ companyPrefix ++ itemReference)
        gtin14      = indicator ++ companyPrefix ++ itemReference ++ [checkDigit]
    in Right $ EPCData {
        epcType     = SGTIN_96,
        pureURI     = "urn:epc:id:sgtin:" ++ companyPrefix ++ "." ++ itemReference ++ "." ++ serial,
        tagURI      = "urn:epc:tag:sgtin-96:" ++ bitsToInt filter ++ "." ++
                      companyPrefix ++ "." ++ itemReference ++ "." ++ serial,
        gtin        = Just gtin14,
        serialNum   = Just serial,
        companyPref = Just companyPrefix
    }

-- 分区表查找
getPartitionSizes :: Int -> (Int, Int)
getPartitionSizes p = case p of
    0 -> (40, 4)    -- 12 位公司前缀, 1 位项目参考
    1 -> (37, 7)    -- 11 位公司前缀, 2 位项目参考
    2 -> (34, 10)   -- 10 位公司前缀, 3 位项目参考
    3 -> (30, 14)   -- 9 位公司前缀, 4 位项目参考
    4 -> (27, 17)   -- 8 位公司前缀, 5 位项目参考
    5 -> (24, 20)   -- 7 位公司前缀, 6 位项目参考
    6 -> (20, 24)   -- 6 位公司前缀, 7 位项目参考
    _ -> error "Invalid partition value"

-- RFID 过滤值语义
data FilterValue = All | PointOfSale | FullCase | Reserved | InnerPack
                 | UnitLoad | UnitInsideTradeItem | Reserved2
                 deriving (Eq, Show, Enum)

filterToBits :: FilterValue -> [Bit]
filterToBits fv = intToBits 3 (fromEnum fv)

-- RFID 写入语义（反向操作）
encodeSGTIN96 :: String -> String -> String -> FilterValue -> Either EncodeError [Word8]
encodeSGTIN96 cp ir serial fv = do
    let header = intToBits 8 0x30
        filter = filterToBits fv
        partition = getPartitionValue cp
        (m, l) = getPartitionSizes (bitsToInt partition)
        companyPrefixBits = bcdToBits m cp
        itemRefBits = bcdToBits l ir
        serialBits = padRight 38 (hexToBits serial)
    return $ bitsToBytes (header ++ filter ++ partition ++ companyPrefixBits ++
                          itemRefBits ++ serialBits)
```

### 3.3 EPCIS 事件处理语义

**定义 3.3 (EPCIS 事件处理)**：

```haskell
-- EPCIS 捕获接口语义
data CaptureInterface = CaptureInterface {
    captureQueue    :: Queue EPCISEvent,
    validator       :: EPCISEvent -> ValidationResult,
    enricher        :: EPCISEvent -> IO EPCISEvent,
    persister       :: EPCISEvent -> IO ()
}

-- 事件捕获语义
captureEvent :: CaptureInterface -> EPCISEvent -> IO (Either CaptureError EventID)
captureEvent iface event = do
    -- 步骤 1: 验证事件
    case validator iface event of
        Invalid errors -> return $ Left $ ValidationFailed errors
        Valid -> do
            -- 步骤 2: 富化事件（添加缺失信息）
            enrichedEvent <- enricher iface event
            -- 步骤 3: 生成事件 ID
            let eventID = generateEventID enrichedEvent
            let eventWithID = enrichedEvent { eventId = Just eventID }
            -- 步骤 4: 持久化事件
            persister iface eventWithID
            return $ Right eventID

-- 事件验证语义
validateEvent :: EPCISEvent -> ValidationResult
validateEvent event = case event of
    ObjectEvent' oe -> validateObjectEvent oe
    AggregationEvent' ae -> validateAggregationEvent ae
    TransactionEvent' te -> validateTransactionEvent te
    TransformationEvent' te -> validateTransformationEvent te

validateObjectEvent :: ObjectEvent -> ValidationResult
validateObjectEvent oe =
    let errors = catMaybes [
            validateRequired (eventTime oe) "eventTime",
            validateRequired (action oe) "action",
            validateNonEmpty (epcList oe) "epcList",
            validateEPCLength (epcList oe),
            validateActionConsistency (action oe) (epcList oe) (quantities oe)
        ]
    in if null errors then Valid else Invalid errors

validateAggregationEvent :: AggregationEvent -> ValidationResult
validateAggregationEvent ae =
    let errors = catMaybes [
            validateRequired (aggEventTime ae) "eventTime",
            validateRequired (aggAction ae) "action",
            validateRequired (parentID ae) "parentID",
            validateActionParentConsistency (aggAction ae) (parentID ae) (childEPCs ae)
        ]
    in if null errors then Valid else Invalid errors

-- 动作语义解释
-- ADD: 将对象添加到指定位置或聚合
-- OBSERVE: 观察到对象在指定位置或状态
-- DELETE: 从指定位置或聚合中移除对象

executeAction :: Action -> EventContext -> IO ActionResult
executeAction ADD ctx = do
    -- 语义: 对象现在存在于指定位置
    updateLocation (epc ctx) (bizLocation ctx)
    when (isAggregation ctx) $
        addToAggregation (parentID ctx) (childEPCs ctx)
    return $ ActionSuccess "Object added"

executeAction OBSERVE ctx = do
    -- 语义: 记录观察快照，不修改状态
    recordObservation (epc ctx) (readPoint ctx) (eventTime ctx)
    return $ ActionSuccess "Object observed"

executeAction DELETE ctx = do
    -- 语义: 对象不再存在于指定位置
    removeFromLocation (epc ctx) (bizLocation ctx)
    when (isAggregation ctx) $
        removeFromAggregation (parentID ctx) (childEPCs ctx)
    return $ ActionSuccess "Object removed"

-- 查询接口语义
data QueryInterface = QueryInterface {
    simpleEventQuery    :: SimpleEventQuery -> IO [EPCISEvent],
    masterDataQuery     :: MasterDataQuery -> IO [MasterData],
    subscriptionManager :: SubscriptionManager
}

-- 简单事件查询语义
evaluateSimpleQuery :: SimpleEventQuery -> [EPCISEvent] -> [EPCISEvent]
evaluateSimpleQuery query events =
    filter (matchesQuery query) events

matchesQuery :: SimpleEventQuery -> EPCISEvent -> Bool
matchesQuery query event =
    maybe True (`matchesEventTime` eventTime event) (eventTimeParam query)
    && maybe True (`matchesEventTypes` event) (eventTypeParam query)
    && maybe True (`matchesEPCs` event) (epcParam query)
    && maybe True (`matchesBizStep` event) (bizStepParam query)
    && maybe True (`matchesDisposition` event) (dispositionParam query)
    && maybe True (`matchesReadPoint` event) (readPointParam query)
    && maybe True (`matchesBizLocation` event) (bizLocationParam query)

-- 事件时序语义
data EventOrdering = EventOrdering {
    partialOrder    :: Set (EventID, EventID),
    causalLinks     :: Set (EventID, EventID),
    temporalOrder   :: Map EventID UTCTime
}

-- 建立偏序关系
computePartialOrder :: [EPCISEvent] -> EventOrdering
computePartialOrder events =
    let -- 基于时间戳的时序
        timeOrder = Map.fromList [(eid e, eventTime e) | e <- events]
        -- 因果关系: 如果事件 e1 读取了 e2 写入的对象
        causal = findCausalLinks events
        -- 偏序: 时间序 + 因果序的传递闭包
        partial = transitiveClosure (timePairs events `Set.union` causal)
    in EventOrdering partial causal timeOrder
  where
    timePairs es = Set.fromList [
        (eid e1, eid e2) | e1 <- es, e2 <- es,
        eventTime e1 < eventTime e2]
```

### 3.4 状态转换语义

**定义 3.4 (状态转换)**：

```haskell
-- 供应链状态
data SupplyChainState = SupplyChainState {
    objectLocations   :: Map EPC_URI Location,
    aggregations      :: Map EPC_URI (Set EPC_URI),
    transactions      :: Map BizTransID (Set EPC_URI),
    dispositions      :: Map EPC_URI Disposition,
    eventHistory      :: [EPCISEvent]
} deriving (Eq, Show)

data Location = UnknownLocation
              | Located GLN
              | InTransit (Maybe GLN) (Maybe GLN)  -- 从 -> 到
              | Destroyed
              deriving (Eq, Show)

-- 状态转换函数
type StateTransition = SupplyChainState -> EPCISEvent -> Either TransitionError SupplyChainState

-- 对象事件转换
objectEventTransition :: StateTransition
objectEventTransition state (ObjectEvent' event) =
    case action event of
        ADD ->
            let newLocs = Map.fromList [(epc, Located loc) | epc <- epcList event]
                loc = fromMaybe (error "ADD requires bizLocation") (bizLocation event)
            in Right $ state {
                objectLocations = objectLocations state `Map.union` newLocs,
                eventHistory = event : eventHistory state
            }
        OBSERVE ->
            let updates = [(epc, Located rp) | epc <- epcList event]
                rp = fromMaybe (error "OBSERVE requires readPoint") (readPoint event)
            in Right $ state {
                objectLocations = foldr (uncurry Map.insert) (objectLocations state) updates,
                eventHistory = event : eventHistory state
            }
        DELETE ->
            let removals = Map.fromList [(epc, UnknownLocation) | epc <- epcList event]
            in Right $ state {
                objectLocations = objectLocations state `Map.union` removals,
                eventHistory = event : eventHistory state
            }

-- 聚合事件转换
aggregationEventTransition :: StateTransition
aggregationEventTransition state (AggregationEvent' event) =
    case aggAction event of
        ADD ->
            let parent = parentID event
                children = Set.fromList (childEPCs event)
                currentChildren = Map.findWithDefault Set.empty parent (aggregations state)
                newChildren = currentChildren `Set.union` children
                -- 更新子对象位置为"在父对象内"
                childLocs = Map.fromList [(child, LocatedParent parent) | child <- childEPCs event]
            in Right $ state {
                aggregations = Map.insert parent newChildren (aggregations state),
                objectLocations = objectLocations state `Map.union` childLocs,
                eventHistory = event : eventHistory state
            }
        OBSERVE ->
            -- 观察不改变聚合关系
            Right $ state { eventHistory = event : eventHistory state }
        DELETE ->
            let parent = parentID event
                children = Set.fromList (childEPCs event)
                currentChildren = Map.findWithDefault Set.empty parent (aggregations state)
                newChildren = currentChildren `Set.difference` children
                -- 子对象位置变为未知
                childLocs = Map.fromList [(child, UnknownLocation) | child <- childEPCs event]
            in Right $ state {
                aggregations = Map.insert parent newChildren (aggregations state),
                objectLocations = objectLocations state `Map.union` childLocs,
                eventHistory = event : eventHistory state
            }

-- 交易事件转换
transactionEventTransition :: StateTransition
transactionEventTransition state (TransactionEvent' event) =
    let trans = fromMaybe (error "TransactionEvent requires transactions") (transactions' event)
        transIDs = map transValue trans
        epcs = epcList' event
        -- 将 EPC 关联到交易
        transUpdates = Map.fromList [(tid, Set.fromList epcs) | tid <- transIDs]
    in case action' event of
        ADD -> Right $ state {
            transactions = Map.unionWith Set.union (transactions state) transUpdates,
            eventHistory = event : eventHistory state
        }
        OBSERVE -> Right $ state { eventHistory = event : eventHistory state }
        DELETE -> Right $ state {
            transactions = foldr Map.delete (transactions state) transIDs,
            eventHistory = event : eventHistory state
        }

-- 状态转换的小步语义 (Small-step)
smallStep :: SupplyChainState -> EPCISEvent -> Either TransitionError SupplyChainState
smallStep state event = case event of
    ObjectEvent' _       -> objectEventTransition state event
    AggregationEvent' _  -> aggregationEventTransition state event
    TransactionEvent' _  -> transactionEventTransition state event
    TransformationEvent' _ -> transformationEventTransition state event

-- 状态转换的大步语义 (Big-step)
bigStep :: SupplyChainState -> [EPCISEvent] -> Either TransitionError SupplyChainState
bigStep state [] = Right state
bigStep state (e:es) = do
    newState <- smallStep state e
    bigStep newState es

-- 转换保持的不变量
data Invariant = LocationConsistent
               | AggregationAcyclic
               | TransactionComplete
               | EventMonotonic
               deriving (Eq, Show)

checkInvariant :: Invariant -> SupplyChainState -> Bool
checkInvariant LocationConsistent state =
    all (\(epc, loc) -> isValidLocation epc loc state) (Map.toList $ objectLocations state)
  where
    isValidLocation epc (LocatedParent parent) state' =
        case Map.lookup parent (aggregations state') of
            Just children -> epc `Set.member` children
            Nothing -> False
    isValidLocation _ _ _ = True

checkInvariant AggregationAcyclic state =
    not $ hasCycle (aggregations state)
  where
    hasCycle graph = any (\node -> dfs Set.empty node graph) (Map.keys graph)
    dfs visited node graph
        | node `Set.member` visited = True
        | otherwise = case Map.lookup node graph of
            Just children -> any (\child -> dfs (Set.insert node visited) child graph) (Set.toList children)
            Nothing -> False
```

---

## 4. 指称语义

### 4.1 GS1 标识系统的数学模型

**定义 4.1 (标识域)**：

```haskell
-- 标识符的数学域
-- D_Identifier = GTIN ⊕ SSCC ⊕ GLN ⊕ GRAI ⊕ GIAI ⊕ GSRN ⊕ GDTI

-- 基本域定义
type Digit = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
type NumericString n = { s ∈ Digit* | |s| = n }

-- GTIN 域 (8, 12, 13, 14 位)
GTIN_Domain = NumericString 8 ⊎ NumericString 12 ⊎ NumericString 13 ⊎ NumericString 14

-- SSCC 域 (18 位)
SSCC_Domain = { s ∈ Digit^18 | validate_checksum(s) = true }

-- GLN 域 (13 位)
GLN_Domain = { s ∈ Digit^13 | validate_checksum(s) = true }

-- EPC URI 域 (唯一标识对象实例)
EPC_Domain = SGTIN ⊎ SSCC_EPC ⊎ SGLN ⊎ GRAI_EPC ⊎ GIAI_EPC ⊎ GSRN_EPC

where:
  SGTIN = { urn:epc:id:sgtin:C.I.S | C ∈ CompanyPrefix, I ∈ ItemRef, S ∈ Serial }
  SSCC_EPC = { urn:epc:id:sscc:C.S | C ∈ CompanyPrefix, S ∈ SerialRef }
  SGLN = { urn:epc:id:sgln:C.L.E | C ∈ CompanyPrefix, L ∈ LocationRef, E ∈ Extension }
```

**定义 4.2 (语义值域)**：

```haskell
-- 值域 V 定义
V = V_Numeric ⊎ V_String ⊎ V_Date ⊎ V_Bool ⊎ V_List ⊎ V_Object ⊎ V_Error

V_Numeric = ℤ ∪ ℚ  -- 整数或有理数
V_String = Char*   -- 字符序列
V_Date = ℤ × ℤ × ℤ  -- (年, 月, 日)
V_Bool = {true, false}
V_List = V*
V_Object = Label → V  -- 记录/对象
V_Error = ErrorMessage

-- 偏序关系 (用于指称语义中的不动点)
⊑ : V × V → Bool
v ⊑ v'  iff  v = ⊥ ∨ v = v'
```

### 4.2 语义函数定义

**定义 4.3 (语义解释函数)**：

```haskell
-- 语义解释函数 [[_]] : Syntax → Environment → V

-- 数字字面量语义
[[ n ]] η = if valid_numeric(n) then n else error

-- 字符串字面量语义
[[ s ]] η = s

-- AI 元素语义
[[ (AI)D ]] η = case lookup_AI(AI) of
    Just ai_def -> if validate_data(ai_def, D)
                   then construct_value(ai_def, D)
                   else error "Invalid data for AI"
    Nothing -> error "Unknown AI"

-- GTIN 语义
[[ GTIN-14(cp, ir, cd) ]] η =
    let gtin_string = "0" ++ cp ++ ir ++ cd
        computed_cd = mod10_check(gtin_string[0..12])
    in if cd == computed_cd
       then GTIN_Val { company_prefix = cp,
                       item_reference = ir,
                       check_digit = cd,
                       level = TradeItem }
       else error "Invalid check digit"

-- SSCC 语义
[[ SSCC(ext, cp, sr, cd) ]] η =
    let sscc_string = ext ++ cp ++ sr ++ cd
        computed_cd = mod10_check(sscc_string[0..16])
    in if length(sscc_string) == 18 ∧ cd == computed_cd
       then SSCC_Val { extension = ext,
                       company_prefix = cp,
                       serial_ref = sr,
                       check_digit = cd }
       else error "Invalid SSCC"

-- EPC 语义
[[ urn:epc:id:sgtin:C.I.S ]] η =
    SGTIN_Val { company_prefix = [[C]] η,
                item_reference = [[I]] η,
                serial = [[S]] η }

-- 条码符号语义
[[ GS1-128(element*) ]] η =
    foldr concat_ai [] (map (λe. [[e]] η) element*)
  where
    concat_ai ai acc = if valid_sequence(ai, acc)
                       then ai : acc
                       else error "Invalid AI sequence"

-- EPCIS 事件语义
[[ ObjectEvent(t, tz, epcs, a, ...) ]] η =
    Event_Record {
        event_type = OBJECT_EVENT,
        event_time = [[t]] η,
        timezone = [[tz]] η,
        epc_list = map (λe. [[e]] η) epcs,
        action = interpret_action(a),
        biz_step = [[biz_step]] η,
        disposition = [[disposition]] η,
        read_point = [[read_point]] η,
        biz_location = [[biz_location]] η
    }

-- 动作语义
interpret_action(ADD) = λstate.λepcs. add_objects(state, epcs)
interpret_action(OBSERVE) = λstate.λepcs. observe_objects(state, epcs)
interpret_action(DELETE) = λstate.λepcs. remove_objects(state, epcs)
```

**定义 4.4 (辅助语义函数)**：

```haskell
-- 校验位计算语义
[[ check_digit(s) ]] =
    let digits = map char_to_int s
        n = length digits
        weights = cycle [3, 1]
        weighted_sum = sum (zipWith (*) (reverse digits) weights)
    in (10 - (weighted_sum mod 10)) mod 10

-- 验证语义
[[ validate(gtin) ]] =
    [[ gtin.check_digit ]] == [[ check_digit(gtin[0..n-2]) ]]

-- 转换语义: GTIN 到 EPC
[[ gtin_to_epc(gtin, serial) ]] =
    "urn:epc:id:sgtin:" ++ gtin.company_prefix ++ "." ++
    gtin.item_reference ++ "." ++ serial

-- 转换语义: EPC 到 GTIN
[[ epc_to_gtin(epc) ]] =
    case parse_epc(epc) of
        SGTIN(cp, ir, s) -> GTIN(cp, ir, compute_check_digit(cp ++ ir))
        _ -> error "Not a valid SGTIN"

-- 查询语义
[[ query(q, events) ]] =
    filter (λe. satisfies(q, e)) events
  where
    satisfies(SimpleQuery params, e) =
        all (λp. match_param(p, e)) params
    match_param(EventTime(start, end), e) =
        start ≤ e.event_time ≤ end
    match_param(EPCMatch(epc_pattern), e) =
        any (λepc. matches(epc_pattern, epc)) e.epc_list
    match_param(BizStep(step), e) =
        e.biz_step == step
```

### 4.3 域方程

**定义 4.5 (域方程)**：

```haskell
-- 递归域方程
-- 对象跟踪域 (包含历史)
ObjectTracking = μX. Location × Disposition × List(EventID) × (1 + X)
  -- 位置 × 状态 × 事件历史 × (终止或继续)

-- 聚合层次结构域
AggregationHierarchy = μA. Set(EPC) × (1 + A)
  -- 直接子对象 × (无父对象或父对象引用)

-- EPCIS 文档域
EPCISDocument = Header × List(EPCISEvent)
Header = Version × DateTime × Sender × (1 + Receiver)

-- 供应链跟踪域 (完整的供应链历史)
SupplyChainTrace = μT. Event × (1 + T)
  -- 事件 × (链结束或继续)

-- 事件追溯域
EventLineage = μL. EPCISEvent × Set(L)
  -- 事件 × 派生事件集合 (构成有向无环图)
```

**定义 4.6 (不动点语义)**：

```haskell
-- 最小不动点语义
fix :: (a -> a) -> a
fix f = f (fix f)

-- 状态更新语义 (最小不动点)
[[ update_state ]] = fix (λf.λstate.λevent.
    if is_terminal(event)
    then state
    else f (apply_event(state, event)) (next_event(event))
)

-- 聚合层次的不动点
descendants :: AggregationHierarchy -> Set EPC
descendants = fix (λf.λnode.
    let direct = children(node)
        indirect = concatMap f direct
    in direct ∪ indirect
)

-- 事件闭包语义
event_closure :: EPCISEvent -> SupplyChainState -> Set EPCISEvent
event_closure = fix (λf.λe.λstate.
    let direct_causes = find_causes(e, state)
        indirect_causes = concatMap (λc. f c state) direct_causes
    in {e} ∪ direct_causes ∪ indirect_causes
)
```

---

## 5. 公理语义

### 5.1 标识符唯一性公理

**公理 5.1 (GTIN 唯一性)**：

```text
∀ gtin₁, gtin₂ ∈ GTIN:
    gtin₁.identifier = gtin₂.identifier
    ↔ gtin₁ = gtin₂

-- 公司前缀唯一性
∀ cp₁, cp₂ ∈ CompanyPrefix:
    cp₁ ≠ cp₂ →
    ∀ ir₁, ir₂: GTIN(cp₁, ir₁, _) ≠ GTIN(cp₂, ir₂, _)

-- 全局唯一性保证
∀ gtin₁, gtin₂ ∈ GTIN:
    company_prefix(gtin₁) = company_prefix(gtin₂) ∧
    item_reference(gtin₁) = item_reference(gtin₂)
    → gtin₁ = gtin₂
```

**公理 5.2 (SSCC 唯一性)**：

```text
∀ sscc₁, sscc₂ ∈ SSCC:
    sscc₁.identifier = sscc₂.identifier
    ↔ sscc₁ = sscc₂

-- 序列号唯一性 (在同一公司前缀内)
∀ sscc₁, sscc₂ ∈ SSCC:
    company_prefix(sscc₁) = company_prefix(sscc₂) ∧
    serial_reference(sscc₁) = serial_reference(sscc₂)
    → sscc₁ = sscc₂

-- SSCC 不可重用性
∀ sscc ∈ SSCC, t₁, t₂ ∈ Time:
    t₁ < t₂ ∧ assigned(sscc, t₁) → ¬assigned(sscc, t₂)
```

**公理 5.3 (GLN 唯一性)**：

```text
∀ gln₁, gln₂ ∈ GLN:
    gln₁.identifier = gln₂.identifier
    ↔ gln₁ = gln₂

-- 位置标识与物理位置的一一对应
∀ gln₁, gln₂ ∈ GLN, loc₁, loc₂ ∈ PhysicalLocation:
    represents(gln₁, loc₁) ∧ represents(gln₂, loc₂) ∧
    loc₁ = loc₂ → gln₁ = gln₂
```

### 5.2 校验位正确性公理

**公理 5.4 (模 10 校验)**：

```text
-- 校验位计算正确性
∀ s ∈ Digitⁿ, n ≥ 2:
    let digits = map(int, s)
        weights = [3, 1, 3, 1, ...] (n-1 个)
        weighted_sum = Σ (digits[i] × weights[i]) for i = 0 to n-2
        check = (10 - (weighted_sum mod 10)) mod 10
    in validate_checksum(s ++ [check]) = true

-- 校验位验证完备性
∀ s ∈ Digitⁿ:
    validate_checksum(s) = true
    ↔ s[n-1] = compute_check_digit(s[0..n-2])

-- 单错误检测
∀ s ∈ Digitⁿ, i ∈ [0, n-2], d ∈ Digit, d ≠ s[i]:
    let s' = s[0..i-1] ++ [d] ++ s[i+1..n-1]
    in validate_checksum(s') = false

-- 相邻交换错误检测
∀ s ∈ Digitⁿ, i ∈ [0, n-3]:
    let s' = s[0..i-1] ++ [s[i+1]] ++ [s[i]] ++ s[i+2..n-1]
    in s[i] ≠ s[i+1] → validate_checksum(s') = false
```

**公理 5.5 (校验传播)**：

```text
-- GTIN 到 EPC 的校验传播
∀ gtin ∈ GTIN, serial ∈ Serial:
    let epc = gtin_to_epc(gtin, serial)
    in validate_checksum(gtin) = true →
       valid_epc_structure(epc) = true

-- EPC 解码正确性
∀ epc ∈ EPC:
    valid_epc_structure(epc) = true →
    ∃! gtin ∈ GTIN, serial ∈ Serial:
        epc = gtin_to_epc(gtin, serial) ∧
        validate_checksum(gtin) = true
```

### 5.3 EPCIS 事件完整性公理

**公理 5.6 (事件完整性)**：

```text
-- 对象事件完整性
∀ e ∈ ObjectEvent:
    has_event_time(e) ∧ has_action(e) ∧ has_epc_list(e)
    → event_valid(e)

-- 聚合事件完整性
∀ e ∈ AggregationEvent:
    has_event_time(e) ∧ has_action(e) ∧ has_parent_id(e) ∧
    (action(e) ≠ ADD → has_child_epcs(e))
    → event_valid(e)

-- 交易事件完整性
∀ e ∈ TransactionEvent:
    has_event_time(e) ∧ has_action(e) ∧ has_epc_list(e) ∧
    has_biz_transaction_list(e)
    → event_valid(e)

-- 转换事件完整性
∀ e ∈ TransformationEvent:
    has_event_time(e) ∧ has_transformation_id(e) ∧
    (has_input_epc_list(e) ∨ has_input_quantity_list(e)) ∧
    (has_output_epc_list(e) ∨ has_output_quantity_list(e))
    → event_valid(e)
```

**公理 5.7 (事件一致性)**：

```text
-- 动作一致性
∀ e ∈ ObjectEvent:
    action(e) = ADD → disposition(e) = active ∨ disposition(e) = unknown
    action(e) = DELETE → disposition(e) = destroyed ∨ disposition(e) = disposed

-- 聚合一致性
∀ e ∈ AggregationEvent:
    action(e) = ADD →
        ∀ child ∈ child_epcs(e): location(child) = location(parent_id(e))
    action(e) = DELETE →
        ∀ child ∈ child_epcs(e): location(child) ≠ location(parent_id(e))

-- 时间单调性
∀ e₁, e₂ ∈ EPCISEvent, o ∈ EPC:
    o ∈ epc_list(e₁) ∧ o ∈ epc_list(e₂) ∧
    event_time(e₁) < event_time(e₂)
    → state_at(e₂, o) = apply(e₂, state_at(e₁, o))
```

**公理 5.8 (因果关系)**：

```text
-- 观察因果性
∀ e₁, e₂ ∈ ObjectEvent, o ∈ EPC:
    o ∈ epc_list(e₁) ∧ o ∈ epc_list(e₂) ∧
    action(e₁) = ADD ∧ action(e₂) = OBSERVE ∧
    event_time(e₁) < event_time(e₂)
    → e₁ ⊏ e₂  (e₁ 是 e₂ 的原因)

-- 聚合因果性
∀ e₁ ∈ AggregationEvent, e₂ ∈ ObjectEvent, child ∈ EPC:
    child ∈ child_epcs(e₁) ∧ action(e₁) = ADD ∧
    child ∈ epc_list(e₂) ∧ action(e₂) = OBSERVE
    → e₁ ⊏ e₂

-- 反身性、传递性、反对称性
∀ e₁, e₂, e₃ ∈ EPCISEvent:
    e₁ ⊏ e₁  (反身性)
    e₁ ⊏ e₂ ∧ e₂ ⊏ e₃ → e₁ ⊏ e₃  (传递性)
    e₁ ⊏ e₂ ∧ e₂ ⊏ e₁ → e₁ = e₂  (反对称性)
```

### 5.4 复合公理与推理规则

**公理 5.9 (供应链跟踪完整性)**：

```text
-- 完全跟踪性
∀ o ∈ EPC, t_start, t_end ∈ Time:
    let trace = query_events(o, t_start, t_end)
    in complete_trace(trace) ↔
       first_event(trace).action = ADD ∧
       last_event(trace).action ∈ {DELETE, OBSERVE} ∧
       contiguous(trace)

-- 位置连续性
∀ o ∈ EPC, e₁, e₂ ∈ EPCISEvent:
    consecutive_events(e₁, e₂, o) →
    location(e₂, o) = next_location(e₁, o)
```

**推理规则 5.1 (校验推导)**：

```text
                    validate_checksum(s[0..n-2]) = d
                    ───────────────────────────────────── (CHECK)
                    validate_checksum(s[0..n-2] ++ [d]) = true

                    validate_checksum(s) = true
                    s = prefix ++ [check]
                    ───────────────────────────────────── (CHECK-EXTRACT)
                    check = compute_check_digit(prefix)
```

**推理规则 5.2 (事件有效性推导)**：

```text
                    has_event_time(e)    has_action(e)
                    has_epc_list(e)      validate_epcs(epc_list(e))
                    ───────────────────────────────────────────── (OBJ-VALID)
                    event_valid(e) for ObjectEvent

                    action(e) = ADD       disposition(e) = active
                    ───────────────────────────────────────────── (ADD-CONSISTENT)
                    action_consistent(e)

                    event_valid(e)        action_consistent(e)
                    time_valid(e)         epc_unique_in_event(e)
                    ───────────────────────────────────────────── (EVENT-SOUND)
                    sound_event(e)
```

**推理规则 5.3 (跟踪推导)**：

```text
                    event_valid(e₁)       event_valid(e₂)
                    o ∈ epc_list(e₁)      o ∈ epc_list(e₂)
                    event_time(e₁) < event_time(e₂)
                    no_intermediate_events(o, e₁, e₂)
                    ───────────────────────────────────────────── (CONSECUTIVE)
                    consecutive_events(e₁, e₂, o)

                    consecutive_events(e₁, e₂, o)
                    location(e₁, o) = loc₁
                    location(e₂, o) = loc₂
                    ───────────────────────────────────────────── (MOVEMENT)
                    moved(o, loc₁, loc₂, event_time(e₁), event_time(e₂))
```

---

**参考文档**：

- `01_Overview.md` - 概述
- `02_Formal_Definition.md` - 形式化定义
- `03_Standards.md` - 标准对标
- `04_Transformation.md` - 转换体系
- `05_Case_Studies.md` - 实践案例

**相关标准**：

- GS1 General Specifications v23.0
- EPCIS v1.2 / v2.0
- CBV (Core Business Vocabulary) v1.2
- TDS (Tag Data Standard) v1.13
- GENC (Geopolitical Entity Names Codes)

**创建时间**：2025-01-21
**最后更新**：2025-01-21
