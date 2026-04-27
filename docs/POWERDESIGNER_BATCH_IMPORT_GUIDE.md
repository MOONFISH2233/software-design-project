# PowerDesigner 批量导入字段 - 自动化方案

## 🎯 三种自动导入方法

### 方法一：VBScript脚本导入（推荐）⭐⭐⭐⭐⭐

**优点**: 完全自动化，一键导入所有表和字段  
**缺点**: 需要编写脚本（已为你准备好）

#### 使用步骤：

1. **准备CSV文件**
   - 文件位置: `docs/powerdesigner_import.csv`
   - 已包含15个表的所有字段定义

2. **打开PowerDesigner并创建CDM**
   ```
   File → New Model → Conceptual Data Model
   Name: SkinHealthSystem_CDM
   ```

3. **运行导入脚本**
   ```
   Tools → Execute Commands → Edit/Run Script
   ```
   
4. **复制粘贴脚本内容**
   - 打开 `docs/powerdesigner_batch_import.vbs`
   - 全选复制所有内容
   - 粘贴到PowerDesigner的脚本编辑器
   - 点击 **Run** 按钮

5. **等待导入完成**
   - 脚本会自动创建15个实体
   - 自动添加所有字段
   - 输出窗口显示进度

6. **手动建立关系**
   - 脚本只导入表和字段
   - 关系需要手动创建（约14个关系，30分钟）

---

### 方法二：从SQL反向工程（最快）⭐⭐⭐⭐⭐

**优点**: 直接利用已有的SQL脚本，无需额外工作  
**缺点**: 需要先有完整的SQL脚本

#### 使用步骤：

1. **确保SQL脚本完整**
   - 文件: `data-server/scripts/init_mysql_week8.sql`
   - 包含15个表的完整定义

2. **在PowerDesigner中执行反向工程**
   ```
   File → Reverse Engineer → Database
   ```

3. **配置数据库连接**
   - **DBMS**: MySQL 8.0
   - **Connection profile**: 新建
     - Host: localhost（或服务器IP）
     - Port: 3306
     - Database: software_design
     - User: root
     - Password: admin

4. **选择导入方式**
   - 如果MySQL已安装并执行了SQL: 选择"Using a data source"
   - 如果只有SQL文件: 选择"Using script files"

5. **选择要导入的对象**
   - 勾选所有15个表
   - 点击 **OK**

6. **自动生成CDM/PDM**
   - PowerDesigner会自动解析SQL
   - 生成完整的ER图
   - 包含所有字段、类型、注释

7. **保存模型文件**
   ```
   File → Save As
   保存为 .cdm 和 .pdm 文件
   ```

---

### 方法三：Excel + VBA宏导入 ⭐⭐⭐⭐

**优点**: 可视化编辑，灵活调整  
**缺点**: 需要启用Excel宏

#### 使用步骤：

1. **准备Excel文件**
   - 打开 `docs/powerdesigner_import.csv`
   - 另存为 `.xlsx` 格式
   - 可以手动调整字段顺序和内容

2. **在Excel中启用宏**
   ```
   文件 → 选项 → 信任中心 → 宏设置
   选择"启用所有宏"
   ```

3. **编写VBA导出脚本**
   - 按 `Alt+F11` 打开VBA编辑器
   - 插入模块
   - 粘贴导出代码（生成PD可识别的XML格式）

4. **在PowerDesigner中导入**
   ```
   File → Import Model → XML Format
   ```

---

## 📋 推荐方案对比

| 方案 | 难度 | 速度 | 灵活性 | 推荐度 |
|------|------|------|--------|--------|
| VBScript脚本 | 低 | 快（5分钟） | 中 | ⭐⭐⭐⭐⭐ |
| SQL反向工程 | 最低 | 最快（2分钟） | 低 | ⭐⭐⭐⭐⭐ |
| Excel+VBA | 中 | 中（15分钟） | 高 | ⭐⭐⭐⭐ |

---

## 🚀 最佳实践建议

### 对于你的情况（已有SQL脚本）

**强烈推荐使用方法二：SQL反向工程**

**原因：**
1. ✅ 你已经有完整的SQL脚本（`init_mysql_week8.sql`）
2. ✅ 不需要重复输入150+个字段
3. ✅ 保证PD模型与SQL完全一致
4. ✅ 只需2-3分钟即可完成

**操作步骤简化版：**
```bash
# 1. 确保服务器上MySQL已执行SQL
ssh root@47.103.108.47
mysql -u root -padmin < /root/course-project/data-server/scripts/init_mysql_week8.sql

# 2. 本地PowerDesigner连接服务器MySQL
File → Reverse Engineer → Database
选择"Using a data source"
配置连接: 47.103.108.47:3306

# 3. 自动生成模型
全选15个表 → OK → 完成！
```

---

## 🔧 如果SQL反向工程失败

**备选方案：使用VBScript脚本**

1. **修改脚本中的CSV路径**
   ```vbscript
   csvPath = "D:\学习\软件设计\docs\powerdesigner_import.csv"
   ```
   确保路径正确

2. **运行脚本**
   ```
   Tools → Execute Commands → Edit/Run Script
   粘贴脚本 → Run
   ```

3. **检查导入结果**
   - 查看Output窗口是否有错误
   - 确认15个实体都已创建
   - 确认字段数量和类型正确

4. **手动补充关系**
   - 使用Relationship工具
   - 按照之前提供的14个关系列表连线

---

## 💡 高级技巧

### 技巧1: 批量设置数据类型映射

如果CSV中的类型不被PD识别，修改脚本中的 `ConvertDataType` 函数：

```vbscript
Function ConvertDataType(pdType)
    ' 添加更多类型映射
    Case "json"
        ConvertDataType = "Text"
    Case "decimal(10,2)"
        ConvertDataType = "Double"
End Function
```

### 技巧2: 自动添加索引

在脚本末尾添加索引创建逻辑：

```vbscript
' 为每个表添加常用索引
For Each entity In model.Entities
    If entity.Code = "skin_sensor_data" Then
        ' 添加device_id索引
        Dim idx
        Set idx = entity.Indexes.AddNew
        idx.Name = "idx_device_id"
        idx.Columns.Add entity.Attributes.GetItemAt("device_id")
    End If
Next
```

### 技巧3: 导出为图片

导入完成后，立即导出ER图：

```
File → Export Image
Format: PNG
Resolution: 300 DPI
Save to: docs/images/database_er_diagram.png
```

---

## ❓ 常见问题

### Q1: 脚本运行时提示"对象不支持此属性"？

**A:** 
- 检查PowerDesigner版本（需要16.x以上）
- 确认已创建CDM模型
- 检查CSV文件格式是否正确

### Q2: 中文注释显示乱码？

**A:**
1. CSV文件保存为UTF-8编码
2. PowerDesigner设置: Tools → Options → General → Character set: UTF-8

### Q3: 某些字段没有导入？

**A:**
- 检查CSV中该行是否有空列
- 确认字段名没有特殊字符
- 查看Output窗口的错误信息

### Q4: 如何只导入部分表？

**A:**
- 删除CSV中不需要的行
- 或在脚本中添加过滤条件：
```vbscript
If tableName <> "system_configs" Then
    ' 只导入非系统配置表
End If
```

---

## ✅ 验收检查

导入完成后，确认：

- [ ] 15个实体全部创建
- [ ] 每个实体的字段数量正确
- [ ] 主键字段标记为Primary
- [ ] 必填字段标记为Mandatory
- [ ] 所有字段有中文注释
- [ ] 数据类型映射正确
- [ ] 可以成功生成PDM
- [ ] 可以成功导出SQL

---

## 📞 快速开始命令

```powershell
# Windows PowerShell - 一键启动流程

# 1. 打开PowerDesigner
Start-Process "C:\Program Files\Sybase\PowerDesigner 16\pdshell16.exe"

# 2. 等待PD启动后，手动执行：
#    File → New Model → CDM
#    Tools → Execute Commands → Edit/Run Script
#    粘贴 powerdesigner_batch_import.vbs 的内容
#    点击 Run
```

---

**总结**: 对于你的情况，**直接使用SQL反向工程是最快的方法**，2分钟即可完成所有工作！如果遇到问题，再使用VBScript脚本作为备选方案。
