' PowerDesigner 批量导入字段脚本
' 从CSV文件读取并自动创建实体和属性

Option Explicit

Dim model
Dim entity
Dim attribute
Dim fso, file, line
Dim tableName, fieldName, fieldType, isPrimary, isMandatory, comment
Dim fields()
Dim i

' 获取当前活动模型
Set model = ActiveModel

If model Is Nothing Then
    MsgBox "请先打开或创建一个CDM模型！"
    Exit Sub
End If

' CSV文件路径（修改为你的文件路径）
Dim csvPath
csvPath = "D:\学习\软件设计\docs\powerdesigner_import.csv"

' 检查文件是否存在
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FileExists(csvPath) Then
    MsgBox "CSV文件不存在：" & csvPath
    Exit Sub
End If

' 读取CSV文件
Set file = fso.OpenTextFile(csvPath, 1) ' 1 = ForReading

' 跳过标题行
file.ReadLine

' 逐行读取
Do While Not file.AtEndOfStream
    line = file.ReadLine
    
    ' 解析CSV行（简单分割，假设没有逗号在字段内）
    fields = Split(line, ",")
    
    If UBound(fields) >= 5 Then
        tableName = Trim(fields(0))
        fieldName = Trim(fields(1))
        fieldType = Trim(fields(2))
        isPrimary = Trim(fields(3))
        isMandatory = Trim(fields(4))
        comment = Trim(fields(5))
        
        ' 查找或创建实体
        Set entity = FindOrCreateEntity(model, tableName)
        
        ' 添加属性
        Set attribute = entity.Attributes.AddNew
        
        attribute.Name = GetChineseName(fieldName)
        attribute.Code = fieldName
        attribute.DataType = ConvertDataType(fieldType)
        
        If isPrimary = "Yes" Or isPrimary = "是" Then
            attribute.Primary = True
        End If
        
        If isMandatory = "Yes" Or isMandatory = "是" Then
            attribute.Mandatory = True
        End If
        
        attribute.Comment = comment
        
        Output "已添加字段: " & tableName & "." & fieldName
    End If
Loop

file.Close

MsgBox "批量导入完成！"

' ==================== 辅助函数 ====================

Function FindOrCreateEntity(model, entityCode)
    Dim ent
    Dim found
    
    found = False
    
    ' 查找现有实体
    For Each ent In model.Entities
        If ent.Code = entityCode Then
            Set FindOrCreateEntity = ent
            found = True
            Exit Function
        End If
    Next
    
    ' 如果没找到，创建新实体
    If Not found Then
        Set ent = model.Entities.AddNew
        ent.Name = GetChineseTableName(entityCode)
        ent.Code = entityCode
        Set FindOrCreateEntity = ent
    End If
End Function

Function ConvertDataType(pdType)
    Select Case LCase(pdType)
        Case "integer", "int"
            ConvertDataType = "Integer"
        Case "bigint"
            ConvertDataType = "BigInt"
        Case "string(50)", "varchar(50)"
            ConvertDataType = "String(50)"
        Case "string(100)", "varchar(100)"
            ConvertDataType = "String(100)"
        Case "string(255)", "varchar(255)"
            ConvertDataType = "String(255)"
        Case "text"
            ConvertDataType = "Text"
        Case "date"
            ConvertDataType = "Date"
        Case "datetime", "timestamp"
            ConvertDataType = "DateTime"
        Case "float"
            ConvertDataType = "Float"
        Case "double"
            ConvertDataType = "Double"
        Case "boolean", "tinyint(1)"
            ConvertDataType = "Boolean"
        Case Else
            ConvertDataType = "String(100)" ' 默认
    End Select
End Function

Function GetChineseName(code)
    ' 简单的字段名映射（可以根据需要扩展）
    Select Case LCase(code)
        Case "id"
            GetChineseName = "ID"
        Case "user_id"
            GetChineseName = "用户ID"
        Case "username"
            GetChineseName = "用户名"
        Case "password_hash"
            GetChineseName = "密码哈希"
        Case "nickname"
            GetChineseName = "昵称"
        Case "phone"
            GetChineseName = "手机号"
        Case "email"
            GetChineseName = "邮箱"
        Case "avatar_url"
            GetChineseName = "头像URL"
        Case "role"
            GetChineseName = "角色"
        Case "status"
            GetChineseName = "状态"
        Case "created_at"
            GetChineseName = "创建时间"
        Case "updated_at"
            GetChineseName = "更新时间"
        Case "device_id"
            GetChineseName = "设备ID"
        Case "device_type"
            GetChineseName = "设备类型"
        Case "firmware_version"
            GetChineseName = "固件版本"
        Case "battery_level"
            GetChineseName = "电池电量"
        Case "signal_strength"
            GetChineseName = "信号强度"
        Case "last_heartbeat"
            GetChineseName = "最后心跳时间"
        Case "moisture"
            GetChineseName = "水分含量"
        Case "oiliness"
            GetChineseName = "油脂度"
        Case "temperature"
            GetChineseName = "温度"
        Case "humidity"
            GetChineseName = "湿度"
        Case "pm25"
            GetChineseName = "PM2.5"
        Case "co2"
            GetChineseName = "CO2浓度"
        Case "sensor_time"
            GetChineseName = "采集时间"
        Case Else
            GetChineseName = code ' 默认使用英文名
    End Select
End Function

Function GetChineseTableName(code)
    Select Case LCase(code)
        Case "users"
            GetChineseTableName = "用户"
        Case "user_profiles"
            GetChineseTableName = "用户资料"
        Case "devices"
            GetChineseTableName = "设备"
        Case "device_bindings"
            GetChineseTableName = "设备绑定"
        Case "skin_sensor_data"
            GetChineseTableName = "皮肤传感器数据"
        Case "environment_sensor_data"
            GetChineseTableName = "环境传感器数据"
        Case "daily_statistics"
            GetChineseTableName = "每日统计数据"
        Case "health_reports"
            GetChineseTableName = "健康报告"
        Case "community_posts"
            GetChineseTableName = "社区帖子"
        Case "post_comments"
            GetChineseTableName = "帖子评论"
        Case "notifications"
            GetChineseTableName = "消息通知"
        Case "user_points"
            GetChineseTableName = "用户积分"
        Case "skincare_products"
            GetChineseTableName = "护肤产品"
        Case "user_skincare_records"
            GetChineseTableName = "护肤记录"
        Case "system_configs"
            GetChineseTableName = "系统配置"
        Case Else
            GetChineseTableName = code
    End Select
End Function
