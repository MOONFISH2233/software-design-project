Scripting Error

×

i

Microsoft VBScript 运行时错误
对象不支持此属性成方法:'model.Entities.AddNew'(0x800A01B6)
At line 112, character 9

确定
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